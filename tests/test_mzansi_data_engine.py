"""Deterministic contract tests for the Mzansi Data Engine foundation (#103 PR2)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MZANSI = ROOT / "governance" / "kpgs-vnext" / "mzansi-language"


def load_engine():
    spec = importlib.util.spec_from_file_location("mzansi_data_engine_under_test", MZANSI / "data_engine.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


engine = load_engine()


class FixedClock:
    def __init__(self) -> None:
        self.moment = datetime(2026, 9, 30, 0, 0, 0, tzinfo=timezone.utc)

    def __call__(self) -> datetime:
        self.moment += timedelta(seconds=1)
        return self.moment


def fixture_records() -> list[dict]:
    return engine.load_fixture_records(MZANSI / "fixtures" / "linguistic-records.synthetic.json")


def fixture_by_id(record_id: str) -> dict:
    for record in fixture_records():
        if record["record_id"] == record_id:
            return record
    raise KeyError(record_id)


def human_record(record_id: str = "test-human-0001") -> dict:
    """A non-synthetic record used only to exercise the admissibility computation."""
    record = fixture_by_id("fx-nso-0002-human-recorded")
    record["record_id"] = record_id
    record["evidence"]["synthetic"] = False
    record["evidence"]["provenance_uri"] = "fixture://test/human/0001"
    return record


class StoreCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.ledger = Path(self._tmp.name) / "ledger.jsonl"
        self.store = engine.LinguisticRecordStore(self.ledger, clock=FixedClock())

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def admit_all(self) -> None:
        for record in fixture_records():
            self.assertEqual(self.store.admit(record, actor="test").outcome, "admitted")


class GateAndSchemaTests(unittest.TestCase):
    def test_dependency_free_gate_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(MZANSI / "validate.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("KPGS-MZANSI-DATA-ENGINE PASS", result.stdout)

    def test_synthetic_fixtures_validate(self) -> None:
        validator = engine.record_validator()
        for record in fixture_records():
            self.assertEqual(validator.errors(record), [], record["record_id"])

    def test_invalid_fixtures_fail_for_the_declared_reason(self) -> None:
        validator = engine.record_validator()
        cases = json.loads((MZANSI / "fixtures" / "linguistic-records.invalid.json").read_text(encoding="utf-8"))["cases"]
        self.assertGreaterEqual(len(cases), 6)
        for case in cases:
            errors = validator.errors(case["record"])
            self.assertTrue(errors, case["case_id"])
            self.assertTrue(
                any(case["expected_error_contains"] in e for e in errors),
                f"{case['case_id']}: {errors}",
            )

    def test_validator_refuses_unsupported_keywords_instead_of_ignoring_them(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "weird.schema.json"
            path.write_text(json.dumps({"type": "object", "oneOf": [{"type": "object"}]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                engine.SchemaValidator(path)

    def test_validator_distinguishes_bool_from_integer(self) -> None:
        validator = engine.record_validator()
        record = fixture_by_id("fx-nso-0003-ai-generated-codeswitch")
        record["code_switch"]["segments"][0]["start_char"] = True
        errors = validator.errors(record)
        self.assertTrue(any("start_char" in e and "expected type integer" in e for e in errors), errors)

    def test_fixture_hygiene(self) -> None:
        raw = (MZANSI / "fixtures" / "linguistic-records.synthetic.json").read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"(sk-[A-Za-z0-9]{8,}|ghp_[A-Za-z0-9]{8,}|AKIA[0-9A-Z]{12,})", raw))
        for record in fixture_records():
            self.assertTrue(record["evidence"]["synthetic"], record["record_id"])
            self.assertTrue(record["source"]["text"].startswith("FIXTURE_"), record["record_id"])
            self.assertEqual(record["source"]["language_tag"], "nso", record["record_id"])


class AdmissionTests(StoreCase):
    def test_admit_then_replay_then_conflict(self) -> None:
        record = fixture_by_id("fx-nso-0001-unverified")
        first = self.store.admit(record, actor="test")
        self.assertEqual(first.outcome, "admitted")
        self.assertEqual(first.event, engine.EVENT_RECORD_ADMITTED)
        self.assertEqual(self.store.sequence, 1)

        replay = self.store.admit(record, actor="test")
        self.assertEqual(replay.outcome, "duplicate")
        self.assertIsNone(replay.entry_id)
        self.assertEqual(self.store.sequence, 1)

        changed = json.loads(json.dumps(record))
        changed["aligned_forms"]["formal"] = "FIXTURE_PLACEHOLDER_CHANGED"
        conflict = self.store.admit(changed, actor="test")
        self.assertEqual(conflict.outcome, "conflict")
        self.assertEqual(conflict.event, engine.EVENT_RECORD_CONFLICT)
        self.assertEqual(self.store.sequence, 2)
        self.assertEqual(self.store.head(record["record_id"]), record)
        self.assertNotEqual(conflict.detail["accepted_payload_hash"], conflict.detail["rejected_payload_hash"])

    def test_admit_refuses_invalid_record_without_appending(self) -> None:
        record = fixture_by_id("fx-nso-0001-unverified")
        record["evidence"]["class"] = "HUMAN_GUESSED"
        with self.assertRaises(engine.SchemaViolation):
            self.store.admit(record, actor="test")
        self.assertEqual(self.store.sequence, 0)
        self.assertFalse(self.ledger.exists())

    def test_actor_is_required(self) -> None:
        with self.assertRaises(engine.DataEngineError):
            self.store.admit(fixture_by_id("fx-nso-0001-unverified"), actor="  ")

    def test_receipts_never_carry_poc_validated(self) -> None:
        self.admit_all()
        for entry in self.store.entries():
            self.assertNotIn("POC_VALIDATED", json.dumps(entry))
            self.assertEqual(entry["schema"], engine.LEDGER_ENTRY_SCHEMA)


class ValidationTransitionTests(StoreCase):
    def setUp(self) -> None:
        super().setUp()
        self.admit_all()
        self.human = "fx-nso-0002-human-recorded"

    def test_validated_requires_validator_ids(self) -> None:
        with self.assertRaises(engine.TransitionRefused):
            self.store.transition_validation(self.human, "validated", actor="test")

    def test_validated_requires_consent(self) -> None:
        with self.assertRaises(engine.TransitionRefused):
            self.store.transition_validation(
                "fx-nso-0005-no-consent", "validated", actor="test", validator_ids=["v1"]
            )

    def test_rejected_and_disputed_require_notes(self) -> None:
        with self.assertRaises(engine.TransitionRefused):
            self.store.transition_validation(self.human, "rejected", actor="test")
        with self.assertRaises(engine.TransitionRefused):
            self.store.transition_validation(self.human, "disputed", actor="test", notes="   ")

    def test_rejected_is_terminal(self) -> None:
        for target in ("validated", "disputed", "pending"):
            with self.assertRaises(engine.TransitionRefused):
                self.store.transition_validation(
                    "fx-nso-0006-rejected", target, actor="test", validator_ids=["v1"], notes="n"
                )

    def test_unknown_status_refused(self) -> None:
        with self.assertRaises(engine.TransitionRefused):
            self.store.transition_validation(self.human, "approved", actor="test")

    def test_validate_dispute_revalidate_path_is_versioned(self) -> None:
        before = self.store.sequence
        r1 = self.store.transition_validation(self.human, "validated", actor="test", validator_ids=["v2", "v1"])
        self.assertEqual(r1.outcome, "transitioned")
        self.assertEqual(self.store.head(self.human)["validation"]["validator_ids"], ["v1", "v2"])
        self.store.transition_validation(self.human, "disputed", actor="test", notes="new evidence")
        self.assertEqual(self.store.head(self.human)["validation"]["status"], "disputed")
        self.store.transition_validation(self.human, "validated", actor="test", validator_ids=["v3"])
        self.assertEqual(self.store.head(self.human)["validation"]["validator_ids"], ["v3"])
        self.assertEqual(self.store.sequence, before + 3)
        history = self.store.history(self.human)
        self.assertEqual([e["event"] for e in history][1:], [engine.EVENT_VALIDATION_TRANSITION] * 3)
        self.assertEqual(history[1]["detail"]["supersedes_entry"], history[0]["entry_id"])


class EvidenceClassTransitionTests(StoreCase):
    def setUp(self) -> None:
        super().setUp()
        self.admit_all()

    def test_unverified_to_human_recorded_requires_provenance_and_consent(self) -> None:
        unverified = "fx-nso-0001-unverified"
        receipt = self.store.transition_evidence_class(unverified, "HUMAN_RECORDED", actor="test")
        self.assertEqual(receipt.detail["gate"], "attested_provenance")

        orphan = fixture_by_id("fx-nso-0001-unverified")
        orphan["record_id"] = "test-orphan-0001"
        orphan["evidence"]["provenance_uri"] = None
        self.store.admit(orphan, actor="test")
        with self.assertRaises(engine.TransitionRefused):
            self.store.transition_evidence_class("test-orphan-0001", "HUMAN_RECORDED", actor="test")

    def test_human_recorded_to_human_validated_requires_validated_status(self) -> None:
        human = "fx-nso-0002-human-recorded"
        with self.assertRaises(engine.TransitionRefused):
            self.store.transition_evidence_class(human, "HUMAN_VALIDATED", actor="test", validator_ids=["v1"])
        self.store.transition_validation(human, "validated", actor="test", validator_ids=["v1"])
        with self.assertRaises(engine.TransitionRefused):
            self.store.transition_evidence_class(human, "HUMAN_VALIDATED", actor="test")
        receipt = self.store.transition_evidence_class(human, "HUMAN_VALIDATED", actor="test", validator_ids=["v9"])
        self.assertEqual(receipt.detail["gate"], "human_validation")
        self.assertEqual(self.store.head(human)["validation"]["validator_ids"], ["v1", "v9"])

    def test_synthetic_evidence_never_self_promotes(self) -> None:
        ai = "fx-nso-0003-ai-generated-codeswitch"
        for target in ("HUMAN_RECORDED", "UNVERIFIED", "AI_TRANSFORMED"):
            with self.assertRaises(engine.TransitionRefused):
                self.store.transition_evidence_class(ai, target, actor="test", validator_ids=["v1"])
        # Human validation of synthetic output is allowed, but origin stays visible.
        self.store.transition_validation(ai, "validated", actor="test", validator_ids=["v1"])
        receipt = self.store.transition_evidence_class(ai, "HUMAN_VALIDATED", actor="test", validator_ids=["v1"])
        head = self.store.head(ai)
        self.assertEqual(head["evidence"]["class"], "HUMAN_VALIDATED")
        self.assertTrue(head["evidence"]["synthetic"])
        self.assertTrue(receipt.detail["synthetic"])
        self.assertEqual(receipt.detail["from"], "AI_GENERATED")

    def test_human_validated_cannot_regress_and_rejected_is_terminal(self) -> None:
        human = "fx-nso-0002-human-recorded"
        self.store.transition_validation(human, "validated", actor="test", validator_ids=["v1"])
        self.store.transition_evidence_class(human, "HUMAN_VALIDATED", actor="test", validator_ids=["v1"])
        with self.assertRaises(engine.TransitionRefused):
            self.store.transition_evidence_class(human, "HUMAN_RECORDED", actor="test")
        with self.assertRaises(engine.TransitionRefused):
            self.store.transition_evidence_class(human, "REJECTED", actor="test")
        self.store.transition_evidence_class(human, "REJECTED", actor="test", reason="withdrawn by validator")
        head = self.store.head(human)
        self.assertEqual(head["evidence"]["class"], "REJECTED")
        self.assertEqual(head["validation"]["status"], "rejected")
        for target in engine.EVIDENCE_CLASSES:
            with self.assertRaises(engine.TransitionRefused):
                self.store.transition_evidence_class(human, target, actor="test", validator_ids=["v1"], reason="r")

    def test_rule_table_has_no_edge_into_synthetic_or_unverified(self) -> None:
        for (_, target), _gate in engine.EVIDENCE_CLASS_TRANSITIONS.items():
            self.assertNotIn(target, {"AI_GENERATED", "AI_TRANSFORMED", "UNVERIFIED"})


class ConsentAndAdmissibilityTests(StoreCase):
    def test_admissible_set_is_computed_from_fields(self) -> None:
        self.admit_all()
        self.store.admit(human_record(), actor="test")
        self.assertEqual(self.store.admissible_records(), [])

        self.store.transition_validation("test-human-0001", "validated", actor="test", validator_ids=["v1"])
        self.assertEqual(self.store.admissible_records(), [])
        self.store.transition_evidence_class("test-human-0001", "HUMAN_VALIDATED", actor="test", validator_ids=["v1"])
        self.assertEqual([r["record_id"] for r in self.store.admissible_records()], ["test-human-0001"])

        unlicensed = human_record("test-human-0002")
        unlicensed["evidence"]["license"] = None
        self.store.admit(unlicensed, actor="test")
        self.store.transition_validation("test-human-0002", "validated", actor="test", validator_ids=["v1"])
        self.store.transition_evidence_class("test-human-0002", "HUMAN_VALIDATED", actor="test", validator_ids=["v1"])
        self.assertEqual([r["record_id"] for r in self.store.admissible_records()], ["test-human-0001"])

    def test_consent_withdrawal_removes_admissibility_and_is_one_way(self) -> None:
        self.store.admit(human_record(), actor="test")
        self.store.transition_validation("test-human-0001", "validated", actor="test", validator_ids=["v1"])
        self.store.transition_evidence_class("test-human-0001", "HUMAN_VALIDATED", actor="test", validator_ids=["v1"])
        self.assertEqual(len(self.store.admissible_records()), 1)

        with self.assertRaises(engine.TransitionRefused):
            self.store.withdraw_consent("test-human-0001", actor="test", reason="")
        receipt = self.store.withdraw_consent("test-human-0001", actor="test", reason="speaker request")
        self.assertEqual(receipt.event, engine.EVENT_CONSENT_WITHDRAWN)
        head = self.store.head("test-human-0001")
        self.assertFalse(head["evidence"]["speaker_consent"])
        self.assertEqual(head["validation"]["status"], "disputed")
        self.assertEqual(self.store.admissible_records(), [])
        with self.assertRaises(engine.TransitionRefused):
            self.store.withdraw_consent("test-human-0001", actor="test", reason="again")
        with self.assertRaises(engine.TransitionRefused):
            self.store.transition_validation("test-human-0001", "validated", actor="test", validator_ids=["v1"])

    def test_snapshot_counts(self) -> None:
        self.admit_all()
        snapshot = self.store.snapshot()
        self.assertEqual(snapshot["records"], 6)
        self.assertEqual(snapshot["by_evidence_class"]["AI_GENERATED"], 1)
        self.assertEqual(snapshot["by_validation_status"]["rejected"], 1)
        self.assertEqual(snapshot["admissible_human"], 0)
        self.assertEqual(snapshot["head_hash"], self.store.head_hash)


class PersistenceTests(StoreCase):
    def test_reload_reproduces_state_and_chain(self) -> None:
        self.admit_all()
        self.store.transition_validation("fx-nso-0002-human-recorded", "validated", actor="test", validator_ids=["v1"])
        self.store.verify_chain()
        reloaded = engine.LinguisticRecordStore(self.ledger)
        self.assertEqual(reloaded.head_hash, self.store.head_hash)
        self.assertEqual(reloaded.sequence, self.store.sequence)
        for record_id in self.store.record_ids():
            self.assertEqual(reloaded.head(record_id), self.store.head(record_id))

    def test_tampered_line_breaks_the_chain(self) -> None:
        self.admit_all()
        lines = self.ledger.read_text(encoding="utf-8").splitlines()
        entry = json.loads(lines[2])
        entry["record"]["evidence"]["class"] = "HUMAN_VALIDATED"
        lines[2] = json.dumps(entry, sort_keys=True, separators=(",", ":"))
        self.ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with self.assertRaises(engine.LedgerIntegrityError):
            engine.LinguisticRecordStore(self.ledger)

    def test_deleted_line_breaks_the_chain(self) -> None:
        self.admit_all()
        lines = self.ledger.read_text(encoding="utf-8").splitlines()
        del lines[1]
        self.ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with self.assertRaises(engine.LedgerIntegrityError):
            engine.LinguisticRecordStore(self.ledger)

    def test_foreign_or_malformed_lines_are_refused(self) -> None:
        self.ledger.write_text('{"schema":"something.else"}\n', encoding="utf-8")
        with self.assertRaises(engine.LedgerIntegrityError):
            engine.LinguisticRecordStore(self.ledger)
        self.ledger.write_text("not json\n", encoding="utf-8")
        with self.assertRaises(engine.LedgerIntegrityError):
            engine.LinguisticRecordStore(self.ledger)

    def test_hashes_are_deterministic_for_identical_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            other = engine.LinguisticRecordStore(Path(tmp) / "other.jsonl", clock=FixedClock())
            for record in fixture_records():
                self.store.admit(record, actor="test")
                other.admit(record, actor="test")
            self.assertEqual(self.store.head_hash, other.head_hash)
            self.assertEqual(
                [e["entry_hash"] for e in self.store.entries()],
                [e["entry_hash"] for e in other.entries()],
            )
            self.assertEqual(self.store.head_hash, engine.sha256_hex(
                list(self.store.entries())[-1]["prev_hash"]
                + engine.canonical_json({k: v for k, v in list(self.store.entries())[-1].items() if k != "entry_hash"})
            ))


if __name__ == "__main__":
    unittest.main()
