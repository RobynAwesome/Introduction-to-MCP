"""Tests for KPGS activation gate."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.kpgs_activation_gate import (  # noqa: E402
    REQUIRED_AGENT_COUNT,
    check_kpgs_activation_gate,
    require_activation_allowed,
)


def test_activation_gate_structure():
    gate = check_kpgs_activation_gate()
    assert gate["schema"] == "kpgs_activation_gate_v1"
    assert "activation_allowed" in gate
    assert "checks" in gate
    assert gate["required_agents"] == REQUIRED_AGENT_COUNT
    assert len(gate["checks"]) >= 6


def test_activation_gate_allow_when_guild_ship():
    gate = check_kpgs_activation_gate(write_report=False)
    if gate["activation_allowed"]:
        assert gate["verdict"] == "ALLOW"
        assert gate["failed_checks"] == []
        assert gate["checks_passed"] == gate["checks_total"]
    else:
        assert gate["verdict"] == "BLOCK"
        assert len(gate["failed_checks"]) > 0


def test_activation_gate_writes_report(tmp_path, monkeypatch):
    from kopano import kpgs_activation_gate as mod

    report_path = tmp_path / "KPGS_ACTIVATION_GATE.json"
    monkeypatch.setattr(mod, "GATE_REPORT_PATH", report_path)
    gate = check_kpgs_activation_gate(write_report=True)
    assert report_path.is_file()
    assert gate.get("report_path")


def _allow_gate():
    return {
        "activation_allowed": True,
        "verdict": "ALLOW",
        "message": "[KPGS_GATE] ALLOW",
    }


def _valid_alp_receipt():
    return {
        "schema": "alp_receipt_v1",
        "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
        "consistency_hash": "abc123",
    }


def test_require_activation_blocks_when_alp_unavailable(monkeypatch):
    from kopano import kpgs_activation_gate as mod

    monkeypatch.setattr(mod, "_ALP_AVAILABLE", False)
    monkeypatch.setattr(mod, "check_kpgs_activation_gate", _allow_gate)
    with pytest.raises(ValueError, match="mandatory ALP unavailable"):
        require_activation_allowed()


def test_require_activation_blocks_when_alp_throws(monkeypatch):
    from kopano import kpgs_activation_gate as mod

    def explode(*, context):
        raise RuntimeError(f"boom: {context}")

    monkeypatch.setattr(mod, "_ALP_AVAILABLE", True)
    monkeypatch.setattr(mod, "_alp_activate", explode)
    monkeypatch.setattr(mod, "check_kpgs_activation_gate", _allow_gate)
    with pytest.raises(ValueError, match="mandatory ALP activation failed"):
        require_activation_allowed()


def test_require_activation_blocks_invalid_alp_receipt(monkeypatch):
    from kopano import kpgs_activation_gate as mod

    monkeypatch.setattr(mod, "_ALP_AVAILABLE", True)
    monkeypatch.setattr(mod, "_alp_activate", lambda **_: {"schema": "wrong"})
    monkeypatch.setattr(mod, "check_kpgs_activation_gate", _allow_gate)
    with pytest.raises(ValueError, match="mandatory ALP receipt invalid"):
        require_activation_allowed()


def test_require_activation_embeds_valid_alp_receipt(monkeypatch):
    from kopano import kpgs_activation_gate as mod

    receipt = _valid_alp_receipt()
    monkeypatch.setattr(mod, "_ALP_AVAILABLE", True)
    monkeypatch.setattr(mod, "_alp_activate", lambda **_: receipt)
    monkeypatch.setattr(mod, "check_kpgs_activation_gate", _allow_gate)
    gate = require_activation_allowed()
    assert gate["alp_receipt"] == receipt
