"""Regression coverage for high-severity CodeQL input-handling findings."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))
sys.path.insert(0, str(REPO / "scripts"))

from kopano import eco_poc_validate as eco  # noqa: E402
from kc_bracket_lint import lint_brackets  # noqa: E402


REG = {
    "sacred_forbidden_patterns": [],
    "canonical_bracket_forms": [
        {"bracket": "CANONICAL_FORM", "aliases": ["Example Name"]},
    ],
}


def test_bracket_linter_preserves_tag_classification():
    assert lint_brackets("[CANONICAL_FORM]", REG) == []
    assert lint_brackets("[Example Name]", REG)
    assert lint_brackets("unmatched [ tag", REG) == []


def test_bracket_linter_handles_adversarial_unclosed_input_in_one_pass():
    text = "[\\[" * 20_000
    assert lint_brackets(text, REG) == []


def _validate_evidence(monkeypatch: pytest.MonkeyPatch, repo_root: Path, evidence: str):
    monkeypatch.setattr(eco, "REPO_ROOT", repo_root)
    monkeypatch.setattr(
        eco,
        "load_unemployment_doctrine",
        lambda: {"livelihood_signals": [{"id": "LIV-01"}], "rate_percent": 32.8},
    )
    monkeypatch.setattr(eco, "_catalog_agent", lambda _agent_id: None)
    monkeypatch.setattr(eco, "_load_state", lambda: {"records": []})
    monkeypatch.setattr(eco, "_save_state", lambda _state: None)
    monkeypatch.setattr(eco, "_append_main_brain", lambda *_args: None)
    return eco.validate_eco_poc(
        agent_id="example_agent",
        claim="Bounded validation claim",
        model="A validation model with enough detail for the stated procedure",
        relation="Observed result",
        baseline="0",
        observed="1",
        unit="events",
        evidence=evidence,
        livelihood_ids=["LIV-01"],
        anticipated_delta="One measured validation event",
    )


def test_repo_relative_evidence_file_is_accepted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    repo_root = tmp_path / "repo"
    evidence_file = repo_root / "receipts" / "result.txt"
    evidence_file.parent.mkdir(parents=True)
    evidence_file.write_text("receipt", encoding="utf-8")

    result = _validate_evidence(monkeypatch, repo_root, "receipts/result.txt")
    receipt = next(item for item in result["oracles"] if item["id"] == "receipt_stack")
    assert receipt["passed"] is True


def test_repo_relative_jsonl_reference_keeps_existing_behavior(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    result = _validate_evidence(monkeypatch, repo_root, "logs/pending-receipt.jsonl")
    receipt = next(item for item in result["oracles"] if item["id"] == "receipt_stack")
    assert receipt["passed"] is True


@pytest.mark.parametrize("evidence", ["../secret.jsonl", "..\\secret.jsonl"])
def test_parent_path_evidence_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, evidence: str):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (tmp_path / "secret.jsonl").write_text("private", encoding="utf-8")

    result = _validate_evidence(monkeypatch, repo_root, evidence)
    receipt = next(item for item in result["oracles"] if item["id"] == "receipt_stack")
    assert receipt["passed"] is False


def test_absolute_external_evidence_file_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    external_file = tmp_path / "outside.txt"
    external_file.write_text("private", encoding="utf-8")

    result = _validate_evidence(monkeypatch, repo_root, str(external_file))
    receipt = next(item for item in result["oracles"] if item["id"] == "receipt_stack")
    assert receipt["passed"] is False


def test_execution_gate_does_not_echo_foreign_exception_text(monkeypatch: pytest.MonkeyPatch):
    from kopano import kpgs_activation_gate as gate

    def foreign():
        raise ValueError("secret-stack-trace-token")

    monkeypatch.setattr(gate, "require_activation_allowed", foreign)
    report = gate.activation_gate_for_execution(write_report=False)
    assert report["verdict"] == "BLOCK"
    assert report["message"] == "KPGS activation gate BLOCK"
    assert "secret-stack-trace-token" not in report["message"]


def test_execution_gate_keeps_known_alp_block_text(monkeypatch: pytest.MonkeyPatch):
    from kopano import kpgs_activation_gate as gate

    def known():
        raise ValueError(gate._ALP_UNAVAILABLE)

    monkeypatch.setattr(gate, "require_activation_allowed", known)
    report = gate.activation_gate_for_execution(write_report=False)
    assert report["message"] == gate._ALP_UNAVAILABLE
