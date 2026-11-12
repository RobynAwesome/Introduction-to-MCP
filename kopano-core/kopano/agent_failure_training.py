from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Iterable, Mapping, Any


class FailureClass(str, Enum):
    """Canonical KPGS/MMAO failure classes."""

    FOC_M01_IMPORT_FABRICATION = "FOC-M01"
    FOC_M02_SIGNATURE_FABRICATION = "FOC-M02"
    FOC_M03_VALIDATION_THEATER = "FOC-M03"
    FOC_R01_SOURCE_HALLUCINATION = "FOC-R01"
    FOC_R02_UNSUPPORTED_FACT_PROMOTION = "FOC-R02"
    FOC_R03_SYCOPHANCY = "FOC-R03"
    FOC_R04_PERSONA_DRIFT = "FOC-R04"
    FOC_R05_DELUSION_REINFORCEMENT = "FOC-R05"
    FOC_R06_MEMORY_CONTAMINATION = "FOC-R06"
    FOC_R07_AUTHORITY_ESCALATION = "FOC-R07"
    FOC_R08_UNAUTHORIZED_TOOL_ACTION = "FOC-R08"
    FOC_R09_CONTROL_RUNTIME_MISMATCH = "FOC-R09"
    FOC_R10_FABRICATED_EXECUTION_EVIDENCE = "FOC-R10"


class KCDecision(str, Enum):
    SAVE = "SAVE"
    WATCH = "WATCH"
    KILL = "KILL"


class ReplayStatus(str, Enum):
    NOT_RUN = "NOT_RUN"
    PASS = "PASS"
    FAIL = "FAIL"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def hash_prompt_context(prompt_context: str) -> str:
    return hashlib.sha256(prompt_context.encode("utf-8")).hexdigest()


def normalize_failure_classes(values: Iterable[str | FailureClass]) -> list[str]:
    normalized: list[str] = []
    valid = {item.value for item in FailureClass}
    for value in values:
        candidate = value.value if isinstance(value, FailureClass) else str(value)
        if candidate not in valid:
            raise ValueError(f"Unknown failure class: {candidate}")
        if candidate not in normalized:
            normalized.append(candidate)
    if not normalized:
        raise ValueError("At least one failure class is required")
    return normalized


@dataclass(frozen=True)
class FailureReceipt:
    """
    Immutable execution receipt.

    The learner may propose a correction, but promotion metadata is deliberately
    excluded. Promotion is a separate governed decision.
    """

    receipt_id: str
    occurred_at: str
    agent_id: str
    model_provider: str
    model_name: str
    model_version: str | None
    prompt_context_sha256: str
    prompt_context_ref: str | None
    prompt_context_redacted: str | None
    system_controls_expected: tuple[str, ...]
    actual_output: str
    violated_governance_rules: tuple[str, ...]
    failure_classes: tuple[str, ...]
    downstream_effects: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    correction_candidate: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema"] = "kpgs_agent_failure_receipt_v1"
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)


@dataclass(frozen=True)
class PromotionDecision:
    receipt_id: str
    student_agent_id: str
    teacher_agent_id: str
    kc_agent_id: str
    teacher_reviewed: bool
    blackmask_passed: bool
    replay_status: ReplayStatus
    kc_decision: KCDecision
    promoted: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["replay_status"] = self.replay_status.value
        payload["kc_decision"] = self.kc_decision.value
        payload["schema"] = "kpgs_agent_failure_promotion_v1"
        return payload


def build_failure_receipt(
    *,
    receipt_id: str,
    agent_id: str,
    model_provider: str,
    model_name: str,
    prompt_context: str,
    system_controls_expected: Iterable[str],
    actual_output: str,
    violated_governance_rules: Iterable[str],
    failure_classes: Iterable[str | FailureClass],
    downstream_effects: Iterable[str] = (),
    evidence_refs: Iterable[str] = (),
    model_version: str | None = None,
    prompt_context_ref: str | None = None,
    prompt_context_redacted: str | None = None,
    correction_candidate: str | None = None,
    occurred_at: str | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> FailureReceipt:
    if not receipt_id.strip():
        raise ValueError("receipt_id is required")
    if not agent_id.strip():
        raise ValueError("agent_id is required")
    controls = tuple(str(x).strip() for x in system_controls_expected if str(x).strip())
    rules = tuple(str(x).strip() for x in violated_governance_rules if str(x).strip())
    if not controls:
        raise ValueError("system_controls_expected must not be empty")
    if not rules:
        raise ValueError("violated_governance_rules must not be empty")

    return FailureReceipt(
        receipt_id=receipt_id.strip(),
        occurred_at=occurred_at or utc_now(),
        agent_id=agent_id.strip(),
        model_provider=model_provider.strip(),
        model_name=model_name.strip(),
        model_version=model_version.strip() if model_version else None,
        prompt_context_sha256=hash_prompt_context(prompt_context),
        prompt_context_ref=prompt_context_ref,
        prompt_context_redacted=prompt_context_redacted,
        system_controls_expected=controls,
        actual_output=actual_output,
        violated_governance_rules=rules,
        failure_classes=tuple(normalize_failure_classes(failure_classes)),
        downstream_effects=tuple(str(x) for x in downstream_effects),
        evidence_refs=tuple(str(x) for x in evidence_refs),
        correction_candidate=correction_candidate,
        metadata=dict(metadata or {}),
    )


def decide_promotion(
    *,
    receipt: FailureReceipt,
    student_agent_id: str,
    teacher_agent_id: str,
    kc_agent_id: str,
    teacher_reviewed: bool,
    blackmask_passed: bool,
    replay_status: ReplayStatus | str,
    kc_decision: KCDecision | str,
) -> PromotionDecision:
    """
    Decide whether a correction may be promoted into learned state.

    Invariants:
    - student, teacher, and KC/ledger identities must be distinct;
    - the student cannot promote itself;
    - promotion requires teacher review, BlackMask pass, replay pass, and KC SAVE.
    """
    if len({student_agent_id, teacher_agent_id, kc_agent_id}) != 3:
        raise ValueError("student, teacher, and KC identities must be distinct")

    replay = replay_status if isinstance(replay_status, ReplayStatus) else ReplayStatus(str(replay_status))
    decision = kc_decision if isinstance(kc_decision, KCDecision) else KCDecision(str(kc_decision))

    gates = {
        "teacher_reviewed": bool(teacher_reviewed),
        "blackmask_passed": bool(blackmask_passed),
        "replay_passed": replay is ReplayStatus.PASS,
        "kc_save": decision is KCDecision.SAVE,
    }
    promoted = all(gates.values())
    failed = [name for name, passed in gates.items() if not passed]
    reason = "all promotion gates passed" if promoted else "blocked: " + ", ".join(failed)

    return PromotionDecision(
        receipt_id=receipt.receipt_id,
        student_agent_id=student_agent_id,
        teacher_agent_id=teacher_agent_id,
        kc_agent_id=kc_agent_id,
        teacher_reviewed=bool(teacher_reviewed),
        blackmask_passed=bool(blackmask_passed),
        replay_status=replay,
        kc_decision=decision,
        promoted=promoted,
        reason=reason,
    )


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    record: dict[str, Any] = {}
    for key, value in pairs:
        if key in record:
            raise ValueError(f"restriction_ledger_tampered: duplicate JSON key {key!r}")
        record[key] = value
    return record


def _canonical_entry_bytes(entry: Mapping[str, Any]) -> bytes:
    filtered = {k: v for k, v in entry.items() if k not in {"entry_sha256", "hmac_sha256"}}
    return json.dumps(filtered, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def observe_failure_receipt(receipt: FailureReceipt, *, ledger_path: Path) -> dict[str, Any]:
    """Stage 1: Record an unreviewed failure observation ONLY.

    Does NOT revoke leases or restrict capabilities.
    """
    row = {
        "schema": "kpgs_observed_failure_v1",
        "status": "OBSERVED",
        "observed_at": utc_now(),
        "receipt": receipt.to_dict(),
    }
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
    return row


def verify_restriction_ledger(
    ledger_path: Path,
    *,
    hmac_key: bytes,
) -> list[dict[str, Any]]:
    """Verify hash-chain and HMAC-SHA256 integrity of the authorised restrictions ledger."""
    if not ledger_path.is_file():
        return []
    entries: list[dict[str, Any]] = []
    prev_hash = "GENESIS"
    raw_lines = ledger_path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(raw_lines):
        if not line.strip():
            continue
        try:
            row = json.loads(line, object_pairs_hook=_reject_duplicate_json_keys)
        except Exception as exc:
            raise ValueError(f"restriction_ledger_tampered at line {idx + 1}: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"restriction_ledger_tampered at line {idx + 1}: non-object entry")
        if row.get("prev_entry_sha256") != prev_hash:
            raise ValueError(f"restriction_ledger_tampered at line {idx + 1}: broken hash chain")
        canonical = _canonical_entry_bytes(row)
        expected_sha = hashlib.sha256(canonical).hexdigest()
        expected_hmac = hmac.new(hmac_key, canonical, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(str(row.get("entry_sha256", "")), expected_sha):
            raise ValueError(f"restriction_ledger_tampered at line {idx + 1}: entry_sha256 mismatch")
        if not hmac.compare_digest(str(row.get("hmac_sha256", "")), expected_hmac):
            raise ValueError(f"restriction_ledger_tampered at line {idx + 1}: hmac_sha256 mismatch")
        prev_hash = expected_sha
        entries.append(row)
    return entries


def _append_signed_restriction_entry(
    ledger_path: Path,
    entry: dict[str, Any],
    *,
    hmac_key: bytes,
) -> dict[str, Any]:
    existing = verify_restriction_ledger(ledger_path, hmac_key=hmac_key)
    prev_hash = existing[-1]["entry_sha256"] if existing else "GENESIS"
    unsigned = {**entry, "prev_entry_sha256": prev_hash}
    canonical = _canonical_entry_bytes(unsigned)
    entry_sha = hashlib.sha256(canonical).hexdigest()
    entry_hmac = hmac.new(hmac_key, canonical, hashlib.sha256).hexdigest()
    signed = {
        **unsigned,
        "entry_sha256": entry_sha,
        "hmac_sha256": entry_hmac,
    }
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(signed, sort_keys=True, ensure_ascii=False) + "\n")
    return signed


def record_authorised_restriction(
    *,
    receipt: FailureReceipt,
    auth_decision: Any,
    kc_watch: Mapping[str, Any],
    teacher_review: Mapping[str, Any],
    validator_id: str,
    domain_id: str,
    capabilities: Iterable[str],
    ledger_path: Path,
    hmac_key: bytes,
) -> dict[str, Any]:
    """Stage 2 & 3: Record an independently validated restriction in the tamper-evident ledger."""
    if not validator_id.strip():
        raise ValueError("validator_id is required")
    if validator_id.strip() == receipt.agent_id.strip():
        raise PermissionError("Self-validation is forbidden; validator_id must differ from failing agent_id")

    verdict_val = getattr(auth_decision.verdict, "value", str(auth_decision.verdict))
    if verdict_val not in {"CONTAIN", "REVOKE"}:
        raise ValueError(f"AuthorizationDecision verdict {verdict_val!r} does not authorise a restriction")

    decision_id = str(getattr(auth_decision, "decision_id", ""))
    if not decision_id or kc_watch.get("decision_id") != decision_id or teacher_review.get("decision_id") != decision_id:
        raise PermissionError("Synthetic or mismatched KC/Teacher validation receipts rejected")
    if kc_watch.get("seat") != "SEAT_01_KC" or kc_watch.get("mutation_authority") is not False:
        raise PermissionError("Invalid KC watch receipt envelope")
    if teacher_review.get("seat") != "SEAT_02_CASSEY" or teacher_review.get("policy_override") is not False:
        raise PermissionError("Invalid or policy-overriding Teacher review receipt rejected")

    cap_list = [str(c).strip() for c in capabilities if str(c).strip()]
    if not cap_list:
        raise ValueError("At least one restricted capability is required")

    entry = {
        "schema": "kpgs_authorised_restriction_v1",
        "status": "RESTRICTED",
        "recorded_at": utc_now(),
        "receipt_id": receipt.receipt_id,
        "subject_id": receipt.agent_id,
        "validator_id": validator_id.strip(),
        "domain_id": domain_id.strip(),
        "capabilities": cap_list,
        "verdict": verdict_val,
        "decision_id": decision_id,
        "kc_watch_mode": kc_watch.get("mode"),
        "teacher_effective_outcome": teacher_review.get("effective_outcome"),
    }
    return _append_signed_restriction_entry(ledger_path, entry, hmac_key=hmac_key)


def lift_restriction_on_promotion(
    *,
    receipt: FailureReceipt,
    promotion: PromotionDecision,
    blackmask_result: Mapping[str, Any],
    teacher_review: Mapping[str, Any],
    kc_watch: Mapping[str, Any],
    ledger_path: Path,
    hmac_key: bytes,
) -> dict[str, Any]:
    """Stage 5: Lift an active restriction only after verified 3-seat promotion and explicit BlackMask drill."""
    if promotion.receipt_id != receipt.receipt_id:
        raise ValueError("PromotionDecision receipt_id does not match FailureReceipt")
    if not promotion.promoted:
        raise PermissionError(f"Cannot lift restriction: {promotion.reason}")
    if len({promotion.student_agent_id, promotion.teacher_agent_id, promotion.kc_agent_id}) != 3:
        raise PermissionError("3-seat separation required for restriction lift")
    if blackmask_result.get("verdict") != "SHIP" or blackmask_result.get("explicit_ack_verified") is not True:
        raise PermissionError(
            "BlackMask explicit 15-commandment + 5-pillar acknowledgement required; default-ack false-green rejected"
        )
    if teacher_review.get("seat") != "SEAT_02_CASSEY" or teacher_review.get("effective_outcome") != "APPROVED" or teacher_review.get("policy_override") is not False:
        raise PermissionError("Valid Cassey teacher APPROVED review required")
    if kc_watch.get("seat") != "SEAT_01_KC" or kc_watch.get("verdict") != "ALLOW":
        raise PermissionError("Valid KC ALLOW watch receipt required")

    entry = {
        "schema": "kpgs_authorised_restriction_v1",
        "status": "RESTRICTION_LIFTED",
        "recorded_at": utc_now(),
        "receipt_id": receipt.receipt_id,
        "subject_id": receipt.agent_id,
        "student_agent_id": promotion.student_agent_id,
        "teacher_agent_id": promotion.teacher_agent_id,
        "kc_agent_id": promotion.kc_agent_id,
        "replay_status": promotion.replay_status.value,
        "kc_decision": promotion.kc_decision.value,
        "blackmask_explicit_ack_verified": True,
    }
    return _append_signed_restriction_entry(ledger_path, entry, hmac_key=hmac_key)

