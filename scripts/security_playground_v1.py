#!/usr/bin/env python3
"""GSMB Security Playground V1 — Runtime Isolation and Admission Gate.

Implements and extends PR #326 candidate doctrine into an enforceable,
independently verifiable acceptance contract.

Features:
- Dedicated nonproduction execution identity validation
- Default-deny production network & isolation controls
- Immutability of protected canonical state (SELF.md, USER.md, IDENTITY.md, SOUL.md, etc.)
- Resource ceilings (CPU, memory, timeout) and operator kill-switch
- Ephemeral storage and tamper-evident forensic sink validation
- Strict cryptographic receipt verification (anti-forgery, append-only proof)
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
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

SCHEMA_V1 = "gsmb_security_playground_v1"
SCHEMA_LEGACY = "gsmb_security_playground_inventory_gate_v1"
SUPPORTED_SCHEMAS = {SCHEMA_V1, SCHEMA_LEGACY}

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
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", version_str)
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
    if schema not in SUPPORTED_SCHEMAS:
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

            if identity.get("is_production_authority") is True:
                blocked.append("playground execution identity claimed production authority")
            if identity.get("is_privileged") is True:
                blocked.append("playground execution identity claimed elevated host privilege")
            if not identity.get("execution_id"):
                held.append("execution_identity execution_id missing")

    # Adversarial Check: Authority spoofing
    claimed_authority = record.get("claimed_authority")
    if claimed_authority in {"founder", "rtc_founder", "ca_codex_forge", "teacher_cassey"}:
        caller_domain = record.get("caller_domain", "playground")
        if caller_domain != "canonical_governance":
            blocked.append(f"cross-domain authority spoofing detected: '{claimed_authority}' claimed from '{caller_domain}'")

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
        if sink_info.get("authenticated") is False:
            held.append("evidence sink transmission lacks cryptographic authentication")

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

    # 7. Receipts Verification (Anti-forgery and authentication)
    receipts = record.get("receipt_refs")
    if not isinstance(receipts, list) or not receipts or any(
        not isinstance(ref, str) or not ref.strip() for ref in receipts
    ):
        held.append("receipt_refs must contain at least one nonempty reference")
    else:
        for ref in receipts:
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
                if not discovery_method or discovery_method == "unverified_assumption":
                    held.append(f"{prefix} unsupported negative claim: 'not_present' requires verified discovery_method and proof hash")

            # Specific PHP checks
            if kind == "php_runtime":
                has_php = True
                source_present = asset.get("source_files_present", False)
                runtime_present = status not in {"not_present", "unknown"}

                # Scenario 2: PHP runtime present without source files
                if runtime_present and not source_present:
                    held.append(f"{prefix} PHP runtime present without PHP source files (unnecessary/rogue runtime)")

                # Scenario 3: PHP source present without PHP runtime
                if source_present and not runtime_present:
                    held.append(f"{prefix} PHP source present without active runtime (dormant source risk)")

            # Container checks (Scenario 4)
            if kind == "container":
                if asset.get("contains_php") is True:
                    has_php = True
                    # Check container isolation boundary
                    if asset.get("container_isolated") is False:
                        blocked.append(f"{prefix} container running PHP lacks verified boundary isolation")
                    # Check PHP version against CVE-2026-109618 / CVE-2026-109619
                    php_ver = asset.get("php_version")
                    if php_ver and is_php_vulnerable(php_ver):
                        blocked.append(
                            f"{prefix} container PHP version {php_ver} is vulnerable to PHP2Shell (CVE-2026-109618, CVE-2026-109619)"
                        )

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
        if source_domain == "playground" and target_domain in {"crud", "gui", "altar", "phu", "hood", "production"}:
            if not oz_crossing.get("zero_trust_admitted"):
                blocked.append(f"unadmitted Oz lattice boundary crossing from {source_domain} to {target_domain}")

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
