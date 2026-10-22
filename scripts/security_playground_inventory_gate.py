#!/usr/bin/env python3
"""Read-only Security Playground asset-inventory admission gate.

This tool evaluates a supplied evidence *claim*. It never discovers live assets,
creates a sandbox, validates a cloud control plane, or authorizes production.
Exit: 0=fixture DRILL_PASS, 2=HOLD/review required, 3=BLOCK, 4=invalid input.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCHEMA = "gsmb_security_playground_inventory_gate_v1"
ISOLATION_CONTROLS = (
    "dedicated_isolation_domain",
    "deny_production_network",
    "production_credentials_absent",
    "production_state_readonly",
    "ephemeral_storage",
)
VALID_MODES = {"fixture", "cloud", "local"}
VALID_KINDS = {"php_runtime", "dependency", "service", "container"}
VALID_STATUSES = {"patched", "not_present", "vulnerable", "unknown"}


def evaluate(record: object) -> dict:
    """Return a bounded disposition; claims are not independent attestations."""
    if not isinstance(record, dict):
        return {"verdict": "BLOCK", "reasons": ["input must be a JSON object"],
                "runtime_verified": False}
    blocked: list[str] = []
    held: list[str] = []
    mode = record.get("mode")
    if record.get("schema") != SCHEMA:
        held.append("schema is missing or unsupported")
    if not isinstance(mode, str) or mode not in VALID_MODES:
        held.append("mode must be fixture, cloud or local")
    revision = record.get("source_revision")
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", revision):
        held.append("source_revision must be a 40-character Git SHA")
    isolation = record.get("isolation")
    if not isinstance(isolation, dict):
        held.append("isolation control assertions are missing")
    else:
        for control in ISOLATION_CONTROLS:
            value = isolation.get(control)
            if value is False:
                blocked.append(f"isolation control explicitly failed: {control}")
            elif value is not True:
                held.append(f"isolation control unverified: {control}")
        if not isinstance(isolation.get("evidence_ref"), str) or not isolation["evidence_ref"].strip():
            held.append("isolation evidence_ref missing")
    mutations = record.get("protected_state_mutations")
    if type(mutations) is not int or mutations < 0:
        held.append("protected_state_mutations must be a nonnegative integer")
    elif mutations:
        blocked.append("attempted protected-state mutation detected")
    assets = record.get("assets")
    if not isinstance(assets, list) or not assets:
        held.append("asset inventory is empty or missing")
    else:
        has_php = False
        ids: set[str] = set()
        for index, asset in enumerate(assets):
            prefix = f"asset[{index}]"
            if not isinstance(asset, dict):
                held.append(f"{prefix} is not an object")
                continue
            asset_id = asset.get("id")
            if not isinstance(asset_id, str) or not asset_id.strip():
                held.append(f"{prefix} missing id")
            elif asset_id in ids:
                held.append(f"{prefix} duplicate id")
            else:
                ids.add(asset_id)
            kind = asset.get("kind")
            if not isinstance(kind, str) or kind not in VALID_KINDS:
                held.append(f"{prefix} kind unknown")
            if kind == "php_runtime":
                has_php = True
            status = asset.get("status")
            if status == "vulnerable":
                blocked.append(f"{prefix} has vulnerable status")
            elif status == "unknown":
                held.append(f"{prefix} status unknown")
            elif not isinstance(status, str) or status not in VALID_STATUSES:
                held.append(f"{prefix} status invalid")
            if not isinstance(asset.get("evidence_ref"), str) or not asset["evidence_ref"].strip():
                held.append(f"{prefix} evidence_ref missing")
        if not has_php:
            held.append("explicit PHP runtime inventory record required, including not_present")
    receipts = record.get("receipt_refs")
    if not isinstance(receipts, list) or not receipts or any(
        not isinstance(ref, str) or not ref.strip() for ref in receipts
    ):
        held.append("receipt_refs must contain at least one nonempty reference")
    if blocked:
        verdict, reasons = "BLOCK", blocked + held
    elif held:
        verdict, reasons = "HOLD", held
    elif mode == "fixture":
        verdict, reasons = "DRILL_PASS", [
            "fixture admission assertions passed; no live isolation or runtime verified"
        ]
    else:
        verdict, reasons = "HOLD", [
            "real-environment claims require independent control-plane and runtime review"
        ]
    return {"schema": SCHEMA, "mode": mode, "verdict": verdict, "reasons": reasons,
            "runtime_verified": False, "production_authority": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Read-only JSON evidence claim")
    args = parser.parse_args()
    try:
        record = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(json.dumps({"verdict": "BLOCK", "error": type(exc).__name__,
                          "runtime_verified": False}), sort_keys=True)
        return 4
    result = evaluate(record)
    print(json.dumps(result, sort_keys=True))
    return {"DRILL_PASS": 0, "HOLD": 2, "BLOCK": 3}[result["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
