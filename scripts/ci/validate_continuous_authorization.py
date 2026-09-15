#!/usr/bin/env python3
"""Run a dependency-free continuous authorization smoke proof."""

from datetime import datetime, timedelta, timezone

from kopano.kpgs_continuous_authorization import (
    AuthorizationVerdict,
    BehaviourObservation,
    ContinuousBehaviouralAuthorizer,
)


def main() -> None:
    now = datetime(2026, 9, 13, tzinfo=timezone.utc)
    iso = lambda delta=0: (now + timedelta(seconds=delta)).isoformat()
    envelope = {
        "intent_id": "intent-ci",
        "actor_id": "builder",
        "executor_seat": "CODEX",
        "surface": "ci",
        "requested_action": "artifact.write",
        "target": "receipt",
        "declared_effects": ["receipt.updated"],
        "allowlist_hit": True,
        "reversibility": "local",
        "external_side_effect": False,
        "classification": "C1_REVERSIBLE",
        "authority_path": "AUTO_LEASE",
        "classifier_version": "v0",
        "submitted_at": iso(-5),
    }
    lease = {
        "lease_id": "lease-ci",
        "intent_id": "intent-ci",
        "actor_id": "builder",
        "surface": "ci",
        "allowed_action": "artifact.write",
        "allowed_target": "receipt",
        "issued_at": iso(-10),
        "expires_at": iso(60),
        "max_invocations": 1,
        "invocations_used": 0,
        "revocable": True,
        "classification": "C1_REVERSIBLE",
    }

    def observe(**overrides):
        values = {
            "session_id": "session-ci",
            "identity_authenticated": True,
            "observed_action": "artifact.write",
            "observed_target": "receipt",
            "instruction_provenance": ("PR:exact-head",),
            "context_provenance": ("policy:zero-trust",),
            "observed_state_changes": ("receipt.updated",),
            "observed_at": iso(),
        }
        values.update(overrides)
        return BehaviourObservation(**values)

    authorizer = ContinuousBehaviouralAuthorizer()
    allowed = authorizer.evaluate(envelope, lease, observe())
    assert allowed.verdict == AuthorizationVerdict.ALLOW, allowed.reason_codes
    drifted = authorizer.evaluate(
        envelope, lease, observe(observed_action="artifact.delete", observed_state_changes=())
    )
    assert drifted.verdict == AuthorizationVerdict.CONTAIN, drifted.reason_codes
    revoked = authorizer.evaluate(envelope, lease, observe(credential_access=True))
    assert revoked.verdict == AuthorizationVerdict.REVOKE, revoked.reason_codes
    print("CONTINUOUS_AUTHORIZATION_PASS")


if __name__ == "__main__":
    main()
