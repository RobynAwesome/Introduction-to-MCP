"""Synthetic acceptance checks for signed GSMB source-read admission.

These do NOT prove provider-supplied read events, host key custody, runtime
isolation, or enforcement in Local/Drive clients.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SECURITY_DIR = ROOT / "governance" / "kpgs-vnext" / "security"
sys.path.insert(0, str(SECURITY_DIR))

from ed25519_stdlib import generate_keypair, sign, verify  # noqa: E402
from entry_read_attestation import (  # noqa: E402
    SCHEMA, REQUIRED_SOURCES, canonical_claims, verify_entry_attestation,
)


def _fixture(surfaces=None):
    surfaces = surfaces or ["cloud"]
    now = datetime.now(timezone.utc)
    seed, public = generate_keypair()
    expected = {src: "sha-or-provider-revision:" + src for src in sorted(set().union(*(REQUIRED_SOURCES[s] for s in surfaces)))}
    ctx = {
        "actor_id": "ag-1",
        "role_id": "lead-developer",
        "tenant_id": "kopano",
        "domain_id": "gsmb",
        "task_id": "task-fixture-1",
        "session_id": "conv-fixture-1",
        "lease_token": "synthetic-lease-token",
        "policy_digest": "f" * 64,
        "admission_surfaces": surfaces,
        "expected_source_versions": expected,
        "required_incident_ids": ["#163"],
    }
    claims = {
        "schema": SCHEMA,
        "reader_kind": "trusted_host",
        "actor_id": ctx["actor_id"],
        "role_id": ctx["role_id"],
        "tenant_id": ctx["tenant_id"],
        "domain_id": ctx["domain_id"],
        "task_id": ctx["task_id"],
        "session_id": ctx["session_id"],
        "lease_sha256": hashlib.sha256(ctx["lease_token"].encode("utf-8")).hexdigest(),
        "policy_digest": ctx["policy_digest"],
        "issued_at": (now - timedelta(minutes=1)).isoformat(),
        "expires_at": (now + timedelta(minutes=5)).isoformat(),
        "surfaces": sorted(surfaces),
        "source_reads": [
            {"source": source, "version": version, "host_read_event_id": "host-synthetic:" + source}
            for source, version in sorted(expected.items())
        ],
        "incident_reads": ["#163"],
        "risk_probe_verdict": "PASS",
    }

    def resign():
        ctx["entry_attestation"] = {
            "claims": claims,
            "kid": "k1",
            "signature_hex": sign(seed, canonical_claims(claims)).hex(),
        }

    resign()
    return ctx, claims, resign, {"k1": public.hex()}


def _check(ctx, keys, session="conv-fixture-1"):
    return verify_entry_attestation(ctx, keys, session, verify)


@pytest.mark.parametrize("surfaces", [["cloud"], ["local"], ["drive"], ["cloud", "drive", "local"]])
def test_read_attestation_per_knowledge_base_and_cross_estate(surfaces):
    ctx, _, _, keys = _fixture(surfaces)
    assert _check(ctx, keys) == (True, "ENTRY_ATTESTATION_VALID")


def test_missing_attestation_and_agent_assertions_do_not_count():
    ctx, claims, _, keys = _fixture()
    ctx.pop("entry_attestation")
    ctx["agent_says_it_read_now"] = True
    assert _check(ctx, keys)[0] is False


def test_unsigned_claim_edit_rejected():
    ctx, claims, _, keys = _fixture()
    claims["incident_reads"].append("#999")
    assert _check(ctx, keys)[1] == "ENTRY_ATTESTATION_INVALID_SIGNATURE"


def test_missing_host_read_events_rejected():
    ctx, claims, resign, keys = _fixture()
    claims["source_reads"] = []
    resign()
    assert _check(ctx, keys)[1] == "ENTRY_ATTESTATION_READS_MISSING"


def test_missing_required_incident_rejected():
    ctx, claims, resign, keys = _fixture()
    claims["incident_reads"] = []
    resign()
    assert _check(ctx, keys)[1] == "ENTRY_ATTESTATION_INCIDENT_READ_MISSING"


def test_risk_probe_must_pass():
    ctx, claims, resign, keys = _fixture()
    claims["risk_probe_verdict"] = "HOLD"
    resign()
    assert _check(ctx, keys)[1] == "ENTRY_ATTESTATION_RISK_PROBE_NOT_PASSED"


def test_stale_source_version_or_copied_agreement_cannot_substitute_current_expected():
    ctx, _, _, keys = _fixture(["cloud", "drive"])
    ctx["expected_source_versions"]["cloud:now"] = "new-current-sha"
    assert _check(ctx, keys)[1] == "ENTRY_ATTESTATION_SOURCE_VERSION_MISMATCH"


def test_local_missing_blocks_local_admission_not_cloud_read():
    ctx, claims, resign, keys = _fixture(["cloud", "local"])
    claims["source_reads"] = [x for x in claims["source_reads"] if not x["source"].startswith("local:")]
    resign()
    assert _check(ctx, keys)[1] == "ENTRY_ATTESTATION_READS_MISSING"


@pytest.mark.parametrize("field", ["task_id", "actor_id", "role_id", "tenant_id", "domain_id"])
def test_identity_task_tenant_role_binding(field):
    ctx, _, _, keys = _fixture()
    ctx[field] = "wrong"
    assert _check(ctx, keys)[1] == "ENTRY_ATTESTATION_AUTHORITY_MISMATCH"


def test_session_binding_not_just_user_claim():
    ctx, _, _, keys = _fixture()
    assert _check(ctx, keys, session="different-conversation")[1] == "ENTRY_ATTESTATION_SESSION_MISMATCH"


def test_lease_and_policy_binding():
    ctx, _, _, keys = _fixture()
    ctx["lease_token"] = "swapped"
    assert _check(ctx, keys)[1] == "ENTRY_ATTESTATION_LEASE_MISMATCH"
    ctx, _, _, keys = _fixture()
    ctx["policy_digest"] = "1" * 64
    assert _check(ctx, keys)[1] == "ENTRY_ATTESTATION_POLICY_MISMATCH"


def test_expired_receipt_and_long_ttl():
    ctx, claims, resign, keys = _fixture()
    now = datetime.now(timezone.utc)
    claims["issued_at"] = (now - timedelta(hours=2)).isoformat()
    claims["expires_at"] = (now - timedelta(hours=1)).isoformat()
    resign()
    assert _check(ctx, keys)[1] == "ENTRY_ATTESTATION_EXPIRED_OR_INVALID_TIME"
    ctx, claims, resign, keys = _fixture()
    claims["expires_at"] = (now + timedelta(hours=2)).isoformat()
    resign()
    assert _check(ctx, keys)[1] == "ENTRY_ATTESTATION_OVERLONG_LEASE"


def test_duplicate_source_receipt_rejected():
    ctx, claims, resign, keys = _fixture()
    claims["source_reads"][0] = dict(claims["source_reads"][1])
    resign()
    assert _check(ctx, keys)[1] == "ENTRY_ATTESTATION_DUPLICATE_READ"


def _load_gate_module():
    gate_path = ROOT / "scripts" / "kpgs_pretooluse_gate.py"
    spec = importlib.util.spec_from_file_location("kpgs_gate_admission_test", gate_path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_pretooluse_enforce_mode_blocks_without_read_receipt(monkeypatch):
    gate = _load_gate_module()
    ctx, _, _, keys = _fixture()
    ctx["entry_admission_mode"] = "enforce"
    ctx.pop("entry_attestation")
    monkeypatch.setattr(gate, "_load_trusted_context", lambda: {"ctx": ctx, "pub_keys_hex": keys, "writable_roots": [ROOT]})
    # Avoid setting up a live lease. This test verifies the read gate denies before lease authorization.
    monkeypatch.setattr(gate, "_authorize_capabilities", lambda *args: None)
    p = {"conversationId": "conv-fixture-1", "toolCall": {"name": "run_command", "args": {"CommandLine": "echo sample"}}}
    assert "ENTRY_ATTESTATION_MISSING" in gate.handle_pre_tool_use(p)["reason"]
    assert gate.handle_pre_tool_use({"toolCall": {"name": "read_file", "args": {}}})["decision"] == "allow"


def test_pretooluse_enforce_mode_accepts_signed_fixture_before_lease(monkeypatch):
    gate = _load_gate_module()
    ctx, _, _, keys = _fixture()
    ctx["entry_admission_mode"] = "enforce"
    monkeypatch.setattr(gate, "_load_trusted_context", lambda: {"ctx": ctx, "pub_keys_hex": keys, "writable_roots": [ROOT], "ctx_path": ROOT / "out-of-band", "ledger_path": None})
    monkeypatch.setattr(gate, "_authorize_capabilities", lambda *args: None)
    # The positive path covers only bounded file mutation; remote/shell tools
    # are held until their own trusted typed adapters exist.
    p = {"conversationId": "conv-fixture-1", "toolCall": {"name": "write_file", "args": {"Path": str(ROOT / "review-only.txt")}}}
    assert gate.handle_pre_tool_use(p)["decision"] == "allow"

def test_pretooluse_enforce_mode_denies_unmediated_external_tool_families(monkeypatch):
    gate = _load_gate_module()
    ctx, _, _, keys = _fixture()
    ctx["entry_admission_mode"] = "enforce"
    monkeypatch.setattr(gate, "_load_trusted_context", lambda: {"ctx": ctx, "pub_keys_hex": keys, "writable_roots": [ROOT]})
    monkeypatch.setattr(gate, "_authorize_capabilities", lambda *args: None)
    cases = [
        ("run_command", {"CommandLine": "echo sample"}),
        ("invoke_subagent", {"TypeName": "child", "Prompt": "work"}),
        ("call_mcp_tool", {"ServerName": "drive", "ToolName": "write", "Arguments": {}}),
        ("mcp_google_drive_update_file", {"file_id": "test"}),
        ("browser_click", {"element": "save"}),
    ]
    for name, args in cases:
        p = {"conversationId": "conv-fixture-1", "toolCall": {"name": name, "args": args}}
        result = gate.handle_pre_tool_use(p)
        assert result["decision"] == "deny" and "typed host adapter" in result["reason"], result
