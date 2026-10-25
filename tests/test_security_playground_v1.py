"""Synthetic Security Playground V1 gate tests with Adversarial Extensions.

Validates all 10 core scenarios plus 6 founder-mandated adversarial tests:
Core Scenarios:
1. PHP absent
2. PHP runtime present without PHP source files
3. PHP source present without PHP runtime
4. PHP inside an isolated container (4a: vulnerable PHP -> BLOCK; 4b: unisolated -> BLOCK; 4c: patched & isolated -> DRILL_PASS)
5. Missing asset inventory
6. Vulnerable dependency
7. Failed isolation control
8. Attempted protected-state mutation
9. Fabricated or unverifiable receipt
10. Attempted promotion of Playground results to production authority

Adversarial Verification Suite:
11. Forged or unauthenticated receipt (SHA-256 alone without authentication envelope)
12. Fabricated git source revision
13. False negative asset inventory (claiming absent without discovery method)
14. Cross-domain authority spoofing (claiming founder / CA authority from playground)
15. Compromised or mutable evidence sink
16. False teacher acknowledgement without detached authenticated review packet
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent if CURRENT_DIR.name == "tests" else CURRENT_DIR

# Add current dir, repo root, and scripts dir to path
sys.path.insert(0, str(CURRENT_DIR))
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

try:
    from scripts.security_playground_v1 import (
        SCHEMA_V1,
        SCHEMA_LEGACY,
        evaluate_playground,
    )
except ImportError:
    from security_playground_v1 import (
        SCHEMA_V1,
        SCHEMA_LEGACY,
        evaluate_playground,
    )

GATE = REPO_ROOT / "scripts" / "security_playground_v1.py"
if not GATE.exists():
    GATE = CURRENT_DIR / "security_playground_v1.py"


def base_fixture() -> dict:
    return {
        "schema": SCHEMA_V1,
        "mode": "fixture",
        "source_revision": "a" * 40,
        "execution_identity": {
            "role": "playground_isolated_runner",
            "is_production_authority": False,
            "is_privileged": False,
            "execution_id": "exec-synthetic-001",
        },
        "isolation": {
            "dedicated_isolation_domain": True,
            "deny_production_network": True,
            "production_credentials_absent": True,
            "production_state_readonly": True,
            "ephemeral_storage": True,
            "resource_ceilings_enforced": True,
            "kill_switch_active": True,
            "tamper_evident_sink": True,
            "evidence_ref": "fixture://synthetic-isolation-claim",
        },
        "evidence_sink": {
            "sink_id": "sink-ephemeral-forensic-01",
            "tamper_evident": True,
            "mutable_storage": False,
            "authenticated": True,
            "compromised": False,
        },
        "resource_ceilings": {
            "cpu_cores": 1.0,
            "memory_mb": 1024,
            "timeout_sec": 120,
        },
        "kill_switch": {
            "triggered": False,
        },
        "protected_state_mutations": 0,
        "protected_state_targets_attempted": [],
        "assets": [
            {
                "id": "asset-php-runtime",
                "kind": "php_runtime",
                "status": "not_present",
                "discovery_method": "filesystem_and_path_exhaustion_scan",
                "source_files_present": False,
                "evidence_ref": "fixture://php-inventory-audit",
            },
            {
                "id": "asset-dep-simple-git",
                "kind": "dependency",
                "status": "patched",
                "evidence_ref": "fixture://lockfile-verified",
            },
        ],
        "receipt_refs": ["fixture://authenticated-test-receipt-v1"],
        "promote_to_production": False,
        "production_authority_claimed": False,
    }


class SecurityPlaygroundV1Tests(unittest.TestCase):

    def assert_disposition(self, sample, expected):
        result = evaluate_playground(sample)
        self.assertEqual(result["verdict"], expected, result)
        self.assertIs(result["runtime_verified"], False)
        self.assertIs(result["production_authority"], False)

    def test_copilot_resource_constraints(self):
        for ceilings in (None, [], {}, {"cpu_cores": -1, "memory_mb": None, "timeout_sec": 0}):
            with self.subTest(ceilings=ceilings):
                sample = base_fixture()
                sample["resource_ceilings"] = ceilings
                self.assert_disposition(sample, "HOLD")
        for field in ("cpu_cores", "memory_mb", "timeout_sec"):
            for value in (True, "1", 0, -1, float("nan"), float("inf")):
                with self.subTest(field=field, value=value):
                    sample = base_fixture()
                    sample["resource_ceilings"][field] = value
                    self.assert_disposition(sample, "HOLD")
            sample = base_fixture()
            sample["resource_ceilings"][field] = 10 ** 1000
            self.assert_disposition(sample, "BLOCK")

    def test_copilot_privilege_flags_require_explicit_false(self):
        for flag in ("is_privileged", "is_production_authority"):
            for value in (None, "false", 0, [], True):
                with self.subTest(flag=flag, value=value):
                    sample = base_fixture()
                    sample["execution_identity"][flag] = value
                    self.assert_disposition(sample, "BLOCK" if value is True else "HOLD")
            sample = base_fixture()
            del sample["execution_identity"][flag]
            self.assert_disposition(sample, "HOLD")

    def test_copilot_caller_cannot_grant_privileged_authority(self):
        for authority in ("founder", "rtc_founder", "ca_codex_forge", "teacher_cassey"):
            sample = base_fixture()
            sample.update(claimed_authority=authority, caller_domain="canonical_governance")
            self.assert_disposition(sample, "BLOCK")

    def test_copilot_sink_requires_all_boolean_assertions(self):
        for sink in (None, [], {}):
            sample = base_fixture()
            sample["evidence_sink"] = sink
            self.assert_disposition(sample, "HOLD")
        for flag, expected in (("tamper_evident", True), ("authenticated", True),
                               ("compromised", False), ("mutable_storage", False)):
            for value in (None, "false", 0, not expected):
                with self.subTest(flag=flag, value=value):
                    sample = base_fixture()
                    sample["evidence_sink"][flag] = value
                    self.assert_disposition(sample, "BLOCK" if type(value) is bool else "HOLD")

    def test_copilot_receipts_are_explicitly_synthetic(self):
        for ref in ("renamed-receipt", "sha256:abc123", "https://example.invalid/receipt"):
            sample = base_fixture()
            sample["receipt_refs"] = [ref]
            self.assert_disposition(sample, "HOLD")
        sample = base_fixture()
        sample["receipt_refs"] = ["fixture://arbitrary-synthetic-receipt"]
        self.assert_disposition(sample, "DRILL_PASS")

    def test_copilot_nonempty_teacher_signature_is_unverified(self):
        sample = base_fixture()
        sample.update(teacher_ack_claimed=True, teacher_review_packet={"teacher_signature": "anything"})
        self.assert_disposition(sample, "HOLD")

    def test_copilot_standalone_php_checks_version(self):
        for version, verdict in (("8.2.14", "BLOCK"), ("8.2.35", "DRILL_PASS"),
                                  (None, "HOLD"), (123, "HOLD"), ("99.0.0", "HOLD"),
                                  ("8.2.35-unverified-backport", "HOLD")):
            sample = base_fixture()
            sample["assets"][0].update(status="patched", source_files_present=True, php_version=version)
            self.assert_disposition(sample, verdict)

    def test_copilot_container_requires_isolation_and_version(self):
        for isolation in (None, "true", 1, False, True):
            for version in (None, 123, [], "8.4.27"):
                with self.subTest(isolation=isolation, version=version):
                    sample = base_fixture()
                    sample["assets"].append(dict(id="php-container", kind="container", status="patched",
                        contains_php=True, container_isolated=isolation, php_version=version,
                        evidence_ref="fixture://container"))
                    verdict = "BLOCK" if isolation is False else (
                        "DRILL_PASS" if isolation is True and version == "8.4.27" else "HOLD")
                    self.assert_disposition(sample, verdict)

    def test_copilot_every_outbound_crossing_requires_boolean_admission(self):
        for target in ("swfus", "blackmask", "telemetry", "unknown", "production"):
            for admitted in (False, None, "true", 1, True):
                with self.subTest(target=target, admitted=admitted):
                    sample = base_fixture()
                    sample["oz_boundary_crossing"] = dict(source="playground", target=target,
                                                          zero_trust_admitted=admitted)
                    self.assert_disposition(sample, "DRILL_PASS" if admitted is True else "BLOCK")
        sample = base_fixture()
        sample["oz_boundary_crossing"] = dict(source="playground", target=[], zero_trust_admitted=True)
        self.assert_disposition(sample, "HOLD")

    def test_copilot_malformed_fields_never_raise_for_direct_callers(self):
        for field in ("schema", "claimed_authority", "mode", "source_revision"):
            for value in ([], {}, 42, None):
                with self.subTest(field=field, value=value):
                    sample = base_fixture()
                    sample[field] = value
                    result = evaluate_playground(sample)
                    self.assertIn(result["verdict"], ("HOLD", "BLOCK"))
        for value in ([], {}, 42, None):
            sample = base_fixture()
            sample["assets"][0]["status"] = value
            self.assert_disposition(sample, "HOLD")

    def test_cli_invalid_and_malformed_input_remain_bounded(self):
        for raw in ("{broken", "[]", json.dumps(dict(base_fixture(), schema=[]))):
            proc = subprocess.run([sys.executable, str(GATE)], input=raw, text=True, capture_output=True)
            self.assertIn(proc.returncode, (2, 4))
            self.assertNotIn("Traceback", proc.stderr)
            self.assertIs(json.loads(proc.stdout)["production_authority"], False)

    # Scenario 1: PHP absent
    def test_scenario_01_php_absent(self) -> None:
        sample = base_fixture()
        result = evaluate_playground(sample)
        self.assertEqual(result["verdict"], "DRILL_PASS")
        self.assertEqual(result["exit_code"], 0)
        self.assertFalse(result["runtime_verified"])
        self.assertFalse(result["production_authority"])

    # Scenario 2: PHP runtime present without PHP source files
    def test_scenario_02_php_runtime_present_without_source(self) -> None:
        sample = base_fixture()
        sample["assets"][0]["status"] = "patched"
        sample["assets"][0]["source_files_present"] = False
        result = evaluate_playground(sample)
        self.assertEqual(result["verdict"], "HOLD")
        self.assertEqual(result["exit_code"], 2)
        self.assertTrue(any("unnecessary/rogue runtime" in r for r in result["reasons"]))

    # Scenario 3: PHP source present without PHP runtime
    def test_scenario_03_php_source_present_without_runtime(self) -> None:
        sample = base_fixture()
        sample["assets"][0]["status"] = "not_present"
        sample["assets"][0]["source_files_present"] = True
        result = evaluate_playground(sample)
        self.assertEqual(result["verdict"], "HOLD")
        self.assertEqual(result["exit_code"], 2)
        self.assertTrue(any("dormant source risk" in r for r in result["reasons"]))

    # Scenario 4: PHP inside an isolated container
    def test_scenario_04a_php_in_container_vulnerable_version(self) -> None:
        sample = base_fixture()
        sample["assets"].append({
            "id": "container-legacy-php",
            "kind": "container",
            "contains_php": True,
            "container_isolated": True,
            "php_version": "8.2.14",  # < 8.2.35, vulnerable to PHP2Shell
            "status": "vulnerable",
            "vulnerability_id": "CVE-2026-109618",
            "evidence_ref": "fixture://container-scan",
        })
        result = evaluate_playground(sample)
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertEqual(result["exit_code"], 3)
        self.assertTrue(any("CVE-2026-109618" in r for r in result["reasons"]))

    def test_scenario_04b_php_in_container_unisolated_boundary(self) -> None:
        sample = base_fixture()
        sample["assets"].append({
            "id": "container-unisolated-php",
            "kind": "container",
            "contains_php": True,
            "container_isolated": False,
            "php_version": "8.4.27",  # patched version but boundary failed
            "status": "patched",
            "evidence_ref": "fixture://container-scan",
        })
        result = evaluate_playground(sample)
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertEqual(result["exit_code"], 3)
        self.assertTrue(any("lacks verified boundary isolation" in r for r in result["reasons"]))

    def test_scenario_04c_php_in_container_patched_and_isolated(self) -> None:
        sample = base_fixture()
        sample["assets"].append({
            "id": "container-secure-php",
            "kind": "container",
            "contains_php": True,
            "container_isolated": True,
            "php_version": "8.4.27",  # patched version
            "status": "patched",
            "evidence_ref": "fixture://container-scan",
        })
        result = evaluate_playground(sample)
        self.assertEqual(result["verdict"], "DRILL_PASS")
        self.assertEqual(result["exit_code"], 0)

    # Scenario 5: Missing asset inventory
    def test_scenario_05_missing_asset_inventory(self) -> None:
        sample = base_fixture()
        sample["assets"] = []
        result = evaluate_playground(sample)
        self.assertEqual(result["verdict"], "HOLD")
        self.assertEqual(result["exit_code"], 2)
        self.assertTrue(any("asset inventory is empty or missing" in r for r in result["reasons"]))

    # Scenario 6: Vulnerable dependency
    def test_scenario_06_vulnerable_dependency(self) -> None:
        sample = base_fixture()
        sample["assets"][1]["status"] = "vulnerable"
        sample["assets"][1]["vulnerability_id"] = "CVE-2026-102829"
        result = evaluate_playground(sample)
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertEqual(result["exit_code"], 3)
        self.assertTrue(any("has vulnerable status" in r for r in result["reasons"]))

    # Scenario 7: Failed isolation control
    def test_scenario_07_failed_isolation_control(self) -> None:
        sample = base_fixture()
        sample["isolation"]["deny_production_network"] = False
        result = evaluate_playground(sample)
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertEqual(result["exit_code"], 3)
        self.assertTrue(any("isolation control explicitly failed" in r for r in result["reasons"]))

    # Scenario 8: Attempted protected-state mutation
    def test_scenario_08_attempted_protected_state_mutation(self) -> None:
        sample = base_fixture()
        sample["protected_state_mutations"] = 1
        sample["protected_state_targets_attempted"] = ["SELF.md"]
        result = evaluate_playground(sample)
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertEqual(result["exit_code"], 3)
        self.assertTrue(any("attempted protected-state mutation detected" in r for r in result["reasons"]))

    # Scenario 9: Fabricated or unverifiable receipt
    def test_scenario_09_fabricated_or_unverifiable_receipt(self) -> None:
        sample = base_fixture()
        sample["receipt_refs"] = ["fixture://fabricated-receipt-unverifiable"]
        result = evaluate_playground(sample)
        self.assertEqual(result["verdict"], "HOLD")
        self.assertEqual(result["exit_code"], 2)
        self.assertTrue(any("unverifiable or fabricated receipt" in r for r in result["reasons"]))

    # Scenario 10: Attempted promotion of Playground results to production authority
    def test_scenario_10_attempted_production_promotion(self) -> None:
        sample = base_fixture()
        sample["promote_to_production"] = True
        result = evaluate_playground(sample)
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertEqual(result["exit_code"], 3)
        self.assertTrue(any("attempted self-promotion" in r for r in result["reasons"]))

    # --- FOUNDER-MANDATED ADVERSARIAL SUITE ---

    # Adversarial Test 1: Forged or raw unauthenticated receipt (SHA-256 checksum alone)
    def test_adversarial_01_forged_or_raw_sha256_receipt(self) -> None:
        sample = base_fixture()
        sample["receipt_refs"] = ["fixture://raw_sha256_only_e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"]
        result = evaluate_playground(sample)
        self.assertEqual(result["verdict"], "HOLD")
        self.assertEqual(result["exit_code"], 2)
        self.assertTrue(any("lacks authentication envelope" in r for r in result["reasons"]))

    # Adversarial Test 2: Fabricated git source revision
    def test_adversarial_02_fabricated_revision(self) -> None:
        sample = base_fixture()
        sample["source_revision"] = "0" * 40
        result = evaluate_playground(sample)
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertEqual(result["exit_code"], 3)
        self.assertTrue(any("fabricated placeholder git revision" in r for r in result["reasons"]))

    # Adversarial Test 3: False negative asset inventory
    def test_adversarial_03_false_negative_asset_inventory(self) -> None:
        sample = base_fixture()
        sample["assets"][0]["discovery_method"] = "unverified_assumption"
        result = evaluate_playground(sample)
        self.assertEqual(result["verdict"], "HOLD")
        self.assertEqual(result["exit_code"], 2)
        self.assertTrue(any("unsupported negative claim" in r for r in result["reasons"]))

    # Adversarial Test 4: Cross-domain authority spoofing
    def test_adversarial_04_cross_domain_authority_spoofing(self) -> None:
        sample = base_fixture()
        sample["claimed_authority"] = "rtc_founder"
        sample["caller_domain"] = "playground"
        result = evaluate_playground(sample)
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertEqual(result["exit_code"], 3)
        self.assertTrue(any("cross-domain authority spoofing detected" in r for r in result["reasons"]))

    # Adversarial Test 5: Compromised or mutable evidence sink
    def test_adversarial_05_compromised_evidence_sink(self) -> None:
        sample = base_fixture()
        sample["evidence_sink"]["compromised"] = True
        result = evaluate_playground(sample)
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertEqual(result["exit_code"], 3)
        self.assertTrue(any("evidence sink is marked compromised" in r for r in result["reasons"]))

    def test_adversarial_05b_mutable_evidence_sink(self) -> None:
        sample = base_fixture()
        sample["evidence_sink"]["mutable_storage"] = True
        result = evaluate_playground(sample)
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertEqual(result["exit_code"], 3)
        self.assertTrue(any("permits mutable overwrites" in r for r in result["reasons"]))

    # Adversarial Test 6: False teacher acknowledgement
    def test_adversarial_06_false_teacher_acknowledgement(self) -> None:
        sample = base_fixture()
        sample["teacher_ack_claimed"] = True
        sample["teacher_review_packet"] = None
        result = evaluate_playground(sample)
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertEqual(result["exit_code"], 3)
        self.assertTrue(any("false teacher acknowledgement" in r for r in result["reasons"]))


if __name__ == "__main__":
    unittest.main()
