#!/usr/bin/env python3
"""GSMB Security Playground V1 — read-only synthetic admission evaluator.

Evaluates caller-supplied assertions under PR #326's candidate contract.
No host controls, Git objects, signatures, receipts or runtime are authenticated.
Only explicit fixture:// references are accepted for synthetic drills; real
evidence and teacher acknowledgements remain HOLD pending a trusted verifier.

Features:
- Dedicated nonproduction execution identity validation
- Default-deny production network & isolation controls
- Immutability of protected canonical state (SELF.md, USER.md, IDENTITY.md, SOUL.md, etc.)
- Resource ceilings (CPU, memory, timeout) and operator kill-switch
- Ephemeral storage and tamper-evident forensic sink validation
- Explicit synthetic-reference policy (no cryptographic attestation)
- Anti-spoofing firewall: blocks cross-domain teacher/founder/CA impersonation
- Rigorous negative asset assertion validation (absence of evidence is not proof of absence)
- PHP2Shell scenario handling (CVE-2026-109618, CVE-2026-109619) with founder reclassifications:
    * Local GSMB: PARTIAL_INVENTORY / HOLD
    * Cloud GSMB: SOURCE_NO_PHP_OBSERVED / RUNTIME_HOLD
    * Production IONOS: HOLD
- Oz structural lattice boundary enforcement (default-deny egress)
- Zero Trust & PKA uncertainty preservation (never promote drill to production)
- Mandatory governance chain: Cassy -> Cassey -> KC -> Founder/RTC

Exit codes:
  0: DRILL_PASS (fixture drill pass; never production graduation)
  2: HOLD (evidence unverified, unknown status, review required)
  3: BLOCK (explicit failure, vulnerable asset, isolation breach, spoofing attempt)
  4: INVALID_INPUT (schema or structural validation error)
"""
from __future__ import annotations

import argparse
import math
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

SCHEMA_V1 = "gsmb_security_playground_v1"
SCHEMA_LEGACY = "gsmb_security_playground_inventory_gate_v1"
SUPPORTED_SCHEMAS = {SCHEMA_V1}

# Local fixture policy, not provider resource limits or runtime enforcement.
RESOURCE_MAXIMA = {"cpu_cores": 2, "memory_mb": 2048, "timeout_sec": 300}

VALID_MODES = {"fixture", "cloud", "local"}
VALID_KINDS = {"php_runtime", "dependency", "service", "container"}
VALID_STATUSES = {"patched", "not_present", "vulnerable", "unknown"}

REQUIRED_ISOLATION_CONTROLS = (
    "dedicated_isolation_domain",
    "deny_production_network",
    "production_credentials_absent",
    "production_state_readonly",
    "ephemeral_storage",
    "resource_ceilings_enforced",
    "kill_switch_active",
    "tamper_evident_sink",
)

LEGACY_ISOLATION_CONTROLS = (
    "dedicated_isolation_domain",
    "deny_production_network",
    "production_credentials_absent",
    "production_state_readonly",
    "ephemeral_storage",
)

PROTECTED_CANON_FILES = {
    "SELF.md",
    "USER.md",
    "IDENTITY.md",
    "SOUL.md",
    "world canon",
    "relationship canon",
    "production credentials",
    "production authority",
    "governance policy",
}

# Vulnerable PHP versions (< 8.2.35, 8.3.36, 8.4.27, 8.5.12)
PHP_FIXED_VERSIONS = {
    "8.2": (8, 2, 35),
    "8.3": (8, 3, 36),
    "8.4": (8, 4, 27),
    "8.5": (8, 5, 12),
}

# Known synthetic test revisions allowed in fixture mode only
SYNTHETIC_TEST_REVISIONS = {"a" * 40, "b" * 40}


def parse_semver(version_str: str) -> Optional[Tuple[int, int, int]]:
    if not isinstance(version_str, str):
        return None
    match = re.fullmatch(r"([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,4})", version_str)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def is_php_vulnerable(version_str: str) -> bool:
    parsed = parse_semver(version_str)
    if not parsed:
        return True
    major, minor, patch = parsed
    branch = f"{major}.{minor}"
    if branch in PHP_FIXED_VERSIONS:
        min_ver = PHP_FIXED_VERSIONS[branch]
        return (major, minor, patch) < min_ver
    # Older branches (5.x, 7.x, 8.0, 8.1) are all vulnerable to PHP2Shell
    if major < 8 or (major == 8 and minor < 2):
        return True
    return False


def _check_php_version(asset: dict, prefix: str, held: list, blocked: list) -> None:
    """Compare synthetic upstream versions; vendor backports require review."""
    version = asset.get("php_version")
    parsed = parse_semver(version)
    if parsed is None:
        held.append(f"{prefix} php_version must be an explicit upstream major.minor.patch string")
    elif f"{parsed[0]}.{parsed[1]}" not in PHP_FIXED_VERSIONS:
        held.append(f"{prefix} PHP branch patch provenance unsupported; independent review required")
    elif is_php_vulnerable(version):
        blocked.append(f"{prefix} PHP version {version} is below upstream fixes for CVE-2026-109618 / CVE-2026-109619")


def evaluate_playground(record: object) -> Dict[str, Any]:
    """Evaluate Security Playground evidence claim and return bounded disposition."""
    if not isinstance(record, dict):
        return {
            "verdict": "BLOCK",
            "reasons": ["input must be a JSON object"],
            "runtime_verified": False,
            "production_authority": False,
            "exit_code": 4,
        }

    blocked: List[str] = []
    held: List[str] = []

    schema = record.get("schema")
    if not isinstance(schema, str) or schema not in SUPPORTED_SCHEMAS:
        held.append(f"schema is missing or unsupported: expected one of {sorted(SUPPORTED_SCHEMAS)}")

    mode = record.get("mode")
    if not isinstance(mode, str) or mode not in VALID_MODES:
        held.append("mode must be fixture, cloud or local")

    revision = record.get("source_revision")
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", revision):
        held.append("source_revision must be a 40-character Git SHA")
    else:
        # Adversarial Check: Fabricated revision check
        if record.get("revision_verified_in_git") is False:
            held.append(f"source_revision {revision[:8]} is not verified in git object database")
        elif revision in {"0" * 40, "f" * 40}:
            blocked.append(f"fabricated placeholder git revision: {revision}")
        elif mode != "fixture" and revision in SYNTHETIC_TEST_REVISIONS:
            blocked.append(f"synthetic fixture revision used outside fixture mode: {revision}")

    # 1. Nonproduction execution identity & Cross-domain authority spoofing
    identity = record.get("execution_identity")
    if schema == SCHEMA_V1:
        if not isinstance(identity, dict):
            held.append("execution_identity assertion missing")
        else:
            role = identity.get("role")
            if not isinstance(role, str) or not role.strip():
                held.append("execution_identity role missing")
            elif role in {"production", "root", "admin", "canonical_landlord"}:
                blocked.append(f"prohibited privileged execution identity in playground: {role}")

            for flag in ("is_production_authority", "is_privileged"):
                if identity.get(flag) is True:
                    blocked.append(f"playground execution identity claimed prohibited {flag}")
                elif identity.get(flag) is not False:
                    held.append(f"execution_identity {flag} requires explicit boolean false")
            if not isinstance(identity.get("execution_id"), str) or not identity["execution_id"].strip():
                held.append("execution_identity execution_id missing")

    # Adversarial Check: Authority spoofing
    claimed_authority = record.get("claimed_authority")
    if "claimed_authority" in record:
        if not isinstance(claimed_authority, str):
            held.append("claimed_authority must be a string")
        elif claimed_authority in {"founder", "rtc_founder", "ca_codex_forge", "teacher_cassey"}:
            blocked.append(f"cross-domain authority spoofing detected: '{claimed_authority}' cannot be granted by caller_domain")

    if schema == SCHEMA_V1:
        ceilings = record.get("resource_ceilings")
        if not isinstance(ceilings, dict):
            held.append("resource_ceilings object required")
        else:
            for field, maximum in RESOURCE_MAXIMA.items():
                value = ceilings.get(field)
                if type(value) not in (int, float) or (type(value) is float and not math.isfinite(value)) or value <= 0:
                    held.append(f"resource_ceilings {field} must be finite and positive")
                elif value > maximum:
                    blocked.append(f"resource_ceilings {field} exceeds fixture policy maximum {maximum}")

    # 2. Kill switch assertion
    kill_switch = record.get("kill_switch")
    if isinstance(kill_switch, dict) and kill_switch.get("triggered") is True:
        blocked.append(f"kill switch actively triggered: {kill_switch.get('reason', 'operator abort')}")

    # 3. Isolation controls verification
    isolation = record.get("isolation")
    controls_to_check = REQUIRED_ISOLATION_CONTROLS if schema == SCHEMA_V1 else LEGACY_ISOLATION_CONTROLS
    if not isinstance(isolation, dict):
        held.append("isolation control assertions are missing")
    else:
        for control in controls_to_check:
            value = isolation.get(control)
            if value is False:
                blocked.append(f"isolation control explicitly failed: {control}")
            elif value is not True:
                held.append(f"isolation control unverified: {control}")
        if not isinstance(isolation.get("evidence_ref"), str) or not isolation["evidence_ref"].strip():
            held.append("isolation evidence_ref missing")

    # 4. Evidence Sink Integrity & Tamper-Resistance
    sink_info = record.get("evidence_sink")
    if isinstance(sink_info, dict):
        if sink_info.get("compromised") is True:
            blocked.append("evidence sink is marked compromised or integrity validation failed")
        if sink_info.get("mutable_storage") is True:
            blocked.append("evidence sink permits mutable overwrites (append-only/tamper-evident sink required)")
        if schema == SCHEMA_V1:
            for field, expected in (("compromised", False), ("mutable_storage", False),
                                    ("tamper_evident", True), ("authenticated", True)):
                value = sink_info.get(field)
                if type(value) is not bool:
                    held.append(f"evidence_sink {field} requires an explicit boolean")
                elif value is not expected:
                    blocked.append(f"evidence_sink {field} assertion failed")
            if not isinstance(sink_info.get("sink_id"), str) or not sink_info["sink_id"].strip():
                held.append("evidence_sink sink_id missing")
    elif schema == SCHEMA_V1:
        held.append("evidence_sink assertions required")

    # 5. Protected state mutation prevention
    mutations = record.get("protected_state_mutations")
    if type(mutations) is not int or mutations < 0:
        held.append("protected_state_mutations must be a nonnegative integer")
    elif mutations > 0:
        blocked.append(f"attempted protected-state mutation detected (count={mutations})")

    attempted_targets = record.get("protected_state_targets_attempted", [])
    if isinstance(attempted_targets, list) and attempted_targets:
        for target in attempted_targets:
            if any(p.lower() in str(target).lower() for p in PROTECTED_CANON_FILES):
                blocked.append(f"attempted mutation of protected canon state: {target}")

    # 6. Prevention of evidence self-promotion
    if record.get("promote_to_production") is True:
        blocked.append("attempted self-promotion of playground evidence to production authority")
    if record.get("production_authority_claimed") is True:
        blocked.append("unauthorized production authority claim")

    # 7. Synthetic reference policy; names and hashes never authenticate content.
    receipts = record.get("receipt_refs")
    if not isinstance(receipts, list) or not receipts or any(
        not isinstance(ref, str) or not ref.strip() for ref in receipts
    ):
        held.append("receipt_refs must contain at least one nonempty reference")
    else:
        for ref in receipts:
            if mode != "fixture" or not re.fullmatch(r"fixture://[A-Za-z0-9][A-Za-z0-9._/-]*", ref):
                held.append("receipt authentication unavailable: only synthetic fixture:// references may pass a drill")
            if "unverifiable" in ref or "fabricated" in ref or "forged" in ref:
                held.append(f"unverifiable or fabricated receipt reference: {ref}")
            if "raw_sha256_only" in ref:
                held.append(f"receipt {ref} lacks authentication envelope (SHA-256 alone is not authentication)")

    # Adversarial Check: False teacher acknowledgments
    teacher_ack = record.get("teacher_ack_claimed")
    if teacher_ack is True:
        review_packet = record.get("teacher_review_packet")
        if not isinstance(review_packet, dict) or not review_packet.get("teacher_signature"):
            blocked.append("false teacher acknowledgement: claimed teacher_ack without detached authenticated teacher_review_packet")
        else:
            held.append("teacher acknowledgement unverified: trusted evidence-bound signature verifier unavailable")
    elif teacher_ack is not None and teacher_ack is not False:
        held.append("teacher_ack_claimed must be a boolean")

    # 8. Asset inventory with positive and negative controls
    assets = record.get("assets")
    if not isinstance(assets, list) or not assets:
        held.append("asset inventory is empty or missing")
    else:
        has_php = False
        ids: Set[str] = set()
        for index, asset in enumerate(assets):
            prefix = f"asset[{index}]"
            if not isinstance(asset, dict):
                held.append(f"{prefix} is not an object")
                continue
            asset_id = asset.get("id")
            if not isinstance(asset_id, str) or not asset_id.strip():
                held.append(f"{prefix} missing id")
            elif asset_id in ids:
                held.append(f"{prefix} duplicate id: {asset_id}")
            else:
                ids.add(asset_id)

            kind = asset.get("kind")
            if not isinstance(kind, str) or kind not in VALID_KINDS:
                held.append(f"{prefix} kind unknown: {kind}")

            # Adversarial Check: False negative asset assertion
            status = asset.get("status")
            if status == "not_present":
                discovery_method = asset.get("discovery_method")
                if not isinstance(discovery_method, str) or not discovery_method.strip() or discovery_method == "unverified_assumption":
                    held.append(f"{prefix} unsupported negative claim: 'not_present' requires a discovery_method assertion")

            # Specific PHP checks
            if kind == "php_runtime":
                has_php = True
                source_present = asset.get("source_files_present")
                if type(source_present) is not bool:
                    held.append(f"{prefix} source_files_present requires an explicit boolean")
                runtime_present = isinstance(status, str) and status in {"patched", "vulnerable"}

                # Scenario 2: PHP runtime present without source files
                if runtime_present and not source_present:
                    held.append(f"{prefix} PHP runtime present without PHP source files (unnecessary/rogue runtime)")

                # Scenario 3: PHP source present without PHP runtime
                if source_present and not runtime_present:
                    held.append(f"{prefix} PHP source present without active runtime (dormant source risk)")
                if runtime_present:
                    _check_php_version(asset, prefix, held, blocked)

            # Container checks (Scenario 4)
            if kind == "container":
                if type(asset.get("contains_php")) is not bool:
                    held.append(f"{prefix} contains_php requires an explicit boolean")
                if asset.get("contains_php") is True:
                    has_php = True
                    # Check container isolation boundary
                    if asset.get("container_isolated") is False:
                        blocked.append(f"{prefix} container running PHP lacks verified boundary isolation")
                    elif asset.get("container_isolated") is not True:
                        held.append(f"{prefix} container_isolated requires explicit boolean true")
                    _check_php_version(asset, prefix, held, blocked)

            if status == "vulnerable":
                blocked.append(f"{prefix} has vulnerable status: {asset.get('vulnerability_id', 'unspecified')}")
            elif status == "unknown":
                held.append(f"{prefix} status unknown")
            elif not isinstance(status, str) or status not in VALID_STATUSES:
                held.append(f"{prefix} status invalid: {status}")

            if not isinstance(asset.get("evidence_ref"), str) or not asset["evidence_ref"].strip():
                held.append(f"{prefix} evidence_ref missing")

        if not has_php:
            held.append("explicit PHP runtime inventory record required, including not_present")

    # 9. Oz lattice boundary check
    oz_crossing = record.get("oz_boundary_crossing")
    if isinstance(oz_crossing, dict):
        source_domain = oz_crossing.get("source")
        target_domain = oz_crossing.get("target")
        if any(not isinstance(v, str) or not v.strip() for v in (source_domain, target_domain)):
            held.append("Oz crossing source and target must be nonempty strings")
        elif source_domain != "playground":
            held.append("Oz crossing source must be playground in this evaluator")
        elif target_domain != source_domain:
            if oz_crossing.get("zero_trust_admitted") is not True:
                blocked.append(f"unadmitted Oz lattice boundary crossing from {source_domain} to {target_domain}")
    elif oz_crossing is not None:
        held.append("oz_boundary_crossing must be an object")

    # Determine final verdict and exit code
    if blocked:
        verdict = "BLOCK"
        reasons = blocked + held
        exit_code = 3
    elif held:
        verdict = "HOLD"
        reasons = held
        exit_code = 2
    elif mode == "fixture":
        verdict = "DRILL_PASS"
        reasons = [
            "fixture admission assertions passed; harmless synthetic drill only; no live isolation or runtime verified"
        ]
        exit_code = 0
    else:
        verdict = "HOLD"
        reasons = [
            f"mode={mode} requires independent runtime containment verifier and human owner sign-off"
        ]
        exit_code = 2

    return {
        "schema": schema,
        "mode": mode,
        "source_revision": revision,
        "verdict": verdict,
        "exit_code": exit_code,
        "reasons": reasons,
        "runtime_verified": False,
        "production_authority": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", "-i", type=Path, help="Path to evidence JSON file (reads stdin if omitted)")
    args = parser.parse_args()

    try:
        raw = sys.stdin.read() if args.input is None else args.input.read_text(encoding="utf-8")
        record = json.loads(raw)
    except Exception as exc:
        output = {
            "verdict": "BLOCK",
            "reasons": [f"failed to parse JSON input: {exc}"],
            "runtime_verified": False,
            "production_authority": False,
            "exit_code": 4,
        }
        print(json.dumps(output, indent=2))
        return 4

    result = evaluate_playground(record)
    print(json.dumps(result, indent=2))
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
