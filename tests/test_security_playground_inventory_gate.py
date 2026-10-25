"""Synthetic Security Playground gate tests. Never access live infrastructure."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.security_playground_inventory_gate import SCHEMA, evaluate

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "security_playground_inventory_gate.py"


def fixture() -> dict:
    return {
        "schema": SCHEMA,
        "mode": "fixture",
        "source_revision": "a" * 40,
        "isolation": {
            "dedicated_isolation_domain": True,
            "deny_production_network": True,
            "production_credentials_absent": True,
            "production_state_readonly": True,
            "ephemeral_storage": True,
            "evidence_ref": "fixture://synthetic-isolation-claim",
        },
        "protected_state_mutations": 0,
        "assets": [
            {"id": "fixture-php", "kind": "php_runtime",
             "status": "not_present", "evidence_ref": "fixture://php-inventory"},
            {"id": "fixture-dependency", "kind": "dependency",
             "status": "patched", "evidence_ref": "fixture://lockfile"},
        ],
        "receipt_refs": ["fixture://test-run"],
    }


class PlaygroundGateTests(unittest.TestCase):
    def test_clean_fixture_is_drill_pass_not_production(self) -> None:
        result = evaluate(fixture())
        self.assertEqual(result["verdict"], "DRILL_PASS")
        self.assertFalse(result["runtime_verified"])
        self.assertFalse(result["production_authority"])

    def test_unknown_php_exposure_holds(self) -> None:
        sample = fixture()
        sample["assets"][0]["status"] = "unknown"
        self.assertEqual(evaluate(sample)["verdict"], "HOLD")

    def test_vulnerable_dependency_blocks(self) -> None:
        sample = fixture()
        sample["assets"][1]["status"] = "vulnerable"
        self.assertEqual(evaluate(sample)["verdict"], "BLOCK")

    def test_isolation_failure_blocks(self) -> None:
        sample = fixture()
        sample["isolation"]["deny_production_network"] = False
        self.assertEqual(evaluate(sample)["verdict"], "BLOCK")

    def test_unverified_isolation_holds(self) -> None:
        sample = fixture()
        del sample["isolation"]["deny_production_network"]
        self.assertEqual(evaluate(sample)["verdict"], "HOLD")

    def test_protected_state_mutation_blocks(self) -> None:
        sample = fixture()
        sample["protected_state_mutations"] = 1
        self.assertEqual(evaluate(sample)["verdict"], "BLOCK")

    def test_missing_php_inventory_holds(self) -> None:
        sample = fixture()
        sample["assets"] = sample["assets"][1:]
        self.assertEqual(evaluate(sample)["verdict"], "HOLD")

    def test_real_environment_never_graduates_from_claims(self) -> None:
        for mode in ("cloud", "local"):
            sample = fixture()
            sample["mode"] = mode
            result = evaluate(sample)
            self.assertEqual(result["verdict"], "HOLD")
            self.assertFalse(result["runtime_verified"])

    def test_invalid_receipts_and_revision_hold(self) -> None:
        sample = fixture()
        sample["receipt_refs"] = []
        sample["source_revision"] = "HEAD"
        self.assertEqual(evaluate(sample)["verdict"], "HOLD")

    def test_malformed_fields_fail_closed_without_exception(self) -> None:
        sample = fixture()
        sample["mode"] = ["fixture"]
        sample["assets"][0]["status"] = []
        sample["assets"][1]["kind"] = {}
        self.assertEqual(evaluate(sample)["verdict"], "HOLD")

    def test_cli_exit_codes(self) -> None:
        for status, expected in (("patched", 0), ("unknown", 2), ("vulnerable", 3)):
            sample = fixture()
            sample["assets"][1]["status"] = status
            with tempfile.TemporaryDirectory() as tempdir:
                path = Path(tempdir) / "evidence.json"
                path.write_text(json.dumps(sample), encoding="utf-8")
                run = subprocess.run(
                    [sys.executable, str(GATE), "--input", str(path)],
                    capture_output=True, text=True, check=False,
                )
                self.assertEqual(run.returncode, expected, run.stderr)
                self.assertFalse(json.loads(run.stdout)["runtime_verified"])

    def test_cli_malformed_json_exits_4_and_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "evidence.json"
            path.write_text('{"bad": json,,}', encoding="utf-8")
            run = subprocess.run(
                [sys.executable, str(GATE), "--input", str(path)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(run.returncode, 4, run.stderr)
            out = json.loads(run.stdout)
            self.assertEqual(out["verdict"], "BLOCK")
            self.assertFalse(out["runtime_verified"])
            self.assertFalse(out["production_authority"])
            self.assertEqual(run.stderr.strip(), "")


if __name__ == "__main__":
    unittest.main()
