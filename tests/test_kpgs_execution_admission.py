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
    ]
    env = {**os.environ, "PYTHONPATH": str(REPO / "kopano-core")}

    for command in cases:
        result = subprocess.run(command, cwd=REPO, env=env, capture_output=True, text=True, check=False)
        assert result.returncode == 2
        assert "--hood-ack" in result.stderr
