"""Verify host-issued GSMB source-read admission, not an agent's self-report.

A trusted reader must independently observe source reads, verify a bounded risk
probe, and sign the resulting claims outside the renter's writable environment.
This verifier never issues attestations and grants no permissions by itself.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import re
from typing import Any, Callable, Mapping

SCHEMA = "gsmb-entry-read-attestation-v1"
REQUIRED_SOURCES = {
    "local": frozenset({"local:home", "local:legacy", "local:now", "local:entryway"}),
    "cloud": frozenset({"cloud:agents", "cloud:now", "cloud:incident-index"}),
    "drive": frozenset({"drive:admission", "drive:agent-homes", "drive:bulletin"}),
}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def canonical_claims(claims: Mapping[str, Any]) -> bytes:
    return json.dumps(claims, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _time(raw: Any) -> datetime | None:
    if not isinstance(raw, str):
        return None
    try:
        d = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return d.astimezone(timezone.utc) if d.tzinfo is not None else None
    except (ValueError, OverflowError):
        return None


def verify_entry_attestation(
    ctx: Mapping[str, Any],
    public_keys_hex: Mapping[str, str],
    conversation_id: str,
    verify_signature: Callable[[bytes, bytes, bytes], bool],
    *,
    now: datetime | None = None,
) -> tuple[bool, str]:
    """Return (admitted, reason) under a sealed host-provided context.

    The host must independently validate each read event and sign the claims.
    Signed agent assertions, or a claim stored only in a document, never qualify.
    """
    receipt = ctx.get("entry_attestation")
    if not isinstance(receipt, dict) or set(receipt) != {"claims", "kid", "signature_hex"}:
        return False, "ENTRY_ATTESTATION_MISSING_OR_MALFORMED"
    claims = receipt.get("claims")
    kid = receipt.get("kid")
    if not isinstance(claims, dict) or not isinstance(kid, str) or kid not in public_keys_hex:
        return False, "ENTRY_ATTESTATION_UNTRUSTED_KEY"
    try:
        pub = bytes.fromhex(public_keys_hex[kid])
        sig = bytes.fromhex(receipt["signature_hex"])
        signed_bytes = canonical_claims(claims)
        valid_sig = len(pub) == 32 and len(sig) == 64 and verify_signature(pub, signed_bytes, sig)
    except (ValueError, TypeError, OverflowError, RecursionError):
        valid_sig = False
    if not valid_sig:
        return False, "ENTRY_ATTESTATION_INVALID_SIGNATURE"

    if claims.get("schema") != SCHEMA or claims.get("reader_kind") != "trusted_host":
        return False, "ENTRY_ATTESTATION_INVALID_ISSUER"
    if not conversation_id or claims.get("session_id") != conversation_id or ctx.get("session_id") != conversation_id:
        return False, "ENTRY_ATTESTATION_SESSION_MISMATCH"
    for field in ("actor_id", "role_id", "tenant_id", "domain_id", "task_id"):
        if not isinstance(ctx.get(field), str) or not ctx[field] or claims.get(field) != ctx[field]:
            return False, "ENTRY_ATTESTATION_AUTHORITY_MISMATCH"
    token = ctx.get("lease_token")
    if not isinstance(token, str) or not token or claims.get("lease_sha256") != hashlib.sha256(token.encode("utf-8")).hexdigest():
        return False, "ENTRY_ATTESTATION_LEASE_MISMATCH"
    digest = ctx.get("policy_digest")
    if not isinstance(digest, str) or not _SHA256.fullmatch(digest) or claims.get("policy_digest") != digest:
        return False, "ENTRY_ATTESTATION_POLICY_MISMATCH"

    current = now or datetime.now(timezone.utc)
    issued, expires = _time(claims.get("issued_at")), _time(claims.get("expires_at"))
    if issued is None or expires is None or issued > current + timedelta(seconds=30) or expires <= current:
        return False, "ENTRY_ATTESTATION_EXPIRED_OR_INVALID_TIME"
    if expires - issued > timedelta(minutes=15) or expires <= issued:
        return False, "ENTRY_ATTESTATION_OVERLONG_LEASE"

    surfaces = ctx.get("admission_surfaces")
    claimed_surfaces = claims.get("surfaces")
    if not isinstance(surfaces, list) or not surfaces or not all(isinstance(s, str) for s in surfaces) or len(surfaces) != len(set(surfaces)):
        return False, "ENTRY_ATTESTATION_SURFACES_MISSING"
    if not set(surfaces).issubset(REQUIRED_SOURCES) or claimed_surfaces != sorted(surfaces):
        return False, "ENTRY_ATTESTATION_SURFACE_MISMATCH"
    expected = ctx.get("expected_source_versions")
    if not isinstance(expected, dict) or not expected:
        return False, "ENTRY_ATTESTATION_SOURCE_BASELINE_MISSING"
    needed = set().union(*(REQUIRED_SOURCES[s] for s in surfaces))
    if not needed.issubset(expected) or any(not isinstance(v, str) or not v.strip() for v in expected.values()):
        return False, "ENTRY_ATTESTATION_REQUIRED_SOURCES_MISSING"
    observations = claims.get("source_reads")
    if not isinstance(observations, list) or len(observations) != len(expected):
        return False, "ENTRY_ATTESTATION_READS_MISSING"
    observed: dict[str, str] = {}
    for row in observations:
        if not isinstance(row, dict) or not all(isinstance(row.get(k), str) and row[k] for k in ("source", "version", "host_read_event_id")):
            return False, "ENTRY_ATTESTATION_READ_EVENT_INVALID"
        source = row["source"]
        if source in observed:
            return False, "ENTRY_ATTESTATION_DUPLICATE_READ"
        observed[source] = row["version"]
    if observed != expected:
        return False, "ENTRY_ATTESTATION_SOURCE_VERSION_MISMATCH"

    required_incidents = ctx.get("required_incident_ids")
    acknowledged_incidents = claims.get("incident_reads")
    if not isinstance(required_incidents, list) or not required_incidents or not all(isinstance(i, str) and i for i in required_incidents):
        return False, "ENTRY_ATTESTATION_INCIDENT_BASELINE_MISSING"
    if not isinstance(acknowledged_incidents, list) or not set(required_incidents).issubset(set(map(str, acknowledged_incidents))):
        return False, "ENTRY_ATTESTATION_INCIDENT_READ_MISSING"
    if claims.get("risk_probe_verdict") != "PASS":
        return False, "ENTRY_ATTESTATION_RISK_PROBE_NOT_PASSED"
    return True, "ENTRY_ATTESTATION_VALID"
