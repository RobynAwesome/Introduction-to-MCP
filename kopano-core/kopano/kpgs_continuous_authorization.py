"""
KPGS Continuous Behavioural Authorization Gate
================================================

Doctrine:
    Identity establishes provenance.
    Behaviour earns continued authority.

This module is a deterministic, pre-actuation governance gate. It does not
perform computer use and it does not trust an authenticated identity as proof
that the current behaviour is authorized.

I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional, Sequence


class AuthorizationVerdict(str, Enum):
    ALLOW = "ALLOW"
    CONTAIN = "CONTAIN"
    REVOKE = "REVOKE"


class CompromiseClass(str, Enum):
    NONE = "NONE"
    IMPERSONATION = "IMPERSONATION"
    BEHAVIOURAL_COMPROMISE = "BEHAVIOURAL_COMPROMISE"
    GOVERNANCE_BLOCK = "GOVERNANCE_BLOCK"
    UNKNOWN = "UNKNOWN"


class RevokeScope(str, Enum):
    NONE = "NONE"
    LEASE = "LEASE"
    SESSION = "SESSION"


@dataclass(frozen=True)
class BehaviourObservation:
    """Observable facts used to re-authorize one proposed action."""

    session_id: str
    identity_authenticated: bool
    observed_action: str
    observed_target: str
    instruction_provenance: Sequence[str] = field(default_factory=tuple)
    context_provenance: Sequence[str] = field(default_factory=tuple)
    observed_state_changes: Sequence[str] = field(default_factory=tuple)
    cross_session_write: bool = False
    spawn_subagent: bool = False
    credential_access: bool = False
    privilege_change: bool = False
    unrelated_resource_access: bool = False
    anomaly_signals: Sequence[str] = field(default_factory=tuple)
    observed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class AuthorizationDecision:
    decision_id: str
    verdict: AuthorizationVerdict
    compromise_class: CompromiseClass
    revoke_scope: RevokeScope
    actor_id: str
    intent_id: str
    session_id: str
    reason_codes: list[str]
    trust_vector: dict[str, bool]
    continued_authority: bool
    mutation_allowed: bool
    observer_seat: str = "SEAT_01_KC"
    teacher_seat: str = "SEAT_02_CASSEY"
    previous_receipt_hash: Optional[str] = None
    receipt_hash: str = ""

    def _hash_payload(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "verdict": self.verdict.value,
            "compromise_class": self.compromise_class.value,
            "revoke_scope": self.revoke_scope.value,
            "actor_id": self.actor_id,
            "intent_id": self.intent_id,
            "session_id": self.session_id,
            "reason_codes": self.reason_codes,
            "trust_vector": self.trust_vector,
            "continued_authority": self.continued_authority,
            "mutation_allowed": self.mutation_allowed,
            "observer_seat": self.observer_seat,
            "teacher_seat": self.teacher_seat,
            "previous_receipt_hash": self.previous_receipt_hash,
        }

    def compute_hash(self) -> str:
        raw = json.dumps(self._hash_payload(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def seal(self) -> "AuthorizationDecision":
        self.receipt_hash = self.compute_hash()
        return self

    def to_dict(self) -> dict[str, Any]:
        out = self._hash_payload()
        out["receipt_hash"] = self.receipt_hash or self.compute_hash()
        return out


def _parse_time(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


class ContinuousBehaviouralAuthorizer:
    """
    Re-authorize every action against identity, authority, intent, provenance,
    state, behaviour and time.

    There is deliberately no aggregate trust score: a failed invariant cannot
    be averaged away by stronger signals elsewhere.
    """

    SENSITIVE_CLASSES = {"C2_MATERIAL", "C3_DESTRUCTIVE"}
    MUTATING_CLASSES = {"C1_REVERSIBLE", "C2_MATERIAL", "C3_DESTRUCTIVE"}
    NON_EXECUTOR_ACTORS = {"kc", "cassey"}
    EXPECTED_AUTHORITY_PATH = {
        "C0_READ": "AUTO",
        "C1_REVERSIBLE": "AUTO_LEASE",
        "C2_MATERIAL": "HUMAN_APPROVAL_REQUIRED",
        "C3_DESTRUCTIVE": "HUMAN_APPROVAL_REQUIRED",
        "CX_UNKNOWN": "BLOCKED",
    }

    def __init__(self, *, non_executor_actors: Optional[set[str]] = None):
        self.non_executor_actors = {
            x.lower() for x in (non_executor_actors or self.NON_EXECUTOR_ACTORS)
        }

    def evaluate(
        self,
        envelope: Mapping[str, Any],
        lease: Optional[Mapping[str, Any]],
        observation: BehaviourObservation,
        *,
        approval_state: str = "NOT_REQUIRED",
        previous_receipt_hash: Optional[str] = None,
    ) -> AuthorizationDecision:
        actor_id = str(envelope.get("actor_id", ""))
        intent_id = str(envelope.get("intent_id", ""))
        classification = str(envelope.get("classification", "CX_UNKNOWN"))
        reasons: list[str] = []

        trust = {
            "identity": bool(observation.identity_authenticated),
            "authority": True,
            "intent": True,
            "provenance": True,
            "state": True,
            "behaviour": True,
            "temporal": True,
        }

        # Identity proves who is present, not whether current behaviour is valid.
        if not observation.identity_authenticated:
            trust["identity"] = False
            reasons.append("IDENTITY_AUTHENTICATION_FAILED")
            return self._decision(
                actor_id, intent_id, observation, reasons, trust,
                AuthorizationVerdict.REVOKE, CompromiseClass.IMPERSONATION,
                RevokeScope.SESSION, previous_receipt_hash,
            )

        # KC watches/saves and Cassey teaches; neither receives mutation authority.
        if actor_id.lower() in self.non_executor_actors and classification in self.MUTATING_CLASSES:
            trust["authority"] = False
            reasons.append("ROLE_BOUNDARY_NON_EXECUTOR_MUTATION")
            return self._decision(
                actor_id, intent_id, observation, reasons, trust,
                AuthorizationVerdict.CONTAIN, CompromiseClass.GOVERNANCE_BLOCK,
                RevokeScope.NONE, previous_receipt_hash,
            )

        if not bool(envelope.get("allowlist_hit", False)):
            trust["authority"] = False
            reasons.append("ALLOWLIST_MISS")

        if classification == "CX_UNKNOWN":
            trust["authority"] = False
            reasons.append("UNKNOWN_CONSEQUENCE_CLASS")

        expected_authority = self.EXPECTED_AUTHORITY_PATH.get(classification)
        if expected_authority is None:
            trust["authority"] = False
            reasons.append("UNRECOGNIZED_CONSEQUENCE_CLASS")
        elif str(envelope.get("authority_path", "")) != expected_authority:
            trust["authority"] = False
            reasons.append("AUTHORITY_PATH_CLASS_MISMATCH")

        if str(envelope.get("requested_action", "")) != observation.observed_action:
            trust["behaviour"] = False
            reasons.append("OBSERVED_ACTION_DRIFT")

        if str(envelope.get("target", "")) != observation.observed_target:
            trust["behaviour"] = False
            reasons.append("OBSERVED_TARGET_DRIFT")

        if not observation.instruction_provenance or not observation.context_provenance:
            trust["provenance"] = False
            reasons.append("PROVENANCE_GAP")

        declared_effects = {str(x) for x in (envelope.get("declared_effects") or [])}
        observed_effects = {str(x) for x in observation.observed_state_changes}
        undeclared = observed_effects - declared_effects
        if undeclared:
            trust["state"] = False
            reasons.append("UNDECLARED_STATE_TRANSITION")

        if observation.cross_session_write:
            trust["temporal"] = False
            reasons.append("UNAUTHORIZED_CROSS_SESSION_PERSISTENCE")

        if observation.unrelated_resource_access:
            trust["behaviour"] = False
            reasons.append("UNRELATED_RESOURCE_ACCESS")

        # These are severe because they can expand authority beyond the lease.
        severe_behaviour = False
        if observation.spawn_subagent:
            trust["behaviour"] = False
            reasons.append("UNAUTHORIZED_SUBAGENT_SPAWN")
            severe_behaviour = True
        if observation.credential_access:
            trust["behaviour"] = False
            reasons.append("CREDENTIAL_BOUNDARY_TOUCH")
            severe_behaviour = True
        if observation.privilege_change:
            trust["behaviour"] = False
            reasons.append("PRIVILEGE_BOUNDARY_CHANGE")
            severe_behaviour = True
        if observation.anomaly_signals:
            trust["behaviour"] = False
            reasons.append("BEHAVIOURAL_ANOMALY_SIGNAL")

        # C0 reads may be AUTO with no lease; mutations require a scoped lease.
        if classification != "C0_READ":
            if lease is None:
                trust["authority"] = False
                reasons.append("LEASE_REQUIRED")
            else:
                self._check_lease(envelope, lease, observation, trust, reasons)
        elif lease is not None:
            self._check_lease(envelope, lease, observation, trust, reasons)

        # Sensitive classes require a distinct approval boundary.
        if classification in self.SENSITIVE_CLASSES:
            if approval_state != "APPROVED":
                trust["authority"] = False
                reasons.append("HUMAN_APPROVAL_NOT_APPROVED")
            if not lease or not str(lease.get("approval_receipt") or ""):
                trust["authority"] = False
                reasons.append("APPROVAL_RECEIPT_MISSING")

        # Identity can remain valid while behaviour independently loses authority.
        if severe_behaviour:
            return self._decision(
                actor_id, intent_id, observation, reasons, trust,
                AuthorizationVerdict.REVOKE, CompromiseClass.BEHAVIOURAL_COMPROMISE,
                RevokeScope.LEASE, previous_receipt_hash,
            )

        behavioural_reasons = {
            "OBSERVED_ACTION_DRIFT",
            "OBSERVED_TARGET_DRIFT",
            "UNDECLARED_STATE_TRANSITION",
            "UNAUTHORIZED_CROSS_SESSION_PERSISTENCE",
            "UNRELATED_RESOURCE_ACCESS",
            "BEHAVIOURAL_ANOMALY_SIGNAL",
        }
        behavioural_drift = any(reason in behavioural_reasons for reason in reasons)
        if behavioural_drift:
            return self._decision(
                actor_id, intent_id, observation, reasons, trust,
                AuthorizationVerdict.CONTAIN, CompromiseClass.BEHAVIOURAL_COMPROMISE,
                RevokeScope.NONE, previous_receipt_hash,
            )

        if not all(trust.values()):
            compromise = (
                CompromiseClass.UNKNOWN
                if not trust["provenance"]
                else CompromiseClass.GOVERNANCE_BLOCK
            )
            return self._decision(
                actor_id, intent_id, observation, reasons, trust,
                AuthorizationVerdict.CONTAIN, compromise,
                RevokeScope.NONE, previous_receipt_hash,
            )

        return self._decision(
            actor_id, intent_id, observation, ["CONTINUOUS_AUTHORIZATION_PASS"], trust,
            AuthorizationVerdict.ALLOW, CompromiseClass.NONE, RevokeScope.NONE,
            previous_receipt_hash,
        )

    def _check_lease(
        self,
        envelope: Mapping[str, Any],
        lease: Mapping[str, Any],
        observation: BehaviourObservation,
        trust: dict[str, bool],
        reasons: list[str],
    ) -> None:
        bindings = (
            ("actor_id", "actor_id", "LEASE_ACTOR_MISMATCH"),
            ("intent_id", "intent_id", "LEASE_INTENT_MISMATCH"),
            ("surface", "surface", "LEASE_SURFACE_MISMATCH"),
            ("requested_action", "allowed_action", "LEASE_ACTION_MISMATCH"),
            ("target", "allowed_target", "LEASE_TARGET_MISMATCH"),
        )
        for envelope_key, lease_key, reason in bindings:
            if str(envelope.get(envelope_key, "")) != str(lease.get(lease_key, "")):
                trust["authority"] = False
                reasons.append(reason)

        if str(lease.get("classification", "")) != str(envelope.get("classification", "")):
            trust["authority"] = False
            reasons.append("LEASE_CLASSIFICATION_MISMATCH")

        if lease.get("revocable") is not True:
            trust["authority"] = False
            reasons.append("LEASE_NOT_REVOCABLE")

        used = int(lease.get("invocations_used", 0))
        maximum = int(lease.get("max_invocations", 0))
        if maximum < 1 or used >= maximum:
            trust["temporal"] = False
            reasons.append("LEASE_EXHAUSTED")

        try:
            observed_at = _parse_time(observation.observed_at)
            issued_at = _parse_time(str(lease.get("issued_at", "")))
            expires_at = _parse_time(str(lease.get("expires_at", "")))
            if observed_at < issued_at:
                trust["temporal"] = False
                reasons.append("LEASE_NOT_YET_VALID")
            if observed_at >= expires_at:
                trust["temporal"] = False
                reasons.append("LEASE_EXPIRED")
        except (TypeError, ValueError):
            trust["temporal"] = False
            reasons.append("LEASE_TIME_INVALID")

    @staticmethod
    def _decision(
        actor_id: str,
        intent_id: str,
        observation: BehaviourObservation,
        reasons: list[str],
        trust: dict[str, bool],
        verdict: AuthorizationVerdict,
        compromise: CompromiseClass,
        revoke_scope: RevokeScope,
        previous_receipt_hash: Optional[str],
    ) -> AuthorizationDecision:
        seed = {
            "actor": actor_id,
            "intent": intent_id,
            "session": observation.session_id,
            "observed_at": observation.observed_at,
            "reasons": reasons,
            "previous_receipt_hash": previous_receipt_hash,
        }
        raw = json.dumps(seed, sort_keys=True, separators=(",", ":"))
        decision_id = f"cba:{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]}"
        return AuthorizationDecision(
            decision_id=decision_id,
            verdict=verdict,
            compromise_class=compromise,
            revoke_scope=revoke_scope,
            actor_id=actor_id,
            intent_id=intent_id,
            session_id=observation.session_id,
            reason_codes=reasons,
            trust_vector=trust,
            continued_authority=verdict is AuthorizationVerdict.ALLOW,
            mutation_allowed=verdict is AuthorizationVerdict.ALLOW,
            previous_receipt_hash=previous_receipt_hash,
        ).seal()


def kc_watch_receipt(decision: AuthorizationDecision) -> dict[str, Any]:
    """KC Save|Watch receipt. This function never grants execution authority."""
    return {
        "seat": "SEAT_01_KC",
        "mode": "SAVE|WATCH",
        "decision_id": decision.decision_id,
        "verdict": decision.verdict.value,
        "receipt_hash": decision.receipt_hash,
        "mutation_authority": False,
        "attention_required": decision.verdict is not AuthorizationVerdict.ALLOW,
    }


def cassey_teacher_review(
    decision: AuthorizationDecision,
    *,
    approved: bool,
    note: str = "",
) -> dict[str, Any]:
    """
    Cassey review receipt. Teacher approval records review; it cannot override a
    CONTAIN/REVOKE decision or convert an invalid lease into authority.
    """
    effective = "APPROVED" if approved and decision.verdict is AuthorizationVerdict.ALLOW else "HOLD"
    return {
        "seat": "SEAT_02_CASSEY",
        "mode": "TEACHER_REVIEW",
        "decision_id": decision.decision_id,
        "review": "APPROVE" if approved else "DENY",
        "effective_outcome": effective,
        "policy_override": False,
        "note": note,
        "mutation_authority": False,
    }
