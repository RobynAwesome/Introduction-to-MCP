#!/usr/bin/env python3
"""KPGS smoke PoC CLI — gate, steward activation, sovereign sim bootstrap."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.kpgs_activation_gate import load_cached_activation_gate  # noqa: E402
from kopano.kpgs_behavioral_poc import run_kpgs_behavioral_poc, run_sovereign_sim_tick  # noqa: E402
from kopano.kpgs_renter_entry import assert_and_log_entry  # noqa: E402
from kopano.sovereign_sim import (  # noqa: E402
    bootstrap_sovereign_sim,
    run_kpgs_smoke_poc,
    sovereign_sim_status,
    sovereign_sim_ui_snapshot,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="KPGS smoke PoC / activation gate")
    parser.add_argument(
        "command",
        choices=("gate", "smoke", "behavioral", "tick", "status", "ui", "bootstrap"),
        help="gate=cached read-only receipt; smoke=full PoC; behavioral=mechanical proofs; tick=sim tick; status=sim status; ui=GUI snapshot; bootstrap=world build",
    )
    parser.add_argument("--json", action="store_true", help="Print raw JSON")
    parser.add_argument("--renter-id", help="Required for every mutating command")
    parser.add_argument("--hood-ack", help="Exact canonical renter acknowledgement; never prefilled")
    args = parser.parse_args()

    hood_entry = None
    if args.command in ("smoke", "behavioral", "tick", "bootstrap"):
        if not args.renter_id:
            parser.error(f"{args.command} requires --renter-id")
        if not args.hood_ack:
            parser.error(f"{args.command} requires --hood-ack; acknowledgements are never prefilled")
        try:
            hood_entry = assert_and_log_entry(
                renter_id=args.renter_id,
                operation=f"cli:kpgs_{args.command}",
                hood_ack=args.hood_ack,
            )
        except ValueError as exc:
            out = {"schema": "kpgs_cli_admission_v1", "verdict": "BLOCKED", "message": str(exc)}
            print(json.dumps(out, indent=2, ensure_ascii=False) if args.json else f"[kc_kpgs_smoke_poc] {args.command} -> BLOCKED: {exc}")
            return 1

    if args.command == "gate":
        out = load_cached_activation_gate()
    elif args.command == "smoke":
        out = run_kpgs_smoke_poc()
    elif args.command == "behavioral":
        out = run_kpgs_behavioral_poc(write_report=True)
    elif args.command == "tick":
        out = run_sovereign_sim_tick(sample_size=12, write_world=True)
    elif args.command == "status":
        out = sovereign_sim_status()
    elif args.command == "ui":
        out = sovereign_sim_ui_snapshot()
    else:
        out = bootstrap_sovereign_sim()

    if hood_entry is not None:
        out = {**out, "hood_entry": hood_entry}

    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        verdict = out.get("verdict") or out.get("gate_verdict") or ("ALLOW" if out.get("activation_allowed") else "BLOCK")
        print(f"[kc_kpgs_smoke_poc] {args.command} -> {verdict}")
        if out.get("summary"):
            print(out["summary"])
        if out.get("message"):
            print(out["message"])

    blocked = out.get("verdict") == "BLOCKED" or (
        args.command in ("gate", "bootstrap", "smoke") and not out.get("activation_allowed", True)
        and out.get("verdict") not in ("PASS", "BOOTSTRAPPED", "ALLOW", "HOLD")
    )
    if blocked and args.command != "ui":
        return 1
    if out.get("verdict") == "HOLD":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
