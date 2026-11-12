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
        hmac_key=HMAC_KEY,
    )

    ctx_file = tmp_path / "hook_context.json"
    ctx_file.write_text(
        json.dumps(
            {
                "hmac_key_hex": HMAC_KEY.hex(),
                "key_id": "k1",
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


def test_pretooluse_denies_write_outside_allowed_roots(monkeypatch):
    """Verifier finding: writes outside the workspace must be denied before side effects."""
    import json
    import subprocess
    import sys

    repo_root = Path(__file__).resolve().parents[1]
    gate = repo_root / "scripts" / "kpgs_pretooluse_gate.py"

    def run(target: str) -> dict:
        payload = {"toolCall": {"name": "write_to_file", "args": {"TargetFile": target}}}
        proc = subprocess.run(
            [sys.executable, str(gate), "--event", "pre-tool-use"],
            input=json.dumps(payload), capture_output=True, text=True, check=True,
        )
        return json.loads(proc.stdout)

    for outside_target in (
        str(repo_root.parent / "outside.txt"),
        r"C:\Windows\System32\outside.txt",
        "/etc/outside.txt",
    ):
        outside = run(outside_target)
        assert outside["decision"] == "deny" and outside["permissionDecision"] == "deny"

    # Also verify foreign Windows drive/UNC syntax is denied when running on POSIX.
    spec = importlib.util.spec_from_file_location("kpgs_pretooluse_gate_test", gate)
    assert spec is not None and spec.loader is not None
    gate_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate_mod)
    monkeypatch.setattr(gate_mod.os, "name", "posix")
    assert gate_mod._path_in_allowed_roots(r"C:\Windows\System32\outside.txt") is False
    assert gate_mod._path_in_allowed_roots(r"\\server\share\outside.txt") is False

    inside = run(str(repo_root / "allowed.txt"))
    assert inside["decision"] == "allow" and inside["permissionDecision"] == "allow"
