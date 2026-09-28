"""Regression checks for KPGS renter ingress and consequential side effects."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano import (  # noqa: E402
    gsmb_poc,
    kc_phu_legacy_api,
    kpgs_activation_gate,
    kpgs_behavioral_poc,
    kpgs_renter_entry,
    operator_auth,
    sovereign_sim,
)
from kopano.api import app  # noqa: E402


def _admission_body(*, ack: str = kpgs_renter_entry.HOOD_ACK_LITERAL) -> dict:
    return {
        "renter_id": "cassy_test",
        "renter_class": "linguistic_actor",
        "hood_ack": ack,
        "ts": "2026-09-25T00:00:00Z",
    }


def _god_headers() -> dict[str, str]:
    token = operator_auth.create_session(
        {
            "id": 1,
            "email": "test-operator@local.invalid",
            "role": "admin",
            "god_mode": True,
            "is_active": True,
        }
    )
    return {"Authorization": f"Bearer {token}"}


def _eco_poc_body(*, ack: str = kpgs_renter_entry.HOOD_ACK_LITERAL) -> dict:
    return {
        **_admission_body(ack=ack),
        "agent_id": "cassy_test",
        "claim": "a bounded test claim",
        "model": "test-model",
    }


def test_missing_alp_blocks_all_traced_world_entrypoints_before_world_write(monkeypatch, tmp_path):
    world_path = tmp_path / "world.json"
    monkeypatch.setattr(kpgs_activation_gate, "_ALP_AVAILABLE", False)
    monkeypatch.setattr(kpgs_activation_gate, "GATE_REPORT_PATH", tmp_path / "gate.json")
    monkeypatch.setattr(sovereign_sim, "WORLD_STATE_PATH", world_path)
    monkeypatch.setattr(sovereign_sim, "SMOKE_REPORT_PATH", tmp_path / "smoke.json")
    monkeypatch.setattr(kpgs_behavioral_poc, "BEHAVIORAL_REPORT_PATH", tmp_path / "behavioral.json")
    monkeypatch.setattr(gsmb_poc, "POC_LOG", tmp_path / "gsmb.jsonl")

    assert sovereign_sim.bootstrap_sovereign_sim(write_log=False)["verdict"] == "BLOCKED"
    assert sovereign_sim.run_kpgs_smoke_poc()["verdict"] == "BLOCKED"
    assert kpgs_behavioral_poc.run_kpgs_behavioral_poc(write_report=True)["verdict"] == "BLOCKED"
    assert kpgs_behavioral_poc.run_sovereign_sim_tick(write_world=True)["verdict"] == "BLOCKED"
    assert gsmb_poc.run_gsmb_poc()["verdict"] == "BLOCKED"
    assert not world_path.exists()
    assert json.loads((tmp_path / "gsmb.jsonl").read_text(encoding="utf-8"))["verdict"] == "BLOCKED"


def test_api_status_routes_only_read_cached_or_source_state(monkeypatch, tmp_path):
    monkeypatch.setattr(kpgs_activation_gate, "GATE_REPORT_PATH", tmp_path / "missing-gate.json")
    monkeypatch.setattr(kpgs_behavioral_poc, "BEHAVIORAL_REPORT_PATH", tmp_path / "missing-behavior.json")
    monkeypatch.setattr(kc_phu_legacy_api, "compile_kpgs_governance", lambda **_: (_ for _ in ()).throw(AssertionError("compiled")))
    monkeypatch.setattr(kc_phu_legacy_api, "validate_spawn_swarm", lambda **_: (_ for _ in ()).throw(AssertionError("validated")))

    client = TestClient(app)
    assert client.get("/api/kc/phu/kpgs/gate").json()["verdict"] == "UNKNOWN"
    assert client.get("/api/kc/phu/kpgs/behavioral-poc").json()["verdict"] == "UNKNOWN"
    assert client.get("/api/kc/phu/kpgs/governance").json()["compile_verdict"] == "UNKNOWN"
    assert client.get("/api/kc/phu/kpgs/spawn/status").json()["schema"] == "kpgs_spawn_swarm_status_v2"
    assert not (tmp_path / "missing-gate.json").exists()
    assert not (tmp_path / "missing-behavior.json").exists()


def test_phu_boot_status_uses_source_snapshot_without_compiling_or_writing(monkeypatch, tmp_path):
    from kopano import kpgs_governance, phu_boot_governance

    state_path = tmp_path / "boot-state.json"
    monkeypatch.setattr(phu_boot_governance, "STATE_PATH", state_path)
    monkeypatch.setattr(
        kpgs_governance,
        "compile_kpgs_governance",
        lambda **_: (_ for _ in ()).throw(AssertionError("status compiled governance")),
    )

    result = phu_boot_governance.boot_status()

    assert result["kpgs_governance"]["source"] == "source_snapshot"
    assert result["kpgs_governance"]["compile_verdict"] == "UNKNOWN"
    assert not state_path.exists()


def test_kpgs_mesh_no_write_validation_skips_persistent_blackmask(monkeypatch, tmp_path):
    from kopano import kpgs_agent_validate, phu_apprenticeship, phu_boot_governance

    state_path = tmp_path / "apprenticeship.json"
    log_path = tmp_path / "main-brain.jsonl"
    report_path = REPO / ".pytest-no-write" / "mesh.json"
    monkeypatch.setattr(kpgs_agent_validate, "REPORT_PATH", report_path)
    monkeypatch.setattr(kpgs_agent_validate, "MAIN_BRAIN_LOG", log_path)
    monkeypatch.setattr(phu_boot_governance, "mesh_agent_ids", lambda: ["cassy"])
    monkeypatch.setattr(phu_apprenticeship, "STATE_PATH", state_path)
    monkeypatch.setattr(phu_apprenticeship, "MAIN_BRAIN_LOG", log_path)

    result = kpgs_agent_validate.validate_kpgs_mesh(write_report=False)

    assert result["agents_total"] == 1
    assert not report_path.exists()
    assert not log_path.exists()
    assert not state_path.exists()


def test_api_blocks_unadmitted_execution_before_operation(monkeypatch, tmp_path):
    entry_log = tmp_path / "entry.jsonl"
    monkeypatch.setattr(kpgs_renter_entry, "MAIN_BRAIN_LOG", entry_log)
    monkeypatch.setattr(kpgs_activation_gate, "_ALP_AVAILABLE", False)
    monkeypatch.setattr(kpgs_activation_gate, "GATE_REPORT_PATH", tmp_path / "gate.json")
    monkeypatch.setattr(sovereign_sim, "SMOKE_REPORT_PATH", tmp_path / "smoke.json")
    monkeypatch.setattr(sovereign_sim, "WORLD_STATE_PATH", tmp_path / "world.json")

    client = TestClient(app)
    path = "/api/kc/phu/kpgs/smoke-poc"
    assert client.post(path, json=_admission_body()).status_code == 401
    headers = _god_headers()
    assert client.post(path, json=_admission_body(ack="WRONG"), headers=headers).status_code == 422
    assert not entry_log.exists()
    assert not (tmp_path / "smoke.json").exists()

    response = client.post(path, json=_admission_body(), headers=headers)
    assert response.status_code == 200
    assert response.json()["hood_entry"]["ack_verified"] is True
    assert response.json()["hood_entry"]["operation"] == "kpgs_smoke_poc"
    assert response.json()["verdict"] == "BLOCKED"
    assert entry_log.exists()
    assert json.loads(entry_log.read_text(encoding="utf-8"))["operation"] == "kpgs_smoke_poc"
    assert not (tmp_path / "world.json").exists()


def test_consequential_phu_mutation_routes_require_operator_and_valid_renter_ack(monkeypatch, tmp_path):
    entry_log = tmp_path / "entry.jsonl"
    monkeypatch.setattr(kpgs_renter_entry, "MAIN_BRAIN_LOG", entry_log)
    monkeypatch.setattr(
        kc_phu_legacy_api,
        "validate_eco_poc",
        lambda **_: (_ for _ in ()).throw(AssertionError("PoC validation ran before admission")),
    )
    monkeypatch.setattr(
        kc_phu_legacy_api,
        "populate_main_brain",
        lambda **_: (_ for _ in ()).throw(AssertionError("Main Brain population ran before admission")),
    )
    monkeypatch.setattr(
        kc_phu_legacy_api,
        "reattach_detached_subbrains",
        lambda **_: (_ for _ in ()).throw(AssertionError("Sub-brains were reattached before admission")),
    )
    monkeypatch.setattr(
        kc_phu_legacy_api,
        "promote_all_flagships",
        lambda **_: (_ for _ in ()).throw(AssertionError("Operating mesh promoted before admission")),
    )
    monkeypatch.setattr(
        kc_phu_legacy_api,
        "promote_flagship",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("Flagship promoted before admission")),
    )
    monkeypatch.setattr(
        kc_phu_legacy_api,
        "record_steward_trust",
        lambda **_: (_ for _ in ()).throw(AssertionError("Steward trust recorded before admission")),
    )
    monkeypatch.setattr(
        kc_phu_legacy_api,
        "run_steward_lane_activate",
        lambda **_: (_ for _ in ()).throw(AssertionError("Steward lane activated before admission")),
    )
    monkeypatch.setattr(
        kc_phu_legacy_api,
        "apply_boot",
        lambda: (_ for _ in ()).throw(AssertionError("PHU boot applied before admission")),
    )
    client = TestClient(app)
    routes = [
        ("/api/kc/phu/poc/validate", _eco_poc_body()),
        ("/api/kc/phu/populate-main-brain", {**_admission_body(), "sync_vault_logs": False}),
        ("/api/kc/phu/reattach-subbrains", {**_admission_body(), "dry_run": True}),
        ("/api/kc/phu/operating-mesh/promote-all", _admission_body()),
        ("/api/kc/phu/operating-mesh/promote/subbrain-test", _admission_body()),
        ("/api/kc/phu/graduation-bar/steward-trust", _admission_body()),
        ("/api/kc/phu/steward-lane/activate", _admission_body()),
        ("/api/kc/phu/boot/v1/apply", _admission_body()),
    ]

    for path, body in routes:
        assert client.post(path, json=body).status_code == 401
        assert client.post(path, json={**body, "hood_ack": "WRONG"}, headers=_god_headers()).status_code == 422

    assert not entry_log.exists()


def test_consequential_phu_mutation_routes_require_alp_and_bind_admission_receipts(monkeypatch, tmp_path):
    entry_log = tmp_path / "entry.jsonl"
    monkeypatch.setattr(kpgs_renter_entry, "MAIN_BRAIN_LOG", entry_log)
    side_effects: list[str] = []

    def validate_poc(**_):
        side_effects.append("poc")
        return {"schema": "eco_poc_test_v1", "verdict": "RECORDED"}

    def populate_brain(**_):
        side_effects.append("populate")
        return {"schema": "populate_main_brain_test_v1", "verdict": "RECORDED"}

    def reattach_sub_brains(**_):
        side_effects.append("reattach")
        return {"schema": "reattach_subbrains_test_v1", "verdict": "RECORDED"}

    def promote_all(**_):
        side_effects.append("promote_all")
        return {"schema": "operating_mesh_promote_all_test_v1", "verdict": "RECORDED"}

    def promote_one(*_args, **_kwargs):
        side_effects.append("promote_one")
        return {"schema": "operating_mesh_promote_one_test_v1", "verdict": "RECORDED"}

    def record_trust(**_):
        side_effects.append("steward_trust")
        return {"schema": "steward_trust_test_v1", "verdict": "RECORDED"}

    def activate_steward(**_):
        side_effects.append("steward_activate")
        return {"schema": "steward_activate_test_v1", "verdict": "RECORDED"}

    def apply_boot():
        side_effects.append("boot_apply")
        return {"schema": "boot_apply_test_v1", "verdict": "RECORDED"}

    monkeypatch.setattr(kc_phu_legacy_api, "validate_eco_poc", validate_poc)
    monkeypatch.setattr(kc_phu_legacy_api, "populate_main_brain", populate_brain)
    monkeypatch.setattr(kc_phu_legacy_api, "reattach_detached_subbrains", reattach_sub_brains)
    monkeypatch.setattr(kc_phu_legacy_api, "promote_all_flagships", promote_all)
    monkeypatch.setattr(kc_phu_legacy_api, "promote_flagship", promote_one)
    monkeypatch.setattr(kc_phu_legacy_api, "record_steward_trust", record_trust)
    monkeypatch.setattr(kc_phu_legacy_api, "run_steward_lane_activate", activate_steward)
    monkeypatch.setattr(kc_phu_legacy_api, "apply_boot", apply_boot)
    monkeypatch.setattr(
        kc_phu_legacy_api,
        "require_alp_receipt",
        lambda: (_ for _ in ()).throw(ValueError("ALP unavailable")),
    )
    client = TestClient(app)
    routes = [
        ("/api/kc/phu/poc/validate", _eco_poc_body(), "eco_poc_validate"),
        (
            "/api/kc/phu/populate-main-brain",
            {**_admission_body(), "sync_vault_logs": False},
            "phu_populate_main_brain",
        ),
        (
            "/api/kc/phu/reattach-subbrains",
            {**_admission_body(), "dry_run": True},
            "phu_reattach_subbrains",
        ),
        (
            "/api/kc/phu/operating-mesh/promote-all",
            _admission_body(),
            "operating_mesh_promote_all",
        ),
        (
            "/api/kc/phu/operating-mesh/promote/subbrain-test",
            _admission_body(),
            "operating_mesh_promote_one",
        ),
        (
            "/api/kc/phu/graduation-bar/steward-trust",
            {**_admission_body(), "note": "test"},
            "graduation_steward_trust",
        ),
        (
            "/api/kc/phu/steward-lane/activate",
            {**_admission_body(), "note": "test"},
            "steward_lane_activate",
        ),
        (
            "/api/kc/phu/boot/v1/apply",
            _admission_body(),
            "phu_boot_apply",
        ),
    ]
    headers = _god_headers()

    for path, body, _operation in routes:
        assert client.post(path, json=body, headers=headers).status_code == 409

    assert side_effects == []
    log_rows = [json.loads(line) for line in entry_log.read_text(encoding="utf-8").splitlines()]
    assert [row["operation"] for row in log_rows] == [
        "eco_poc_validate",
        "phu_populate_main_brain",
        "phu_reattach_subbrains",
        "operating_mesh_promote_all",
        "operating_mesh_promote_one",
        "graduation_steward_trust",
        "steward_lane_activate",
        "phu_boot_apply",
    ]
    assert all(
        row["ack_verified"] is True and row["ack_receipt"]["verdict"] == "ACKNOWLEDGED"
        for row in log_rows
    )

    alp_receipt = {"schema": "alp_receipt_v1", "consistency_hash": "testhash"}
    monkeypatch.setattr(kc_phu_legacy_api, "require_alp_receipt", lambda: alp_receipt)
    for path, body, operation in routes:
        response = client.post(path, json=body, headers=headers)
        assert response.status_code == 200
        payload = response.json()
        assert payload["operator"] == "test-operator@local.invalid"
        assert payload["hood_entry"]["operation"] == operation
        assert payload["hood_entry"]["ack_verified"] is True
        assert payload["alp_receipt"] == alp_receipt

    assert side_effects == [
        "poc",
        "populate",
        "reattach",
        "promote_all",
        "promote_one",
        "steward_trust",
        "steward_activate",
        "boot_apply",
    ]


def test_mcp_poc_and_mesh_mutations_require_renter_admission(monkeypatch):
    from CLI import mao_server, tsap_mcp_server
    from kopano import (
        agent_build_poc_validate,
        eco_poc_validate,
        kpgs_cli_admission,
        operating_mesh,
        steward_lane,
    )

    calls: list[dict] = []

    def admit(**kwargs):
        calls.append(kwargs)
        return {"hood_entry": {"operation": kwargs["operation"]}, "alp_receipt": {"schema": "alp_receipt_v1"}}

    monkeypatch.setattr(kpgs_cli_admission, "admit_cli_renter", admit)
    monkeypatch.setattr(
        agent_build_poc_validate,
        "validate_agent_build_poc",
        lambda *, write_report: {"verdict": "PASS", "write_report": write_report},
    )
    monkeypatch.setattr(eco_poc_validate, "validate_eco_poc", lambda **_: {"verdict": "PASS"})
    monkeypatch.setattr(operating_mesh, "promote_all_flagships", lambda **_: {"verdict": "PASS"})
    monkeypatch.setattr(steward_lane, "run_steward_lane_activate", lambda **_: {"verdict": "ACTIVE"})

    common = {
        "renter_id": "mcp_test",
        "renter_class": "stateless_renter",
        "hood_ack": kpgs_renter_entry.HOOD_ACK_LITERAL,
    }
    mao_server.mao_agent_build_poc_validate(**common)
    mao_server.mao_eco_poc_validate(agent_id="agent", claim="claim", model="model", **common)
    tsap_mcp_server.tsap_agent_build_poc_validate(**common)
    tsap_mcp_server.eco_poc_validate(agent_id="agent", claim="claim", model="model", **common)
    tsap_mcp_server.tsap_operating_mesh_promote_all(**common)
    mao_server.mao_steward_lane_activate(**common)
    tsap_mcp_server.tsap_steward_lane_activate(**common)

    assert [call["operation"] for call in calls] == [
        "mcp:mao_agent_build_poc_validate",
        "mcp:mao_eco_poc_validate",
        "mcp:tsap_agent_build_poc_validate",
        "mcp:tsap_eco_poc_validate",
        "mcp:tsap_operating_mesh_promote_all",
        "mcp:mao_steward_lane_activate",
        "mcp:tsap_steward_lane_activate",
    ]
    assert all(call["hood_ack"] == kpgs_renter_entry.HOOD_ACK_LITERAL for call in calls)


def test_tsap_and_ai_flow_api_mutations_require_operator_and_renter_ack(monkeypatch, tmp_path):
    entry_log = tmp_path / "entry.jsonl"
    monkeypatch.setattr(kpgs_renter_entry, "MAIN_BRAIN_LOG", entry_log)
    fail_if_called = lambda *_args, **_kwargs: (_ for _ in ()).throw(
        AssertionError("mutation ran before admission")
    )
    for name in (
        "begin_department_students",
        "student_submit",
        "teacher_review",
        "blackmask_drill",
        "operate_guardian_flow",
        "operate_identi_flow",
    ):
        monkeypatch.setattr(kc_phu_legacy_api, name, fail_if_called)

    client = TestClient(app)
    routes = [
        ("/api/kc/phu/apprenticeship/begin-students", {**_admission_body(), "run_blackmask": False}),
        (
            "/api/kc/phu/apprenticeship/student-submit",
            {**_admission_body(), "department_id": "dept", "action": "submit", "evidence": "test"},
        ),
        (
            "/api/kc/phu/apprenticeship/teacher-review",
            {**_admission_body(), "department_id": "dept", "approve": True},
        ),
        ("/api/kc/phu/apprenticeship/blackmask-drill", {**_admission_body(), "agent_id": "cassy"}),
        (
            "/api/kc/phu/ai-flow/guardian",
            {**_admission_body(), "department_id": "dept", "action": "review", "evidence": "test"},
        ),
        (
            "/api/kc/phu/ai-flow/identi",
            {**_admission_body(), "department_id": "dept", "action": "review", "evidence": "test"},
        ),
    ]
    headers = _god_headers()
    for path, body in routes:
        assert client.post(path, json=body).status_code == 401
        assert client.post(path, json={**body, "hood_ack": "WRONG"}, headers=headers).status_code == 422
    assert not entry_log.exists()


def test_tsap_and_ai_flow_api_mutations_return_admission_receipts(monkeypatch, tmp_path):
    entry_log = tmp_path / "entry.jsonl"
    monkeypatch.setattr(kpgs_renter_entry, "MAIN_BRAIN_LOG", entry_log)
    alp_receipt = {"schema": "alp_receipt_v1", "consistency_hash": "tsap-test"}
    monkeypatch.setattr(kc_phu_legacy_api, "require_alp_receipt", lambda: alp_receipt)
    operations: list[str] = []

    def record(name: str):
        def run(*_args, **_kwargs):
            operations.append(name)
            return {"verdict": "RECORDED"}

        return run

    for name in (
        "begin_department_students",
        "student_submit",
        "teacher_review",
        "blackmask_drill",
        "operate_guardian_flow",
        "operate_identi_flow",
    ):
        monkeypatch.setattr(kc_phu_legacy_api, name, record(name))

    routes = [
        ("/api/kc/phu/apprenticeship/begin-students", {**_admission_body(), "run_blackmask": False}, "phu_apprenticeship_begin_students", "begin_department_students"),
        ("/api/kc/phu/apprenticeship/student-submit", {**_admission_body(), "department_id": "dept", "action": "submit", "evidence": "test"}, "phu_apprenticeship_student_submit", "student_submit"),
        ("/api/kc/phu/apprenticeship/teacher-review", {**_admission_body(), "department_id": "dept", "approve": True}, "phu_apprenticeship_teacher_review", "teacher_review"),
        ("/api/kc/phu/apprenticeship/blackmask-drill", {**_admission_body(), "agent_id": "cassy"}, "phu_apprenticeship_blackmask_drill", "blackmask_drill"),
        ("/api/kc/phu/ai-flow/guardian", {**_admission_body(), "department_id": "dept", "action": "review", "evidence": "test"}, "phu_ai_flow_guardian", "operate_guardian_flow"),
        ("/api/kc/phu/ai-flow/identi", {**_admission_body(), "department_id": "dept", "action": "review", "evidence": "test"}, "phu_ai_flow_identi", "operate_identi_flow"),
    ]
    client = TestClient(app)
    headers = _god_headers()
    for path, body, operation, side_effect in routes:
        response = client.post(path, json=body, headers=headers)
        assert response.status_code == 200
        payload = response.json()
        assert payload["hood_entry"]["operation"] == operation
        assert payload["hood_entry"]["ack_verified"] is True
        assert payload["alp_receipt"] == alp_receipt
        assert payload["verdict"] == "RECORDED"
        assert operations[-1] == side_effect
    assert len(operations) == len(routes)
    assert [json.loads(line)["operation"] for line in entry_log.read_text(encoding="utf-8").splitlines()] == [
        route[2] for route in routes
    ]


def test_mao_and_tsap_mcp_mutations_admit_before_any_execution(monkeypatch):
    import pytest

    from CLI import mao_server, tsap_mcp_server
    from kopano import kpgs_cli_admission, lpm_lph_engine, mao_dispatch, phu_apprenticeship

    calls: list[str] = []

    def admit(*, renter_id: str, renter_class: str, hood_ack: str, operation: str):
        calls.append(f"admit:{operation}")
        if hood_ack != kpgs_renter_entry.HOOD_ACK_LITERAL:
            raise ValueError("invalid renter acknowledgement")
        return {"hood_entry": {"operation": operation}, "alp_receipt": {"schema": "alp_receipt_v1"}}

    monkeypatch.setattr(kpgs_cli_admission, "admit_cli_renter", admit)
    for name in ("student_submit", "teacher_review", "begin_department_students"):
        monkeypatch.setattr(phu_apprenticeship, name, lambda **_: {"status": "RECORDED"})
    monkeypatch.setattr(phu_apprenticeship, "blackmask_drill", lambda *_args, **_: {"verdict": "SHIP"})
    monkeypatch.setattr(
        phu_apprenticeship,
        "departments_from_config",
        lambda: [{"id": "dept", "mao_teacher": "cassey"}],
    )
    monkeypatch.setattr(lpm_lph_engine, "operate_guardian_flow", lambda **_: {"verdict": "RECORDED"})
    monkeypatch.setattr(lpm_lph_engine, "operate_identi_flow", lambda **_: {"verdict": "RECORDED"})
    monkeypatch.setattr(mao_dispatch, "execute_task", lambda *_: calls.append("execute") or {"execution_mode": "test"})

    common = {
        "renter_id": "mcp_test",
        "renter_class": "stateless_renter",
        "hood_ack": kpgs_renter_entry.HOOD_ACK_LITERAL,
    }
    routes = [
        (tsap_mcp_server.tsap_student_submit, {"department_id": "dept", "action": "submit", "evidence": "test"}, "mcp:tsap_student_submit"),
        (tsap_mcp_server.tsap_teacher_review, {"department_id": "dept", "approve": True}, "mcp:tsap_teacher_review"),
        (tsap_mcp_server.tsap_blackmask_drill, {"agent_id": "cassy"}, "mcp:tsap_blackmask_drill"),
        (tsap_mcp_server.tsap_begin_department_students, {}, "mcp:tsap_begin_department_students"),
        (tsap_mcp_server.tsap_guardian_flow, {"department_id": "dept", "action": "review", "evidence": "test"}, "mcp:tsap_guardian_flow"),
        (tsap_mcp_server.tsap_identi_flow, {"department_id": "dept", "action": "review", "evidence": "test"}, "mcp:tsap_identi_flow"),
        (mao_server.mao_tsap_student_turn, {"department_id": "dept", "message": "submit"}, "mcp:mao_tsap_student_turn"),
        (mao_server.mao_tsap_teacher_turn, {"department_id": "dept", "approve": True}, "mcp:mao_tsap_teacher_turn"),
        (mao_server.mao_blackmask_drill, {"agent_id": "cassy"}, "mcp:mao_blackmask_drill"),
        (mao_server.mao_begin_department_students, {}, "mcp:mao_begin_department_students"),
        (mao_server.mao_guardian_flow, {"department_id": "dept", "action": "review", "evidence": "test"}, "mcp:mao_guardian_flow"),
        (mao_server.mao_identi_flow, {"department_id": "dept", "action": "review", "evidence": "test"}, "mcp:mao_identi_flow"),
    ]
    for tool, arguments, expected_operation in routes:
        calls.clear()
        result = tool(**arguments, **common)
        assert calls[0] == f"admit:{expected_operation}"
        assert result["hood_entry"]["operation"] == expected_operation
        assert result["alp_receipt"]["schema"] == "alp_receipt_v1"

    calls.clear()
    with pytest.raises(ValueError, match="invalid renter acknowledgement"):
        mao_server.mao_tsap_student_turn(
            department_id="dept",
            message="must not execute",
            renter_id="mcp_test",
            renter_class="stateless_renter",
            hood_ack="WRONG",
        )
    assert calls == ["admit:mcp:mao_tsap_student_turn"]


def test_tsap_and_ai_flow_mutation_clis_require_explicit_renter_fields():
    invocations = [
        ("kc_phu_department_students_begin.py", ["--drill-agent", "cassy"]),
        (
            "kc_ai_flow_operate.py",
            ["guardian", "--department", "dept", "--action", "review", "--evidence", "test"],
        ),
        (
            "kc_ai_flow_operate.py",
            ["identi", "--department", "dept", "--action", "review", "--evidence", "test"],
        ),
    ]
    for script, arguments in invocations:
        proc = subprocess.run(
            [sys.executable, str(REPO / "scripts" / script), *arguments],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 2
        assert "--renter-id" in proc.stderr
        assert "--hood-ack" in proc.stderr


def test_false_breathing_cycle_cannot_emit_gsmb_pass(monkeypatch, tmp_path):
    from kopano import protocols, telemetry_breathing_flow

    monkeypatch.setattr(gsmb_poc, "POC_LOG", tmp_path / "gsmb.jsonl")
    monkeypatch.setattr(
        kpgs_activation_gate,
        "activation_gate_for_execution",
        lambda **_: {
            "activation_allowed": True,
            "verdict": "ALLOW",
            "alp_receipt": {"schema": "alp_receipt_v1", "consistency_hash": "testhash"},
        },
    )
    monkeypatch.setattr(
        protocols,
        "activate_all_protocols",
        lambda **_: {
            "schema": "mmao_activation_v1",
            "alp_receipt": "testhash",
            "protocols_active": 19,
        },
    )
    monkeypatch.setattr(telemetry_breathing_flow.TelemetryBreathingFlow, "execute_breathing_cycle", lambda *_: False)
    monkeypatch.setattr(
        telemetry_breathing_flow.TelemetryBreathingFlow,
        "emit_agent_dots",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("emitted after failed cycle")),
    )

    receipt = gsmb_poc.run_gsmb_poc()
    assert receipt["verdict"] == "HOLD"
    assert receipt["failed_stage"] == "breathing_cycle"
    assert json.loads((tmp_path / "gsmb.jsonl").read_text(encoding="utf-8"))["verdict"] == "HOLD"


def test_mutating_kpgs_clis_require_explicit_renter_ack_before_execution():
    cases = [
        [sys.executable, "scripts/kc_kpgs_governance.py", "compile", "--renter-id", "cli_test"],
        [sys.executable, "scripts/kc_kpgs_smoke_poc.py", "smoke", "--renter-id", "cli_test"],
        [sys.executable, "-m", "kopano.gsmb_poc"],
        [sys.executable, "kopano-core/kopano/continuous_gsmb_runner.py"],
        [sys.executable, "scripts/kc_eco_poc_validate.py", "--renter-id", "cli_test", "--claim", "test", "--model", "test"],
        [sys.executable, "scripts/kc_phu_populate_main_brain.py", "--renter-id", "cli_test"],
        [sys.executable, "scripts/kc_phu_reattach_subbrains.py", "--renter-id", "cli_test"],
        [sys.executable, "scripts/kc_agent_build_poc_validate.py", "--renter-id", "cli_test"],
        [sys.executable, "scripts/kc_kpefs_full_gate.py", "--renter-id", "cli_test"],
        [sys.executable, "scripts/kc_kpefs_run_snapshot.py", "--renter-id", "cli_test"],
        [sys.executable, "scripts/kc_phu_operating_mesh.py", "promote-all", "--renter-id", "cli_test"],
        [sys.executable, "scripts/kc_phu_graduation_bar.py", "steward-trust", "--renter-id", "cli_test"],
        [sys.executable, "scripts/kc_steward_lane_run.py", "activate", "--renter-id", "cli_test"],
        [sys.executable, "scripts/kc_phu_boot_v1.py", "apply", "--renter-id", "cli_test"],
    ]
    env = {**os.environ, "PYTHONPATH": str(REPO / "kopano-core")}

    for command in cases:
        result = subprocess.run(command, cwd=REPO, env=env, capture_output=True, text=True, check=False)
        assert result.returncode == 2
        assert "--hood-ack" in result.stderr


def test_monorepo_phu_actions_require_confirmation_and_forward_renter_ack(monkeypatch):
    from kopano import monorepo_control

    calls: list[tuple[str, list[str]]] = []
    monkeypatch.setattr(
        monorepo_control,
        "run_script",
        lambda script, args: (calls.append((script, args)) or (0, "ok")),
    )

    try:
        monorepo_control.execute_script_action("phu_populate_main_brain", confirm=True)
    except ValueError as exc:
        assert "renter_id and hood_ack" in str(exc)
    else:
        raise AssertionError("PHU populate accepted missing renter admission")

    try:
        monorepo_control.execute_script_action(
            "phu_reattach_subbrains",
            renter_id="cli_test",
            hood_ack=kpgs_renter_entry.HOOD_ACK_LITERAL,
        )
    except ValueError as exc:
        assert "confirm=true" in str(exc)
    else:
        raise AssertionError("PHU reattachment accepted missing confirmation")

    result = monorepo_control.execute_script_action(
        "phu_reattach_subbrains",
        confirm=True,
        renter_id="cli_test",
        renter_class="stateless_renter",
        hood_ack=kpgs_renter_entry.HOOD_ACK_LITERAL,
    )
    assert result["ok"] is True
    assert calls == [
        (
            "kc_phu_reattach_subbrains.py",
            [
                "--renter-id",
                "cli_test",
                "--renter-class",
                "stateless_renter",
                "--hood-ack",
                kpgs_renter_entry.HOOD_ACK_LITERAL,
            ],
        )
    ]
