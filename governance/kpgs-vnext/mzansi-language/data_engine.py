"""Mzansi Data Engine foundation - Phase 7 PR2 for RobynAwesome/Introduction-to-MCP#103.

Schema-backed, append-only persistence for linguistic records with provenance,
consent and validation state. Dependency-free (standard library only), in the
same style as the other ``governance/kpgs-vnext`` runtimes.

What this module does
---------------------
* validates records against ``linguistic-record.schema.json`` with a small
  Draft 2020-12 subset evaluator driven by the schema file itself;
* persists admitted records to a hash-linked JSONL ledger (one entry per
  governed event) with idempotent replay and conflict detection;
* applies explicit rule tables for validation-status and evidence-class
  transitions so that synthetic evidence never silently becomes human truth;
* computes the admissible evidence set from the data-plane fields
  (class, status, consent, license, synthetic) instead of from prose.

What this module does not do
----------------------------
No model, dataset, speech, routing, translation or native-speaker claim. It
stores and governs evidence records; it does not produce them.

Boundary words: ``PENDING`` and ``HOLD`` are valid outcomes. ``POC_VALIDATED``
is a receipt outcome elsewhere, never a return value here.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Callable, Iterable, Iterator, Mapping

HERE = Path(__file__).resolve().parent
RECORD_SCHEMA_PATH = HERE / "linguistic-record.schema.json"

LEDGER_ENTRY_SCHEMA = "kpgs.mzansi.data-engine.ledger-entry.v1"
RECORD_SCHEMA_CONST = "kpgs.mzansi.linguistic-record.v1"
GENESIS_HASH = "0" * 64

EVIDENCE_CLASSES = (
    "HUMAN_RECORDED",
    "HUMAN_VALIDATED",
    "AI_GENERATED",
    "AI_TRANSFORMED",
    "UNVERIFIED",
    "REJECTED",
)
SYNTHETIC_CLASSES = frozenset({"AI_GENERATED", "AI_TRANSFORMED"})
VALIDATION_STATUSES = ("pending", "validated", "rejected", "disputed")

# validation.status lifecycle. Keys are current status, values are the statuses
# that may follow. ``rejected`` is terminal.
VALIDATION_TRANSITIONS: Mapping[str, frozenset[str]] = {
    "pending": frozenset({"validated", "rejected", "disputed"}),
    "disputed": frozenset({"validated", "rejected"}),
    "validated": frozenset({"disputed"}),
    "rejected": frozenset(),
}

# evidence.class lifecycle. Each allowed edge names the gate that must hold.
# Anything not listed is refused. ``REJECTED`` is terminal.
EVIDENCE_CLASS_TRANSITIONS: Mapping[tuple[str, str], str] = {
    ("UNVERIFIED", "HUMAN_RECORDED"): "attested_provenance",
    ("HUMAN_RECORDED", "HUMAN_VALIDATED"): "human_validation",
    ("AI_GENERATED", "HUMAN_VALIDATED"): "human_validation",
    ("AI_TRANSFORMED", "HUMAN_VALIDATED"): "human_validation",
    ("UNVERIFIED", "REJECTED"): "rejection_reason",
    ("HUMAN_RECORDED", "REJECTED"): "rejection_reason",
    ("HUMAN_VALIDATED", "REJECTED"): "rejection_reason",
    ("AI_GENERATED", "REJECTED"): "rejection_reason",
    ("AI_TRANSFORMED", "REJECTED"): "rejection_reason",
}

EVENT_RECORD_ADMITTED = "record_admitted"
EVENT_RECORD_CONFLICT = "record_conflict"
EVENT_VALIDATION_TRANSITION = "validation_transition"
EVENT_EVIDENCE_CLASS_TRANSITION = "evidence_class_transition"
EVENT_CONSENT_WITHDRAWN = "consent_withdrawn"
EVENTS = frozenset(
    {
        EVENT_RECORD_ADMITTED,
        EVENT_RECORD_CONFLICT,
        EVENT_VALIDATION_TRANSITION,
        EVENT_EVIDENCE_CLASS_TRANSITION,
        EVENT_CONSENT_WITHDRAWN,
    }
)

_DATE_TIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(\.\d+)?([Zz]|[+-]\d{2}:\d{2})$"
)


class DataEngineError(Exception):
    """Base class for governed refusals raised by this module."""


class SchemaViolation(DataEngineError):
    """A payload does not satisfy its JSON Schema contract."""

    def __init__(self, errors: list[str]):
        self.errors = list(errors)
        super().__init__("; ".join(self.errors))


class TransitionRefused(DataEngineError):
    """A lifecycle transition is not permitted by the rule tables."""


class LedgerIntegrityError(DataEngineError):
    """The on-disk ledger failed hash-chain or structural verification."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(moment: datetime) -> str:
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.isoformat()


# ---------------------------------------------------------------------------
# Schema evaluation (Draft 2020-12 subset, driven by the schema files)
# ---------------------------------------------------------------------------


class SchemaValidator:
    """Evaluate the JSON Schema keywords the Mzansi contracts actually use.

    Supported: ``type`` (scalar or list, including ``null``), ``const``,
    ``enum``, ``required``, ``properties``, ``additionalProperties: false``,
    ``minLength``, ``minimum``, ``maximum``, ``pattern``, ``items``,
    ``uniqueItems``, ``format`` (``date-time`` checked; ``uri-reference`` must
    be a whitespace-free string) and ``$ref`` to a sibling schema file.

    Unsupported keywords raise ``ValueError`` at load time so a contract change
    can never pass silently through a validator that ignores it.
    """

    SUPPORTED = frozenset(
        {
            "$schema",
            "$id",
            "title",
            "description",
            "type",
            "const",
            "enum",
            "required",
            "properties",
            "additionalProperties",
            "minLength",
            "minimum",
            "maximum",
            "pattern",
            "items",
            "uniqueItems",
            "format",
            "$ref",
        }
    )

    def __init__(self, schema_path: Path):
        self.schema_path = Path(schema_path)
        self.schema = self._load(self.schema_path)
        self._refs: dict[str, Mapping[str, Any]] = {}
        self._check_supported(self.schema, self.schema_path.name)

    @staticmethod
    def _load(path: Path) -> Mapping[str, Any]:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise ValueError(f"schema file missing: {path}") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"schema file is not valid JSON: {path}: {exc}") from exc
        if not isinstance(value, Mapping):
            raise ValueError(f"schema root must be an object: {path}")
        return value

    def _check_supported(self, node: Any, where: str) -> None:
        if isinstance(node, Mapping):
            unsupported = set(node) - self.SUPPORTED
            if unsupported:
                raise ValueError(f"{where}: unsupported schema keywords {sorted(unsupported)}")
            ref = node.get("$ref")
            if ref is not None:
                self._resolve_ref(ref)
            for key in ("properties",):
                for name, child in node.get(key, {}).items():
                    self._check_supported(child, f"{where}/{key}/{name}")
            if "items" in node:
                self._check_supported(node["items"], f"{where}/items")

    def _resolve_ref(self, ref: str) -> Mapping[str, Any]:
        if ref in self._refs:
            return self._refs[ref]
        if "#" in ref or "/" in ref or ref.startswith(".."):
            raise ValueError(f"only sibling-file $ref values are supported, got {ref!r}")
        target = self.schema_path.parent / ref
        resolved = self._load(target)
        self._refs[ref] = resolved
        self._check_supported(resolved, ref)
        return resolved

    def errors(self, instance: Any) -> list[str]:
        found: list[str] = []
        self._walk(self.schema, instance, "$", found)
        return found

    def validate(self, instance: Any) -> None:
        found = self.errors(instance)
        if found:
            raise SchemaViolation(found)

    # -- keyword evaluation -------------------------------------------------

    @staticmethod
    def _type_matches(expected: str, value: Any) -> bool:
        if expected == "null":
            return value is None
        if expected == "boolean":
            return isinstance(value, bool)
        if expected == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        if expected == "number":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        if expected == "string":
            return isinstance(value, str)
        if expected == "array":
            return isinstance(value, list)
        if expected == "object":
            return isinstance(value, Mapping)
        raise ValueError(f"unsupported type keyword value {expected!r}")

    def _walk(self, node: Mapping[str, Any], value: Any, path: str, found: list[str]) -> None:
        if "$ref" in node:
            node = self._resolve_ref(node["$ref"])

        if "const" in node and value != node["const"]:
            found.append(f"{path}: expected const {node['const']!r}")
            return

        if "enum" in node and value not in node["enum"]:
            found.append(f"{path}: value {value!r} not in enum")
            return

        declared = node.get("type")
        if declared is not None:
            types = declared if isinstance(declared, list) else [declared]
            if not any(self._type_matches(t, value) for t in types):
                found.append(f"{path}: expected type {declared}, got {type(value).__name__}")
                return

        if isinstance(value, str):
            min_length = node.get("minLength")
            if min_length is not None and len(value) < min_length:
                found.append(f"{path}: shorter than minLength {min_length}")
            pattern = node.get("pattern")
            if pattern is not None and re.search(pattern, value) is None:
                found.append(f"{path}: does not match pattern {pattern}")
            fmt = node.get("format")
            if fmt == "date-time" and not self._is_date_time(value):
                found.append(f"{path}: not an RFC 3339 date-time")
            elif fmt == "uri-reference" and re.search(r"\s", value):
                found.append(f"{path}: uri-reference contains whitespace")

        if isinstance(value, (int, float)) and not isinstance(value, bool):
            minimum = node.get("minimum")
            if minimum is not None and value < minimum:
                found.append(f"{path}: below minimum {minimum}")
            maximum = node.get("maximum")
            if maximum is not None and value > maximum:
                found.append(f"{path}: above maximum {maximum}")

        if isinstance(value, list):
            if node.get("uniqueItems") and len({canonical_json(v) for v in value}) != len(value):
                found.append(f"{path}: items are not unique")
            item_schema = node.get("items")
            if item_schema is not None:
                for index, item in enumerate(value):
                    self._walk(item_schema, item, f"{path}[{index}]", found)

        if isinstance(value, Mapping):
            properties = node.get("properties", {})
            for name in node.get("required", []):
                if name not in value:
                    found.append(f"{path}: missing required property {name!r}")
            if node.get("additionalProperties") is False:
                for name in value:
                    if name not in properties:
                        found.append(f"{path}: undeclared property {name!r}")
            for name, child in properties.items():
                if name in value:
                    self._walk(child, value[name], f"{path}.{name}", found)

    @staticmethod
    def _is_date_time(value: str) -> bool:
        if _DATE_TIME_RE.match(value) is None:
            return False
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00").replace("z", "+00:00"))
        except ValueError:
            return False
        return True


def record_validator() -> SchemaValidator:
    return SchemaValidator(RECORD_SCHEMA_PATH)


# ---------------------------------------------------------------------------
# Receipts and ledger entries
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Receipt:
    """What the engine is willing to say happened. Never carries ``POC_VALIDATED``."""

    outcome: str
    record_id: str
    event: str | None
    entry_id: str | None
    entry_hash: str | None
    detail: Mapping[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome,
            "record_id": self.record_id,
            "event": self.event,
            "entry_id": self.entry_id,
            "entry_hash": self.entry_hash,
            "detail": dict(self.detail),
        }


def _entry_hash(entry: Mapping[str, Any]) -> str:
    body = {k: v for k, v in entry.items() if k != "entry_hash"}
    return sha256_hex(entry["prev_hash"] + canonical_json(body))


class LinguisticRecordStore:
    """Append-only, hash-linked JSONL store for Mzansi linguistic records.

    One line per governed event. State is rebuilt by replay; the chain is
    verified on load and a break raises ``LedgerIntegrityError`` (HOLD).
    """

    def __init__(
        self,
        ledger_path: Path | str,
        *,
        validator: SchemaValidator | None = None,
        clock: Callable[[], datetime] = utc_now,
    ):
        self.ledger_path = Path(ledger_path)
        self.validator = validator or record_validator()
        self.clock = clock
        self._entries: list[dict[str, Any]] = []
        self._heads: dict[str, dict[str, Any]] = {}
        self._head_entry: dict[str, str] = {}
        self._payload_hashes: dict[str, str] = {}
        self._head_hash = GENESIS_HASH
        if self.ledger_path.exists():
            self._replay()

    # -- public read surface ------------------------------------------------

    @property
    def head_hash(self) -> str:
        return self._head_hash

    @property
    def sequence(self) -> int:
        return len(self._entries)

    def entries(self) -> Iterator[Mapping[str, Any]]:
        for entry in self._entries:
            yield deepcopy(entry)

    def record_ids(self) -> list[str]:
        return sorted(self._heads)

    def head(self, record_id: str) -> dict[str, Any]:
        try:
            return deepcopy(self._heads[record_id])
        except KeyError as exc:
            raise KeyError(f"unknown record_id {record_id!r}") from exc

    def history(self, record_id: str) -> list[Mapping[str, Any]]:
        return [deepcopy(e) for e in self._entries if e["record_id"] == record_id]

    def admissible_records(self, *, include_synthetic: bool = False) -> list[dict[str, Any]]:
        """Evidence that may feed downstream work, computed from data-plane fields only."""
        chosen: list[dict[str, Any]] = []
        for record_id in sorted(self._heads):
            record = self._heads[record_id]
            evidence = record["evidence"]
            if evidence["class"] != "HUMAN_VALIDATED":
                continue
            if record["validation"]["status"] != "validated":
                continue
            if evidence["speaker_consent"] is not True:
                continue
            if evidence["license"] is None:
                continue
            if evidence["synthetic"] and not include_synthetic:
                continue
            chosen.append(deepcopy(record))
        return chosen

    def snapshot(self) -> dict[str, Any]:
        by_class = {name: 0 for name in EVIDENCE_CLASSES}
        by_status = {name: 0 for name in VALIDATION_STATUSES}
        for record in self._heads.values():
            by_class[record["evidence"]["class"]] += 1
            by_status[record["validation"]["status"]] += 1
        return {
            "schema": "kpgs.mzansi.data-engine.snapshot.v1",
            "ledger_path": str(self.ledger_path),
            "sequence": self.sequence,
            "head_hash": self._head_hash,
            "records": len(self._heads),
            "by_evidence_class": by_class,
            "by_validation_status": by_status,
            "admissible_human": len(self.admissible_records(include_synthetic=False)),
            "admissible_including_synthetic": len(self.admissible_records(include_synthetic=True)),
        }

    def verify_chain(self) -> None:
        prev = GENESIS_HASH
        for index, entry in enumerate(self._entries):
            if entry.get("sequence") != index + 1:
                raise LedgerIntegrityError(f"sequence gap at line {index + 1}")
            if entry.get("prev_hash") != prev:
                raise LedgerIntegrityError(f"prev_hash mismatch at sequence {index + 1}")
            if _entry_hash(entry) != entry.get("entry_hash"):
                raise LedgerIntegrityError(f"entry_hash mismatch at sequence {index + 1}")
            prev = entry["entry_hash"]
        if prev != self._head_hash:
            raise LedgerIntegrityError("head hash does not match last entry")

    # -- governed writes ----------------------------------------------------

    def admit(self, record: Mapping[str, Any], *, actor: str) -> Receipt:
        """Admit a record. Replays are idempotent; a changed payload under a known id is a conflict."""
        self._require_actor(actor)
        candidate = deepcopy(dict(record))
        self.validator.validate(candidate)
        record_id = candidate["record_id"]
        payload_hash = sha256_hex(canonical_json(candidate))

        known = self._payload_hashes.get(record_id)
        if known is not None:
            if known == payload_hash:
                return Receipt(
                    outcome="duplicate",
                    record_id=record_id,
                    event=None,
                    entry_id=None,
                    entry_hash=None,
                    detail={"payload_hash": payload_hash, "note": "identical replay; nothing appended"},
                )
            entry = self._append(
                EVENT_RECORD_CONFLICT,
                record_id,
                actor,
                record=None,
                detail={
                    "accepted_payload_hash": known,
                    "rejected_payload_hash": payload_hash,
                    "note": "record_id already admitted with different content; head unchanged",
                },
            )
            return Receipt(
                outcome="conflict",
                record_id=record_id,
                event=EVENT_RECORD_CONFLICT,
                entry_id=entry["entry_id"],
                entry_hash=entry["entry_hash"],
                detail=entry["detail"],
            )

        entry = self._append(
            EVENT_RECORD_ADMITTED,
            record_id,
            actor,
            record=candidate,
            detail={"payload_hash": payload_hash},
        )
        return Receipt(
            outcome="admitted",
            record_id=record_id,
            event=EVENT_RECORD_ADMITTED,
            entry_id=entry["entry_id"],
            entry_hash=entry["entry_hash"],
            detail=entry["detail"],
        )

    def transition_validation(
        self,
        record_id: str,
        new_status: str,
        *,
        actor: str,
        validator_ids: Iterable[str] = (),
        notes: str | None = None,
    ) -> Receipt:
        self._require_actor(actor)
        current = self.head(record_id)
        old_status = current["validation"]["status"]
        if new_status not in VALIDATION_STATUSES:
            raise TransitionRefused(f"unknown validation status {new_status!r}")
        if new_status not in VALIDATION_TRANSITIONS[old_status]:
            raise TransitionRefused(f"validation {old_status} -> {new_status} is not permitted")

        ids = sorted(set(validator_ids))
        if new_status == "validated":
            if not ids:
                raise TransitionRefused("validated requires at least one validator_id")
            if current["evidence"]["speaker_consent"] is not True:
                raise TransitionRefused("validated requires speaker_consent true")
        if new_status in {"rejected", "disputed"} and not (notes or "").strip():
            raise TransitionRefused(f"{new_status} requires non-empty notes")

        updated = deepcopy(current)
        updated["validation"]["status"] = new_status
        updated["validation"]["validator_ids"] = ids if ids else current["validation"]["validator_ids"]
        updated["validation"]["notes"] = notes if notes is not None else current["validation"]["notes"]
        return self._append_version(
            EVENT_VALIDATION_TRANSITION,
            record_id,
            actor,
            updated,
            {"from": old_status, "to": new_status, "validator_ids": ids},
        )

    def transition_evidence_class(
        self,
        record_id: str,
        new_class: str,
        *,
        actor: str,
        validator_ids: Iterable[str] = (),
        reason: str | None = None,
    ) -> Receipt:
        self._require_actor(actor)
        current = self.head(record_id)
        old_class = current["evidence"]["class"]
        if new_class not in EVIDENCE_CLASSES:
            raise TransitionRefused(f"unknown evidence class {new_class!r}")
        gate = EVIDENCE_CLASS_TRANSITIONS.get((old_class, new_class))
        if gate is None:
            raise TransitionRefused(f"evidence class {old_class} -> {new_class} is not permitted")

        ids = sorted(set(validator_ids))
        if gate == "attested_provenance":
            if current["evidence"]["provenance_uri"] is None:
                raise TransitionRefused("attested_provenance requires provenance_uri")
            if current["evidence"]["speaker_consent"] is not True:
                raise TransitionRefused("attested_provenance requires speaker_consent true")
        elif gate == "human_validation":
            if current["validation"]["status"] != "validated":
                raise TransitionRefused("human_validation requires validation.status validated")
            if not ids:
                raise TransitionRefused("human_validation requires at least one validator_id")
            if current["evidence"]["speaker_consent"] is not True:
                raise TransitionRefused("human_validation requires speaker_consent true")
        elif gate == "rejection_reason":
            if not (reason or "").strip():
                raise TransitionRefused("REJECTED requires a non-empty reason")

        updated = deepcopy(current)
        updated["evidence"]["class"] = new_class
        if gate == "human_validation":
            merged = sorted(set(updated["validation"]["validator_ids"]) | set(ids))
            updated["validation"]["validator_ids"] = merged
        if gate == "rejection_reason":
            updated["validation"]["status"] = "rejected"
            updated["validation"]["notes"] = reason
        # ``synthetic`` is immutable: origin stays visible after promotion.
        updated["evidence"]["synthetic"] = current["evidence"]["synthetic"]
        return self._append_version(
            EVENT_EVIDENCE_CLASS_TRANSITION,
            record_id,
            actor,
            updated,
            {
                "from": old_class,
                "to": new_class,
                "gate": gate,
                "validator_ids": ids,
                "synthetic": current["evidence"]["synthetic"],
                "reason": reason,
            },
        )

    def withdraw_consent(self, record_id: str, *, actor: str, reason: str) -> Receipt:
        """Consent can be withdrawn through the engine; it is never re-granted here."""
        self._require_actor(actor)
        if not (reason or "").strip():
            raise TransitionRefused("consent withdrawal requires a non-empty reason")
        current = self.head(record_id)
        if current["evidence"]["speaker_consent"] is not True:
            raise TransitionRefused("speaker_consent is already false")
        updated = deepcopy(current)
        updated["evidence"]["speaker_consent"] = False
        if updated["validation"]["status"] == "validated":
            updated["validation"]["status"] = "disputed"
        updated["validation"]["notes"] = reason
        return self._append_version(
            EVENT_CONSENT_WITHDRAWN,
            record_id,
            actor,
            updated,
            {"reason": reason, "validation_status": updated["validation"]["status"]},
        )

    # -- internals ----------------------------------------------------------

    @staticmethod
    def _require_actor(actor: str) -> None:
        if not isinstance(actor, str) or not actor.strip():
            raise DataEngineError("actor is required for every governed write")

    def _append_version(
        self,
        event: str,
        record_id: str,
        actor: str,
        updated: dict[str, Any],
        detail: dict[str, Any],
    ) -> Receipt:
        self.validator.validate(updated)
        detail = dict(detail)
        detail["supersedes_entry"] = self._head_entry[record_id]
        entry = self._append(event, record_id, actor, record=updated, detail=detail)
        return Receipt(
            outcome="transitioned",
            record_id=record_id,
            event=event,
            entry_id=entry["entry_id"],
            entry_hash=entry["entry_hash"],
            detail=entry["detail"],
        )

    def _append(
        self,
        event: str,
        record_id: str,
        actor: str,
        *,
        record: dict[str, Any] | None,
        detail: dict[str, Any],
    ) -> dict[str, Any]:
        if event not in EVENTS:
            raise DataEngineError(f"unknown event {event!r}")
        sequence = self.sequence + 1
        entry: dict[str, Any] = {
            "schema": LEDGER_ENTRY_SCHEMA,
            "entry_id": f"mze-{sequence:08d}",
            "sequence": sequence,
            "event": event,
            "record_id": record_id,
            "actor": actor,
            "at": _iso(self.clock()),
            "prev_hash": self._head_hash,
            "record": record,
            "detail": detail,
        }
        entry["entry_hash"] = _entry_hash(entry)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(canonical_json(entry) + "\n")
        self._apply(entry)
        return deepcopy(entry)

    def _apply(self, entry: dict[str, Any]) -> None:
        self._entries.append(entry)
        self._head_hash = entry["entry_hash"]
        record = entry.get("record")
        if record is not None:
            self._heads[entry["record_id"]] = record
            self._head_entry[entry["record_id"]] = entry["entry_id"]
            if entry["event"] == EVENT_RECORD_ADMITTED:
                self._payload_hashes[entry["record_id"]] = entry["detail"]["payload_hash"]

    def _replay(self) -> None:
        with self.ledger_path.open("r", encoding="utf-8") as handle:
            for line_no, raw in enumerate(handle, start=1):
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    entry = json.loads(raw)
                except json.JSONDecodeError as exc:
                    raise LedgerIntegrityError(f"line {line_no} is not JSON: {exc}") from exc
                if not isinstance(entry, dict) or entry.get("schema") != LEDGER_ENTRY_SCHEMA:
                    raise LedgerIntegrityError(f"line {line_no} is not a {LEDGER_ENTRY_SCHEMA} entry")
                if entry.get("event") not in EVENTS:
                    raise LedgerIntegrityError(f"line {line_no} carries unknown event {entry.get('event')!r}")
                if entry.get("record") is not None:
                    errors = self.validator.errors(entry["record"])
                    if errors:
                        raise LedgerIntegrityError(f"line {line_no} record violates schema: {errors[0]}")
                self._apply(entry)
        self.verify_chain()


def load_fixture_records(path: Path | str) -> list[dict[str, Any]]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, Mapping) or not isinstance(value.get("records"), list):
        raise ValueError(f"fixture file must be an object with a 'records' list: {path}")
    return [deepcopy(item) for item in value["records"]]


__all__ = [
    "DataEngineError",
    "EVIDENCE_CLASSES",
    "EVIDENCE_CLASS_TRANSITIONS",
    "GENESIS_HASH",
    "LEDGER_ENTRY_SCHEMA",
    "LedgerIntegrityError",
    "LinguisticRecordStore",
    "Receipt",
    "SchemaValidator",
    "SchemaViolation",
    "TransitionRefused",
    "VALIDATION_STATUSES",
    "VALIDATION_TRANSITIONS",
    "canonical_json",
    "load_fixture_records",
    "record_validator",
    "sha256_hex",
]
