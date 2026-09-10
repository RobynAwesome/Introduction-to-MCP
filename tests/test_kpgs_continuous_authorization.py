from datetime import datetime, timedelta, timezone

from kopano.kpgs_continuous_authorization import (
    AuthorizationVerdict,
    BehaviourObservation,
    CompromiseClass,
    ContinuousBehaviouralAuthorizer,
    RevokeScope,
    cassey_teacher_review,
    kc_watch_receipt,
)


NOW = datetime(2026, 9, 10, 14, 0, tzinfo=timezone.utc)


def iso(delta_seconds=0):
    return (NOW + timedelta(seconds=delta_seconds)).isoformat()


def c1_envelope(actor="cassy"):
    return {
        "intent_id": "intent-001",
        "actor_id": actor,
        "executor_seat": "CODEX",
        "surface": "windows",
        "requested_action": "ui.type_text",
        "target": "Notepad",
        "declared_effects": ["Notepad.text_changed"],
        "allowlist_hit": True,
        "reversibility": "local",
        "external_side_effect": False,
        "classification": "C1_REVERSIBLE",
        "authority_path": "AUTO_LEASE",
        "classifier_version": "v0",
        "submitted_at": iso(-5),
    }


def lease(actor="cassy", *, used=0):
    return {
        "lease_id": "lease-001",
        "intent_id": "intent-001",
        "actor_id": actor,
        "surface": "windows",
        "allowed_action": "ui.type_text",
        "allowed_target": "Notepad",
        "issued_at": iso(-10),
        "expires_at": iso(60),
        "max_invocations": 1,
        "invocations_used": used,
        "revocable": True,
        "classification": "C1_REVERSIBLE",
    }


def observation(**overrides):
    data = dict(
        session_id="session-001",
        identity_authenticated=True,
        observed_action="ui.type_text",
        observed_target="Notepad",
        instruction_provenance=("USER_INTENT:intent-001",),
        context_provenance=("NOW.md@40a31fe8",),
        observed_state_changes=("Notepad.text_changed",),
        observed_at=iso(),
    )
    data.update(overrides)
    return BehaviourObservation(**data)


def test_valid_identity_and_scoped_behavior_is_allowed():
    out = ContinuousBehaviouralAuthorizer().evaluate(c1_envelope(), lease(), observation())
    assert out.verdict == AuthorizationVerdict.ALLOW
    assert out.compromise_class == CompromiseClass.NONE
    assert out.continued_authority is True
    assert all(out.trust_vector.values())
    assert len(out.receipt_hash) == 64


def test_failed_identity_revokes_session_as_impersonation():
    out = ContinuousBehaviouralAuthorizer().evaluate(
        c1_envelope(), lease(), observation(identity_authenticated=False)
    )
    assert out.verdict == AuthorizationVerdict.REVOKE
    assert out.compromise_class == CompromiseClass.IMPERSONATION
    assert out.revoke_scope == RevokeScope.SESSION
    assert out.mutation_allowed is False


def test_legitimate_identity_with_action_drift_is_contained():
    out = ContinuousBehaviouralAuthorizer().evaluate(
        c1_envelope(), lease(), observation(observed_action="ui.delete_file")
    )
    assert out.verdict == AuthorizationVerdict.CONTAIN
    assert out.compromise_class == CompromiseClass.BEHAVIOURAL_COMPROMISE
    assert "OBSERVED_ACTION_DRIFT" in out.reason_codes
    assert out.trust_vector["identity"] is True
    assert out.trust_vector["behaviour"] is False


def test_severe_behavioral_drift_revokes_only_current_lease():
    out = ContinuousBehaviouralAuthorizer().evaluate(
        c1_envelope(), lease(), observation(credential_access=True)
    )
    assert out.verdict == AuthorizationVerdict.REVOKE
    assert out.compromise_class == CompromiseClass.BEHAVIOURAL_COMPROMISE
    assert out.revoke_scope == RevokeScope.LEASE
    assert out.trust_vector["identity"] is True


def test_cross_session_persistence_is_contained():
    out = ContinuousBehaviouralAuthorizer().evaluate(
        c1_envelope(), lease(), observation(cross_session_write=True)
    )
    assert out.verdict == AuthorizationVerdict.CONTAIN
    assert "UNAUTHORIZED_CROSS_SESSION_PERSISTENCE" in out.reason_codes
    assert out.trust_vector["temporal"] is False


def test_exhausted_lease_does_not_inherit_continuing_authority():
    out = ContinuousBehaviouralAuthorizer().evaluate(c1_envelope(), lease(used=1), observation())
    assert out.verdict == AuthorizationVerdict.CONTAIN
    assert out.compromise_class == CompromiseClass.GOVERNANCE_BLOCK
    assert "LEASE_EXHAUSTED" in out.reason_codes
    assert out.continued_authority is False


def test_material_action_requires_separate_human_approval():
    env = c1_envelope()
    env["classification"] = "C2_MATERIAL"
    env["authority_path"] = "HUMAN_APPROVAL_REQUIRED"
    l = lease()
    l["classification"] = "C2_MATERIAL"
    out = ContinuousBehaviouralAuthorizer().evaluate(env, l, observation(), approval_state="PENDING")
    assert out.verdict == AuthorizationVerdict.CONTAIN
    assert out.compromise_class == CompromiseClass.GOVERNANCE_BLOCK
    assert "HUMAN_APPROVAL_NOT_APPROVED" in out.reason_codes
    assert "APPROVAL_RECEIPT_MISSING" in out.reason_codes


def test_kc_and_cassey_are_non_executor_roles_for_mutations():
    auth = ContinuousBehaviouralAuthorizer()
    for actor in ("kc", "cassey"):
        env = c1_envelope(actor=actor)
        l = lease(actor=actor)
        out = auth.evaluate(env, l, observation())
        assert out.verdict == AuthorizationVerdict.CONTAIN
        assert "ROLE_BOUNDARY_NON_EXECUTOR_MUTATION" in out.reason_codes


def test_kc_watch_and_cassey_review_cannot_override_policy():
    blocked = ContinuousBehaviouralAuthorizer().evaluate(
        c1_envelope(), lease(), observation(credential_access=True)
    )
    kc = kc_watch_receipt(blocked)
    teacher = cassey_teacher_review(blocked, approved=True, note="reviewed")

    assert kc["mutation_authority"] is False
    assert kc["attention_required"] is True
    assert teacher["review"] == "APPROVE"
    assert teacher["effective_outcome"] == "HOLD"
    assert teacher["policy_override"] is False


def test_receipts_chain_without_changing_policy_semantics():
    auth = ContinuousBehaviouralAuthorizer()
    first = auth.evaluate(c1_envelope(), lease(), observation())
    second = auth.evaluate(
        c1_envelope(),
        lease(),
        observation(observed_at=iso(1)),
        previous_receipt_hash=first.receipt_hash,
    )
    assert second.previous_receipt_hash == first.receipt_hash
    assert second.receipt_hash != first.receipt_hash
    assert second.verdict == AuthorizationVerdict.ALLOW
