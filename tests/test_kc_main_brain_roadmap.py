"""Tests for Main Brain roadmap gate."""

from __future__ import annotations

import json
from pathlib import Path

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from kc_main_brain_roadmap import check_entry_gate, load_roadmap  # noqa: E402


def test_roadmap_loads() -> None:
    roadmap = load_roadmap()
    assert roadmap["schema"] == "main_brain_roadmap_v1"
    assert roadmap["cassy"]["lead_student"] is True


def test_historical_rows_never_promote_to_production() -> None:
    ok, msg = check_entry_gate()
    assert not ok
    assert "HOLD_UNVERIFIED_RUNTIME" in msg


def test_no_caller_supplied_verifier_bypass() -> None:
    import pytest
    with pytest.raises(TypeError):
        check_entry_gate(live_proof_verifier=lambda: True)


def test_existing_historical_count_remains_non_authoritative() -> None:
    ok, msg = check_entry_gate()
    assert not ok
    assert "provider-authenticated serving-runtime verification not implemented" in msg


def test_swarm_agents_registry() -> None:
    reg = json.loads(
        (REPO_ROOT / "docs/swarm-ops/agents/SWARM_AGENTS.json").read_text(encoding="utf-8")
    )
    cassy = next(a for a in reg["agents"] if a["id"] == "cassy")
    assert cassy["apprenticeship"]["active"] is True
    mesh = [a for a in reg["agents"] if a["id"] == "claude"][0]
    assert mesh["apprenticeship"]["student"] == "cassy"
