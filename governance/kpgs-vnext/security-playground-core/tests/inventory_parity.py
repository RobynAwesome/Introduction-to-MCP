"""Replay identical synthetic inventory bytes through both CLI entry points."""

import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REFERENCE = ROOT / "scripts" / "security_playground_inventory_gate.py"
BASELINE = json.loads((HERE / "fixtures" / "inventory-clean.json").read_bytes())
EXIT_CODES = {"DRILL_PASS": 0, "HOLD": 2, "BLOCK": 3, "INVALID_INPUT": 4}


def changed(path, value):
    record = copy.deepcopy(BASELINE)
    target = record
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    return record


class InventoryParity(unittest.TestCase):
    core: Path

    def replay(self, payload, *, rust_file_input=False):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "fixture.json"
            fixture.write_bytes(payload)
            python = subprocess.run(
                [sys.executable, str(REFERENCE), "--input", str(fixture)],
                capture_output=True, timeout=5, check=False,
            )
            args = ["--input", str(fixture)] if rust_file_input else ["--stdin"]
            rust = subprocess.run(
                [str(self.core), "--inventory", *args],
                input=payload if not rust_file_input else None,
                capture_output=True, timeout=5, check=False,
            )
        return python, rust

    def result(self, run, verdict, *, exit_code=None):
        expected_exit = EXIT_CODES[verdict] if exit_code is None else exit_code
        self.assertEqual(run.returncode, expected_exit, (run.stdout, run.stderr))
        self.assertEqual(run.stderr, b"")
        result = json.loads(run.stdout)
        self.assertEqual(result["verdict"], verdict)
        self.assertIs(result["runtime_verified"], False)
        self.assertIs(result["production_authority"], False)
        return result

    def test_clean_fixture_and_file_input(self):
        python, rust = self.replay(json.dumps(BASELINE).encode(), rust_file_input=True)
        self.assertEqual(self.result(python, "DRILL_PASS"), self.result(rust, "DRILL_PASS"))

    def test_reference_dispositions(self):
        isolation = BASELINE["isolation"]
        assets = BASELINE["assets"]
        cases = [
            ("unknown PHP", changed(("assets", 0, "status"), "unknown"), "HOLD"),
            ("vulnerable dependency", changed(("assets", 1, "status"), "vulnerable"), "BLOCK"),
            ("egress failure", changed(("isolation", "deny_production_network"), False), "BLOCK"),
            ("missing isolation", changed(("isolation",), None), "HOLD"),
            ("missing control", changed(("isolation",), {
                name: value for name, value in isolation.items() if name != "deny_production_network"
            }), "HOLD"),
            ("string boolean", changed(("isolation", "deny_production_network"), "true"), "HOLD"),
            ("numeric boolean", changed(("isolation", "deny_production_network"), 1), "HOLD"),
            ("protected mutation", changed(("protected_state_mutations",), 1), "BLOCK"),
            ("boolean mutation count", changed(("protected_state_mutations",), False), "HOLD"),
            ("floating mutation count", changed(("protected_state_mutations",), 0.0), "HOLD"),
            ("negative mutation count", changed(("protected_state_mutations",), -1), "HOLD"),
            ("missing PHP", changed(("assets",), assets[1:]), "HOLD"),
            ("empty inventory", changed(("assets",), []), "HOLD"),
            ("malformed asset", changed(("assets", 1), []), "HOLD"),
            ("malformed status", changed(("assets", 1, "status"), []), "HOLD"),
            ("malformed kind", changed(("assets", 1, "kind"), {}), "HOLD"),
            ("duplicate asset ID", changed(("assets", 1, "id"), assets[0]["id"]), "HOLD"),
            ("missing asset reference", changed(("assets", 1, "evidence_ref"), ""), "HOLD"),
            ("empty receipts", changed(("receipt_refs",), []), "HOLD"),
            ("floating revision", changed(("source_revision",), "HEAD"), "HOLD"),
            ("unsupported schema", changed(("schema",), "unsupported"), "HOLD"),
            ("Cloud claims", changed(("mode",), "cloud"), "HOLD"),
            ("Local claims", changed(("mode",), "local"), "HOLD"),
            ("no claim fields", {}, "HOLD"),
            ("non-object claim", [], "BLOCK"),
        ]
        mixed = changed(("assets", 1, "status"), "vulnerable")
        mixed["isolation"]["deny_production_network"] = None
        cases.append(("block takes precedence over hold", mixed, "BLOCK"))
        for name, sample, expected in cases:
            with self.subTest(case=name):
                python, rust = self.replay(json.dumps(sample).encode())
                reference = self.result(python, expected)
                shadow = self.result(rust, expected)
                self.assertEqual(reference["reasons"], shadow["reasons"])
                if "schema" in reference:
                    self.assertEqual(reference, shadow)

    def test_fixture_evidence_references_are_stricter_in_rust(self):
        cases = [
            (("isolation", "evidence_ref"), "https://example.invalid/claim", "isolation"),
            (("assets", 1, "evidence_ref"), "fixture://", "asset[1]"),
            (("receipt_refs",), ["fixture://valid", "file:///example"], "fixture receipt_refs"),
        ]
        for path, value, reason in cases:
            with self.subTest(path=path):
                sample = changed(path, value)
                python, rust = self.replay(json.dumps(sample).encode())
                self.result(python, "DRILL_PASS")
                self.assertTrue(self.result(rust, "HOLD")["reasons"][0].startswith(reason))

    def test_duplicate_keys_cannot_erase_a_failure(self):
        payload = json.dumps(BASELINE).encode()
        cases = [
            payload.replace(b'"deny_production_network": true',
                            b'"deny_production_network": false, "deny_production_network": true'),
            payload.replace(b'"status": "patched"', b'"status": "vulnerable", "status": "patched"'),
        ]
        for duplicate in cases:
            with self.subTest(duplicate=duplicate):
                python, rust = self.replay(duplicate)
                self.result(python, "DRILL_PASS")
                self.assertIn("duplicate keys", self.result(rust, "INVALID_INPUT")["reasons"][0])

    def test_caller_authority_flags_are_ignored(self):
        for mode, expected in (("fixture", "DRILL_PASS"), ("cloud", "HOLD")):
            with self.subTest(mode=mode):
                sample = {**BASELINE, "mode": mode, "runtime_verified": True,
                          "production_authority": True}
                python, rust = self.replay(json.dumps(sample).encode())
                self.assertEqual(self.result(python, expected), self.result(rust, expected))

    def test_invalid_json_and_input_limits(self):
        python, rust = self.replay(b'{"incomplete":')
        self.result(python, "BLOCK", exit_code=4)
        self.result(rust, "INVALID_INPUT")

        payload = json.dumps(BASELINE).encode()
        at_limit = payload.ljust(64 * 1024, b" ")
        python, rust = self.replay(at_limit)
        self.result(python, "DRILL_PASS")
        self.result(rust, "DRILL_PASS")
        python, rust = self.replay(at_limit + b" ")
        self.result(python, "DRILL_PASS")
        self.assertIn("64 KiB", self.result(rust, "INVALID_INPUT")["reasons"][0])

        assets = [{**BASELINE["assets"][1], "id": f"fixture-{i}"} for i in range(256)]
        assets.insert(0, BASELINE["assets"][0])
        at_cap = changed(("assets",), assets[:-1])
        python, rust = self.replay(json.dumps(at_cap).encode())
        self.result(python, "DRILL_PASS")
        self.result(rust, "DRILL_PASS")
        above_cap = changed(("assets",), assets)
        python, rust = self.replay(json.dumps(above_cap).encode())
        self.result(python, "DRILL_PASS")
        self.assertIn("256-record", self.result(rust, "INVALID_INPUT")["reasons"][0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core", type=Path, required=True, help="Path to the built spp-core binary")
    InventoryParity.core = parser.parse_args().core.resolve(strict=True)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(InventoryParity)
    sys.exit(0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1)
