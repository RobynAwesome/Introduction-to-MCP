"""KPEFS CLI persistence requires renter admission; diagnostics remain read-only."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from scripts import kc_kpefs_full_gate, kc_kpefs_run_snapshot
from kopano import agent_build_poc_validate, external_swarm_lane, graduation_bar, operating_mesh


def test_full_gate_no_write_skips_report_and_snapshot_writes(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["kc_kpefs_full_gate.py", "--no-write", "--json"])
    monkeypatch.setattr(kc_kpefs_full_gate, "_run", lambda *_: (0, "ok"))
    monkeypatch.setattr(
        operating_mesh,
        "operating_mesh_status",
        lambda: {"phase3_exit_met": True, "operating_count": 10, "flagships_total": 10},
    )
    monkeypatch.setattr(
        graduation_bar,
        "graduation_bar_status",
        lambda: {"phase5_exit_met": True, "verified_production": 10, "public_graduation_bar": 10},
    )
    monkeypatch.setattr(external_swarm_lane, "kpefs_closure_status", lambda: {"full_closure": False})
    validation_modes: list[bool] = []
    monkeypatch.setattr(
        agent_build_poc_validate,
        "validate_agent_build_poc",
        lambda *, write_report: (
            validation_modes.append(write_report)
            or {"verdict": "PASS", "passed": 1, "total": 1, "failed_checks": [], "report_path": None}
        ),
    )
    monkeypatch.setattr(
        external_swarm_lane,
        "write_closure_snapshot",
        lambda **_: (_ for _ in ()).throw(AssertionError("snapshot persisted in no-write mode")),
    )

    assert kc_kpefs_full_gate.main() == 0
    report = json.loads(capsys.readouterr().out)
    assert report["verdict"] == "PASS"
    assert validation_modes == [False]


def test_run_snapshot_no_write_skips_closure_snapshot(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        ["kc_kpefs_run_snapshot.py", "--skip-gate", "--no-write", "--json"],
    )
    monkeypatch.setattr(
        external_swarm_lane,
        "kpefs_closure_status",
        lambda: {"internal_kpefs_complete": True, "full_closure": False},
    )
    monkeypatch.setattr(
        external_swarm_lane,
        "write_closure_snapshot",
        lambda **_: (_ for _ in ()).throw(AssertionError("snapshot persisted in no-write mode")),
    )

    assert kc_kpefs_run_snapshot.main() == 0
    report = json.loads(capsys.readouterr().out)
    assert report["closure"]["internal_kpefs_complete"] is True
