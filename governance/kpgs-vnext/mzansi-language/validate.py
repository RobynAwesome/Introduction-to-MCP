#!/usr/bin/env python3
"""Dependency-free gate for the Mzansi Data Engine foundation (#103 PR2).

Checks, in order:
1. the four PR1 contracts are still JSON Schema Draft 2020-12 and strict;
2. every synthetic fixture record validates and is honestly labelled synthetic;
3. every invalid fixture case is refused with the expected error;
4. a throwaway ledger round-trips: admit, replay, conflict, transition, reload,
   chain verification, and tamper detection.

Prints ``KPGS-MZANSI-DATA-ENGINE PASS`` on success. Any failure exits non-zero
with a ``KPGS-MZANSI-DATA-ENGINE FAIL:`` line. This gate proves structure and
rule enforcement; it does not prove any linguistic, dataset or speech claim.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
from typing import Any

HERE = Path(__file__).resolve().parent
PREFIX = "KPGS-MZANSI-DATA-ENGINE"

CONTRACTS = {
    "linguistic-record.schema.json": {
        "schema",
        "record_id",
        "source",
        "aligned_forms",
        "code_switch",
        "speaker_context",
        "evidence",
        "validation",
        "created_at",
    },
    "inference-request.schema.json": {"schema", "request_id", "input", "target", "user_contract", "execution", "created_at"},
    "validation-receipt.schema.json": {"schema", "receipt_id", "request_id", "created_at"},
}

SECRET_LIKE = re.compile(r"(sk-[A-Za-z0-9]{8,}|ghp_[A-Za-z0-9]{8,}|AKIA[0-9A-Z]{12,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")


def fail(message: str) -> None:
    raise SystemExit(f"{PREFIX} FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def load_json(relative: str) -> dict[str, Any]:
    path = HERE / relative
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing {relative}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {relative}: {exc}")
    require(isinstance(value, dict), f"{relative} must contain a JSON object")
    return value


def load_engine():
    spec = importlib.util.spec_from_file_location("mzansi_data_engine", HERE / "data_engine.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module  # dataclasses resolve postponed annotations through sys.modules
    spec.loader.exec_module(module)
    return module


def validate_contract_shapes() -> None:
    for name, required in CONTRACTS.items():
        schema = load_json(name)
        require(schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", f"{name} must use Draft 2020-12")
        require(schema.get("type") == "object", f"{name} must define an object root")
        require(schema.get("additionalProperties") is False, f"{name} must reject undeclared root properties")
        declared = set(schema.get("required", []))
        require(required <= declared, f"{name} missing required fields: {sorted(required - declared)}")
    evidence = load_json("evidence-class.schema.json")
    require(evidence.get("type") == "string", "evidence-class must be a string enum")
    require(
        evidence.get("enum") == ["HUMAN_RECORDED", "HUMAN_VALIDATED", "AI_GENERATED", "AI_TRANSFORMED", "UNVERIFIED", "REJECTED"],
        "evidence-class enum drifted from PR1",
    )


def validate_synthetic_fixtures(engine) -> list[dict[str, Any]]:
    fixture = load_json("fixtures/linguistic-records.synthetic.json")
    require(fixture.get("non_canonical") is True, "synthetic fixture set must declare non_canonical: true")
    records = fixture.get("records")
    require(isinstance(records, list) and len(records) >= 4, "synthetic fixture set needs at least four records")
    validator = engine.record_validator()
    seen: set[str] = set()
    raw = json.dumps(fixture)
    require(SECRET_LIKE.search(raw) is None, "synthetic fixture contains a secret-like token")
    for record in records:
        errors = validator.errors(record)
        require(not errors, f"synthetic fixture {record.get('record_id')!r} invalid: {errors[0] if errors else ''}")
        require(record["record_id"] not in seen, f"duplicate fixture record_id {record['record_id']}")
        seen.add(record["record_id"])
        require(record["evidence"]["synthetic"] is True, f"fixture {record['record_id']} must be synthetic: true")
        require(record["source"]["language_tag"] == "nso", f"fixture {record['record_id']} leaves the Sepedi-only slice")
        require(record["source"]["text"].startswith("FIXTURE_"), f"fixture {record['record_id']} text is not a placeholder")
        uri = record["evidence"]["provenance_uri"]
        require(uri is None or uri.startswith("fixture://"), f"fixture {record['record_id']} provenance must use fixture://")
        for segment in record["code_switch"]["segments"]:
            text = record["source"]["text"]
            require(
                text[segment["start_char"] : segment["end_char"]] == segment["text"],
                f"fixture {record['record_id']} code-switch offsets do not match segment text",
            )
        if record["code_switch"]["present"]:
            require(record["code_switch"]["segments"], f"fixture {record['record_id']} present=true needs segments")
        else:
            require(not record["code_switch"]["segments"], f"fixture {record['record_id']} present=false must have no segments")
    classes = {record["evidence"]["class"] for record in records}
    require({"UNVERIFIED", "HUMAN_RECORDED", "AI_GENERATED", "AI_TRANSFORMED"} <= classes, "fixtures must cover the promotable classes")
    return records


def validate_invalid_fixtures(engine) -> None:
    fixture = load_json("fixtures/linguistic-records.invalid.json")
    cases = fixture.get("cases")
    require(isinstance(cases, list) and len(cases) >= 6, "invalid fixture set needs at least six cases")
    validator = engine.record_validator()
    for case in cases:
        errors = validator.errors(case["record"])
        require(bool(errors), f"invalid case {case['case_id']} was accepted")
        require(
            any(case["expected_error_contains"] in e for e in errors),
            f"invalid case {case['case_id']} failed for an unexpected reason: {errors}",
        )


class FixedClock:
    def __init__(self) -> None:
        self.moment = datetime(2026, 9, 30, 0, 0, 0, tzinfo=timezone.utc)

    def __call__(self) -> datetime:
        self.moment += timedelta(seconds=1)
        return self.moment


def validate_ledger_round_trip(engine, records: list[dict[str, Any]]) -> None:
    by_id = {record["record_id"]: record for record in records}
    with tempfile.TemporaryDirectory() as tmp:
        ledger = Path(tmp) / "mzansi-ledger.jsonl"
        store = engine.LinguisticRecordStore(ledger, clock=FixedClock())
        for record in records:
            receipt = store.admit(record, actor="validate.py")
            require(receipt.outcome == "admitted", f"admit failed for {record['record_id']}: {receipt.outcome}")
        sequence_after_admit = store.sequence
        require(sequence_after_admit == len(records), "one ledger entry per admitted record expected")

        replay = store.admit(records[0], actor="validate.py")
        require(replay.outcome == "duplicate", "identical replay must be reported as duplicate")
        require(store.sequence == sequence_after_admit, "identical replay must not append")

        changed = json.loads(json.dumps(records[0]))
        changed["aligned_forms"]["semantic_gloss"] = "FIXTURE_PLACEHOLDER_GLOSS_CHANGED"
        conflict = store.admit(changed, actor="validate.py")
        require(conflict.outcome == "conflict", "changed payload under a known id must be a conflict")
        require(store.head(records[0]["record_id"]) == records[0], "conflict must leave the head unchanged")

        human = by_id["fx-nso-0002-human-recorded"]["record_id"]
        try:
            store.transition_validation(human, "validated", actor="validate.py")
            fail("validated without validator_ids was accepted")
        except engine.TransitionRefused:
            pass
        store.transition_validation(human, "validated", actor="validate.py", validator_ids=["fixture-validator-1"])
        store.transition_evidence_class(human, "HUMAN_VALIDATED", actor="validate.py", validator_ids=["fixture-validator-1"])
        require(store.head(human)["evidence"]["synthetic"] is True, "synthetic flag must survive promotion")
        require(store.admissible_records(include_synthetic=False) == [], "synthetic fixtures must never be human-admissible")
        require(len(store.admissible_records(include_synthetic=True)) == 1, "exactly one synthetic-admissible record expected")

        ai = by_id["fx-nso-0003-ai-generated-codeswitch"]["record_id"]
        try:
            store.transition_evidence_class(ai, "HUMAN_RECORDED", actor="validate.py")
            fail("AI_GENERATED -> HUMAN_RECORDED was accepted")
        except engine.TransitionRefused:
            pass

        no_consent = by_id["fx-nso-0005-no-consent"]["record_id"]
        try:
            store.transition_validation(no_consent, "validated", actor="validate.py", validator_ids=["fixture-validator-1"])
            fail("validated without consent was accepted")
        except engine.TransitionRefused:
            pass

        rejected = by_id["fx-nso-0006-rejected"]["record_id"]
        try:
            store.transition_validation(rejected, "validated", actor="validate.py", validator_ids=["fixture-validator-1"])
            fail("rejected -> validated was accepted")
        except engine.TransitionRefused:
            pass

        store.verify_chain()
        head_hash = store.head_hash
        reloaded = engine.LinguisticRecordStore(ledger, clock=FixedClock())
        require(reloaded.head_hash == head_hash, "reload must reproduce the head hash")
        require(reloaded.head(human) == store.head(human), "reload must reproduce record heads")
        require(reloaded.snapshot()["records"] == len(records), "reload must reproduce record count")

        lines = ledger.read_text(encoding="utf-8").splitlines()
        tampered = json.loads(lines[1])
        tampered["actor"] = "tampered"
        lines[1] = json.dumps(tampered, sort_keys=True, separators=(",", ":"))
        ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")
        try:
            engine.LinguisticRecordStore(ledger, clock=FixedClock())
            fail("tampered ledger line was accepted on reload")
        except engine.LedgerIntegrityError:
            pass


def main() -> None:
    engine = load_engine()
    validate_contract_shapes()
    records = validate_synthetic_fixtures(engine)
    validate_invalid_fixtures(engine)
    validate_ledger_round_trip(engine, records)
    print(
        f"{PREFIX} PASS: contracts strict, {len(records)} synthetic fixtures admitted, invalid cases refused, "
        "ledger replay/conflict/transition/reload/tamper boundaries hold. No linguistic or model claim."
    )


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # surface as a gate failure, not a traceback
        print(f"{PREFIX} FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
