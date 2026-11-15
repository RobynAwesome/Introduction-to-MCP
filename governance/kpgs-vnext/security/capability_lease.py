"""Reference KPGS capability-lease authority runtime.

This module is intentionally standard-library only. It proves the governance
semantics required by issue #42 without turning a Stateless Renter, frontend,
or skill into a credential landlord.

The compact token is a KPGS envelope, not a claim of JWT conformance. An
OIDC/JWT identity boundary may translate an authenticated subject into this
lease at the Sovereign Hub boundary. The signing key ring remains server-side.
"""

from __future__ import annotations

from base64 import urlsafe_b64decode, urlsafe_b64encode
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import importlib.util
import json
from pathlib import Path
import secrets
import sys
from typing import Any, Callable, Iterable, Mapping

TOKEN_TYPE = "KPGS-LEASE"
TOKEN_ALG = "HS256"
EDDSA_ALG = "EdDSA"
SUBJECT_KINDS = {"renter", "adapter", "skill", "agent", "human", "service"}
FORBIDDEN_AMBIENT_CAPABILITIES = {"admin", "all-access", "*"}


def _load_ed25519():
    mod_path = Path(__file__).resolve().parent / "ed25519_stdlib.py"
    spec = importlib.util.spec_from_file_location("kpgs_ed25519_stdlib", mod_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load ed25519_stdlib from {mod_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, module)
    spec.loader.exec_module(module)
    return module


_ED25519 = _load_ed25519()


class LeaseError(Exception):
    """Base class for fail-closed lease errors."""


class LeaseSignatureError(LeaseError):
    pass


class LeaseExpired(LeaseError):
    pass


class LeaseRevoked(LeaseError):
    pass


class LeaseDenied(LeaseError):
    pass


class LeaseReplay(LeaseDenied):
    pass


@dataclass(frozen=True)
class AuthorizationDecision:
    lease_id: str
    subject_id: str
    subject_kind: str
    tenant_id: str
    domain_id: str
    task_id: str
    capability: str
    resource_scope: str
    correlation_id: str
    key_id: str


class KeyRing:
    """Server-side signing/verification keys with explicit rotation (HS256)."""

    algorithm = TOKEN_ALG
    can_sign = True

    def __init__(self, keys: Mapping[str, bytes], active_key_id: str):
        self._keys: dict[str, bytes] = {}
        for key_id, key in keys.items():
            self._validate_key(key_id, key)
            self._keys[key_id] = bytes(key)
        if active_key_id not in self._keys:
            raise ValueError("active key id must exist in key ring")
        self._active_key_id = active_key_id

    @staticmethod
    def _validate_key(key_id: str, key: bytes) -> None:
        if not isinstance(key_id, str) or not key_id.strip():
            raise ValueError("key id is required")
        if not isinstance(key, (bytes, bytearray)) or len(key) < 32:
            raise ValueError("signing keys must contain at least 32 bytes")

    @property
    def active_key_id(self) -> str:
        return self._active_key_id

    def rotate(self, key_id: str, key: bytes) -> None:
        self._validate_key(key_id, key)
        self._keys[key_id] = bytes(key)
        self._active_key_id = key_id

    def retire(self, key_id: str) -> None:
        if key_id == self._active_key_id:
            raise ValueError("active signing key cannot be retired")
        self._keys.pop(key_id, None)

    def sign(self, key_id: str, message: bytes) -> bytes:
        key = self._keys.get(key_id)
        if key is None:
            raise LeaseSignatureError("unknown signing key")
        return hmac.new(key, message, hashlib.sha256).digest()

    def verify(self, key_id: str, message: bytes, signature: bytes) -> bool:
        key = self._keys.get(key_id)
        if key is None:
            return False
        expected = hmac.new(key, message, hashlib.sha256).digest()
        return hmac.compare_digest(expected, signature)


class Ed25519KeyRing:
    """Server-side Ed25519 signing/verification key ring (no shared secret in verifier)."""

    algorithm = EDDSA_ALG
    can_sign = True

    def __init__(self, private_seeds: Mapping[str, bytes], active_key_id: str):
        self._seeds: dict[str, bytes] = {}
        self._public_keys: dict[str, bytes] = {}
        for key_id, seed in private_seeds.items():
            self._validate_seed(key_id, seed)
            seed_bytes = bytes(seed)
            self._seeds[key_id] = seed_bytes
            self._public_keys[key_id] = _ED25519.public_key_from_seed(seed_bytes)
        if active_key_id not in self._seeds:
            raise ValueError("active key id must exist in key ring")
        self._active_key_id = active_key_id

    @staticmethod
    def _validate_seed(key_id: str, seed: bytes) -> None:
        if not isinstance(key_id, str) or not key_id.strip():
            raise ValueError("key id is required")
        if not isinstance(seed, (bytes, bytearray)) or len(seed) != 32:
            raise ValueError("Ed25519 signing seeds must contain exactly 32 bytes")

    @property
    def active_key_id(self) -> str:
        return self._active_key_id

    def rotate(self, key_id: str, seed: bytes) -> None:
        self._validate_seed(key_id, seed)
        seed_bytes = bytes(seed)
        self._seeds[key_id] = seed_bytes
        self._public_keys[key_id] = _ED25519.public_key_from_seed(seed_bytes)
        self._active_key_id = key_id

    def retire(self, key_id: str) -> None:
        if key_id == self._active_key_id:
            raise ValueError("active signing key cannot be retired")
        self._seeds.pop(key_id, None)
        self._public_keys.pop(key_id, None)

    def sign(self, key_id: str, message: bytes) -> bytes:
        seed = self._seeds.get(key_id)
        if seed is None:
            raise LeaseSignatureError("unknown Ed25519 signing key")
        return _ED25519.sign(seed, message)

    def verify(self, key_id: str, message: bytes, signature: bytes) -> bool:
        pub = self._public_keys.get(key_id)
        if pub is None:
            return False
        return _ED25519.verify(pub, message, signature)

    def export_public_keys(self) -> dict[str, bytes]:
        return dict(self._public_keys)

    def export_public_keys_hex(self) -> dict[str, str]:
        return {k: v.hex() for k, v in self._public_keys.items()}


class Ed25519PublicKeyRing:
    """Verifier-only Ed25519 public key ring holding zero signing authority."""

    algorithm = EDDSA_ALG
    can_sign = False

    def __init__(self, public_keys: Mapping[str, bytes]):
        if not public_keys:
            raise ValueError("at least one Ed25519 public verifying key is required")
        self._public_keys: dict[str, bytes] = {}
        for key_id, pub in public_keys.items():
            if not isinstance(key_id, str) or not key_id.strip():
                raise ValueError("key id is required")
            if not isinstance(pub, (bytes, bytearray)) or len(pub) != 32:
                raise ValueError("Ed25519 public keys must contain exactly 32 bytes")
            self._public_keys[key_id] = bytes(pub)

    def sign(self, key_id: str, message: bytes) -> bytes:
        raise LeaseSignatureError("verifier-only Ed25519 public key ring cannot sign leases")

    def verify(self, key_id: str, message: bytes, signature: bytes) -> bool:
        pub = self._public_keys.get(key_id)
        if pub is None:
            return False
        return _ED25519.verify(pub, message, signature)


def _b64encode(value: bytes) -> str:
    return urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    try:
        return urlsafe_b64decode(value + padding)
    except Exception as exc:
        raise LeaseSignatureError("invalid compact-token encoding") from exc


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _iso8601(value: datetime) -> str:
    normalized = value.astimezone(timezone.utc).replace(microsecond=0)
    return normalized.isoformat().replace("+00:00", "Z")


def _parse_time(value: Any, field_name: str) -> datetime:
    if not isinstance(value, str):
        raise LeaseDenied(f"{field_name} must be an ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise LeaseDenied(f"{field_name} is invalid") from exc
    if parsed.tzinfo is None:
        raise LeaseDenied(f"{field_name} must include timezone")
    return parsed.astimezone(timezone.utc)


class CapabilityLeaseAuthority:
    """Issue, verify, revoke and authorize short-lived capability leases."""

    def __init__(
        self,
        key_ring: KeyRing | Ed25519KeyRing | Ed25519PublicKeyRing,
        *,
        issuer: str = "kpgs-sovereign-hub",
        max_ttl_seconds: int = 900,
        clock: Callable[[], datetime] | None = None,
        restriction_ledger_path: Path | str | None = None,
        restriction_hmac_key: bytes | None = None,
        restriction_public_keys: Mapping[str, bytes] | None = None,
    ):
        if max_ttl_seconds <= 0:
            raise ValueError("max_ttl_seconds must be positive")
        self.key_ring = key_ring
        self.issuer = issuer
        self.max_ttl_seconds = max_ttl_seconds
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._restriction_ledger_path = Path(restriction_ledger_path) if restriction_ledger_path else None
        self._restriction_public_keys: dict[str, bytes] | None = (
            {k: bytes(v) for k, v in restriction_public_keys.items()}
            if restriction_public_keys
            else None
        )
        if restriction_hmac_key is not None:
            self._restriction_hmac_key: bytes | None = restriction_hmac_key
        elif hasattr(self.key_ring, "_keys") and getattr(self.key_ring, "can_sign", False):
            self._restriction_hmac_key = self.key_ring._keys[self.key_ring.active_key_id]
        else:
            self._restriction_hmac_key = None
        if self._restriction_ledger_path is not None and not self._restriction_public_keys and not self._restriction_hmac_key:
            raise LeaseDenied("restriction ledger verification requires public keys or verification key")
        self._revocations: dict[str, dict[str, str]] = {}
        self._operation_nonces: set[tuple[str, str]] = set()
        self._issued_nonces: set[str] = set()
        self._audit_log: list[dict[str, Any]] = []

    @staticmethod
    def _reject_dup_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        record: dict[str, Any] = {}
        for k, v in pairs:
            if k in record:
                raise LeaseDenied(f"restriction_ledger_tampered: duplicate JSON key {k!r}")
            record[k] = v
        return record

    def _load_and_verify_restriction_entries(self) -> list[dict[str, Any]]:
        if not self._restriction_ledger_path or not self._restriction_ledger_path.is_file():
            return []
        entries: list[dict[str, Any]] = []
        prev_hash = "GENESIS"
        try:
            raw_lines = self._restriction_ledger_path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise LeaseDenied(f"restriction_ledger_unreadable: {exc}") from exc
        for idx, line in enumerate(raw_lines):
            if not line.strip():
                continue
            try:
                row = json.loads(line, object_pairs_hook=self._reject_dup_keys)
            except LeaseDenied:
                raise
            except Exception as exc:
                raise LeaseDenied(f"restriction_ledger_tampered at line {idx + 1}") from exc
            if not isinstance(row, dict) or row.get("prev_entry_sha256") != prev_hash:
                raise LeaseDenied(f"restriction_ledger_tampered at line {idx + 1}: broken hash chain")
            filtered = {
                k: v
                for k, v in row.items()
                if k not in {"entry_sha256", "hmac_sha256", "ed25519_sig"}
            }
            canonical = json.dumps(filtered, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
            expected_sha = hashlib.sha256(canonical).hexdigest()
            if not hmac.compare_digest(str(row.get("entry_sha256", "")), expected_sha):
                raise LeaseDenied(f"restriction_ledger_tampered at line {idx + 1}: entry_sha256 mismatch")

            if self._restriction_public_keys is not None:
                kid = str(row.get("ed25519_kid", ""))
                sig_hex = str(row.get("ed25519_sig", ""))
                pub = self._restriction_public_keys.get(kid)
                if pub is None or not sig_hex:
                    raise LeaseDenied(f"restriction_ledger_tampered at line {idx + 1}: missing or untrusted ed25519 signature")
                try:
                    sig_bytes = bytes.fromhex(sig_hex)
                except ValueError as exc:
                    raise LeaseDenied(f"restriction_ledger_tampered at line {idx + 1}: invalid ed25519 hex") from exc
                if not _ED25519.verify(pub, canonical, sig_bytes):
                    raise LeaseDenied(f"restriction_ledger_tampered at line {idx + 1}: ed25519 signature mismatch")
            elif self._restriction_hmac_key is not None:
                expected_hmac = hmac.new(self._restriction_hmac_key, canonical, hashlib.sha256).hexdigest()
                if not hmac.compare_digest(str(row.get("hmac_sha256", "")), expected_hmac):
                    raise LeaseDenied(f"restriction_ledger_tampered at line {idx + 1}: hmac_sha256 mismatch")
            else:
                raise LeaseDenied("restriction_ledger_tampered: no trusted verifier configured")

            prev_hash = expected_sha
            entries.append(row)
        return entries

    def _assert_not_restricted(
        self,
        *,
        subject_id: str,
        domain_id: str,
        capabilities: Iterable[str],
    ) -> None:
        entries = self._load_and_verify_restriction_entries()
        if not entries:
            return
        lifted_receipts = {
            str(e.get("receipt_id"))
            for e in entries
            if e.get("status") == "RESTRICTION_LIFTED" and e.get("subject_id") == subject_id
        }
        req_caps = {str(c).strip() for c in capabilities if str(c).strip()}
        for entry in entries:
            if entry.get("status") != "RESTRICTED":
                continue
            if entry.get("subject_id") != subject_id:
                continue
            receipt_id = str(entry.get("receipt_id", ""))
            if receipt_id in lifted_receipts:
                continue
            entry_domain = str(entry.get("domain_id", ""))
            if entry_domain not in {"*", domain_id}:
                continue
            entry_caps = {str(c).strip() for c in (entry.get("capabilities") or [])}
            if "*" in entry_caps or (req_caps & entry_caps):
                raise LeaseDenied(
                    f"subject {subject_id!r} restricted by validated failure receipt {receipt_id!r}"
                )

    @staticmethod
    def _validate_capabilities(capabilities: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for item in capabilities:
            name = item.get("name")
            resource_scope = item.get("resource_scope")
            constraints = item.get("constraints", [])
            if not isinstance(name, str) or len(name.strip()) < 3:
                raise LeaseDenied("capability name is required")
            if name in FORBIDDEN_AMBIENT_CAPABILITIES:
                raise LeaseDenied("ambient capability names are forbidden")
            if not isinstance(resource_scope, str) or not resource_scope.strip():
                raise LeaseDenied("resource scope is required")
            if resource_scope.strip() == "*":
                raise LeaseDenied("wildcard resource scope is forbidden")
            if not isinstance(constraints, list) or not all(
                isinstance(value, str) and value.strip() for value in constraints
            ):
                raise LeaseDenied("capability constraints must be non-empty strings")
            normalized.append(
                {
                    "name": name.strip(),
                    "resource_scope": resource_scope.strip(),
                    "constraints": list(constraints),
                }
            )
        if not normalized:
            raise LeaseDenied("at least one capability is required")
        return normalized

    @staticmethod
    def _validate_secret_provider_refs(refs: Iterable[str]) -> list[str]:
        normalized: list[str] = []
        for ref in refs:
            if not isinstance(ref, str) or "://" not in ref:
                raise LeaseDenied(
                    "secret provider references must be URI-like references, not raw secret material"
                )
            normalized.append(ref)
        return normalized

    def _new_nonce(self) -> str:
        while True:
            nonce = secrets.token_urlsafe(18)
            if nonce not in self._issued_nonces:
                self._issued_nonces.add(nonce)
                return nonce

    def _record_audit(
        self,
        *,
        event: str,
        outcome: str,
        reason: str,
        lease: Mapping[str, Any] | None = None,
        capability: str | None = None,
        resource_scope: str | None = None,
        correlation_id: str = "",
        evidence_ref: str = "",
        key_id: str = "",
    ) -> None:
        subject = lease.get("subject", {}) if lease else {}
        self._audit_log.append(
            {
                "schema": "kpgs.capability-audit.v1",
                "event": event,
                "outcome": outcome,
                "reason": reason,
                "lease_id": lease.get("lease_id") if lease else None,
                "subject_id": subject.get("id") if isinstance(subject, dict) else None,
                "subject_kind": subject.get("kind") if isinstance(subject, dict) else None,
                "tenant_id": lease.get("tenant_id") if lease else None,
                "domain_id": lease.get("domain_id") if lease else None,
                "task_id": lease.get("task_id") if lease else None,
                "capability": capability,
                "resource_scope": resource_scope,
                "correlation_id": correlation_id,
                "evidence_ref": evidence_ref,
                "key_id": key_id,
                "at": _iso8601(self._clock()),
            }
        )

    def issue(
        self,
        *,
        subject_id: str,
        subject_kind: str,
        tenant_id: str,
        domain_id: str,
        task_id: str,
        capabilities: Iterable[Mapping[str, Any]],
        policy_decision_ref: str,
        governing_spec_ref: str,
        ttl_seconds: int = 300,
        secret_provider_refs: Iterable[str] = (),
        correlation_id: str = "",
        evidence_ref: str = "",
    ) -> str:
        if not getattr(self.key_ring, "can_sign", True):
            raise LeaseSignatureError("verifier-only authority cannot issue capability leases")
        if subject_kind not in SUBJECT_KINDS:
            raise LeaseDenied("unsupported subject kind")
        for label, value in {
            "subject_id": subject_id,
            "tenant_id": tenant_id,
            "domain_id": domain_id,
            "task_id": task_id,
            "policy_decision_ref": policy_decision_ref,
            "governing_spec_ref": governing_spec_ref,
        }.items():
            if not isinstance(value, str) or not value.strip():
                raise LeaseDenied(f"{label} is required")
        if ttl_seconds <= 0 or ttl_seconds > self.max_ttl_seconds:
            raise LeaseDenied("lease TTL exceeds the short-lived authority boundary")

        issued_at = self._clock().astimezone(timezone.utc)
        expires_at = issued_at + timedelta(seconds=ttl_seconds)
        lease_id = "lease_" + secrets.token_urlsafe(18)
        nonce = self._new_nonce()
        capability_list = self._validate_capabilities(capabilities)
        self._assert_not_restricted(
            subject_id=subject_id,
            domain_id=domain_id,
            capabilities=[c["name"] for c in capability_list],
        )
        provider_refs = self._validate_secret_provider_refs(secret_provider_refs)

        payload: dict[str, Any] = {
            "lease_id": lease_id,
            "subject": {"id": subject_id, "kind": subject_kind},
            "tenant_id": tenant_id,
            "domain_id": domain_id,
            "task_id": task_id,
            "capabilities": capability_list,
            "issued_at": _iso8601(issued_at),
            "expires_at": _iso8601(expires_at),
            "nonce": nonce,
            "policy_decision_ref": policy_decision_ref,
            "governing_spec_ref": governing_spec_ref,
            "secret_provider_refs": provider_refs,
            "audit": {
                "correlation_id": correlation_id or f"corr:{lease_id}",
                "evidence_ref": evidence_ref or f"evidence:{lease_id}",
            },
        }
        token = self._encode(payload)
        self._record_audit(
            event="lease-issued",
            outcome="allow",
            reason="short-lived scoped lease issued",
            lease=payload,
            correlation_id=payload["audit"]["correlation_id"],
            evidence_ref=payload["audit"]["evidence_ref"],
            key_id=self.key_ring.active_key_id,
        )
        return token

    def _encode(self, payload: Mapping[str, Any]) -> str:
        alg = getattr(self.key_ring, "algorithm", TOKEN_ALG)
        header = {
            "alg": alg,
            "typ": TOKEN_TYPE,
            "kid": self.key_ring.active_key_id,
            "iss": self.issuer,
        }
        encoded_header = _b64encode(_canonical_json(header))
        encoded_payload = _b64encode(_canonical_json(payload))
        signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
        signature = self.key_ring.sign(self.key_ring.active_key_id, signing_input)
        return f"{encoded_header}.{encoded_payload}.{_b64encode(signature)}"

    def verify(self, token: str) -> tuple[dict[str, Any], str]:
        if not isinstance(token, str) or len(token) > 32_768:
            raise LeaseSignatureError("invalid lease token")
        parts = token.split(".")
        if len(parts) != 3:
            raise LeaseSignatureError("invalid compact lease token")
        encoded_header, encoded_payload, encoded_signature = parts
        try:
            header = json.loads(_b64decode(encoded_header))
            payload = json.loads(_b64decode(encoded_payload))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise LeaseSignatureError("lease token JSON is invalid") from exc
        if not isinstance(header, dict) or not isinstance(payload, dict):
            raise LeaseSignatureError("lease token envelope is invalid")
        expected_alg = getattr(self.key_ring, "algorithm", TOKEN_ALG)
        if header.get("alg") != expected_alg or header.get("typ") != TOKEN_TYPE:
            raise LeaseSignatureError("unsupported lease token algorithm/type")
        if header.get("iss") != self.issuer:
            raise LeaseSignatureError("lease issuer mismatch")
        key_id = header.get("kid")
        if not isinstance(key_id, str) or not key_id:
            raise LeaseSignatureError("lease key id is missing")
        signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
        signature = _b64decode(encoded_signature)
        if not self.key_ring.verify(key_id, signing_input, signature):
            raise LeaseSignatureError("lease signature verification failed")

        issued_at = _parse_time(payload.get("issued_at"), "issued_at")
        expires_at = _parse_time(payload.get("expires_at"), "expires_at")
        now = self._clock().astimezone(timezone.utc)
        ttl = (expires_at - issued_at).total_seconds()
        if ttl <= 0 or ttl > self.max_ttl_seconds:
            raise LeaseDenied("lease lifetime violates short-lived authority policy")
        if now < issued_at:
            raise LeaseDenied("lease is not active yet")
        if now >= expires_at:
            raise LeaseExpired("lease expired")

        lease_id = payload.get("lease_id")
        if not isinstance(lease_id, str) or not lease_id:
            raise LeaseDenied("lease identity is missing")
        if lease_id in self._revocations:
            raise LeaseRevoked("lease revoked")
        subject = payload.get("subject") if isinstance(payload.get("subject"), dict) else {}
        caps = [
            str(item.get("name", ""))
            for item in (payload.get("capabilities") or [])
            if isinstance(item, dict)
        ]
        self._assert_not_restricted(
            subject_id=str(subject.get("id", "")),
            domain_id=str(payload.get("domain_id", "")),
            capabilities=caps,
        )
        nonce = payload.get("nonce")
        if not isinstance(nonce, str) or len(nonce) < 8:
            raise LeaseDenied("lease nonce is missing")
        return payload, key_id

    def authorize(
        self,
        token: str,
        *,
        tenant_id: str,
        domain_id: str,
        task_id: str,
        capability: str,
        resource_scope: str,
        operation_nonce: str,
        correlation_id: str,
    ) -> AuthorizationDecision:
        lease: dict[str, Any] | None = None
        key_id = ""
        try:
            lease, key_id = self.verify(token)
            expected = {
                "tenant_id": tenant_id,
                "domain_id": domain_id,
                "task_id": task_id,
            }
            for field_name, value in expected.items():
                if lease.get(field_name) != value:
                    raise LeaseDenied(f"{field_name} scope mismatch")

            admitted = any(
                item.get("name") == capability
                and item.get("resource_scope") == resource_scope
                for item in lease.get("capabilities", [])
                if isinstance(item, dict)
            )
            if not admitted:
                raise LeaseDenied("capability/resource scope denied")
            if not isinstance(operation_nonce, str) or len(operation_nonce) < 8:
                raise LeaseDenied("operation nonce is required")

            replay_key = (lease["lease_id"], operation_nonce)
            if replay_key in self._operation_nonces:
                raise LeaseReplay("operation nonce replay detected")
            self._operation_nonces.add(replay_key)

            audit = lease.get("audit", {})
            evidence_ref = audit.get("evidence_ref", "") if isinstance(audit, dict) else ""
            self._record_audit(
                event="capability-used",
                outcome="allow",
                reason="lease and exact resource scope admitted",
                lease=lease,
                capability=capability,
                resource_scope=resource_scope,
                correlation_id=correlation_id,
                evidence_ref=evidence_ref,
                key_id=key_id,
            )
            subject = lease["subject"]
            return AuthorizationDecision(
                lease_id=lease["lease_id"],
                subject_id=subject["id"],
                subject_kind=subject["kind"],
                tenant_id=tenant_id,
                domain_id=domain_id,
                task_id=task_id,
                capability=capability,
                resource_scope=resource_scope,
                correlation_id=correlation_id,
                key_id=key_id,
            )
        except LeaseError as exc:
            self._record_audit(
                event="capability-used",
                outcome="deny",
                reason=type(exc).__name__,
                lease=lease,
                capability=capability,
                resource_scope=resource_scope,
                correlation_id=correlation_id,
                key_id=key_id,
            )
            raise

    def revoke(self, token_or_lease_id: str, *, reason: str, evidence_ref: str) -> str:
        if not reason.strip() or not evidence_ref.strip():
            raise LeaseDenied("revocation requires reason and evidence reference")
        lease: dict[str, Any] | None = None
        key_id = ""
        lease_id = token_or_lease_id
        if "." in token_or_lease_id:
            lease, key_id = self.verify(token_or_lease_id)
            lease_id = lease["lease_id"]
        self._revocations[lease_id] = {
            "reason": reason,
            "evidence_ref": evidence_ref,
            "revoked_at": _iso8601(self._clock()),
        }
        self._record_audit(
            event="lease-revoked",
            outcome="allow",
            reason=reason,
            lease=lease or {"lease_id": lease_id},
            evidence_ref=evidence_ref,
            key_id=key_id,
        )
        return lease_id

    def audit_events(self) -> tuple[dict[str, Any], ...]:
        return tuple(dict(event) for event in self._audit_log)
