#!/usr/bin/env python3
"""Phase 5 graduation bar — verified production separate from operating mesh."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.graduation_bar import (  # noqa: E402
    graduation_bar_status,
    graduation_claim_allowed,
    record_steward_trust,
    run_guard_verified_production,
)
from kopano.kpgs_cli_admission import admit_cli_renter  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="KPEFS Phase 5 graduation bar")
    p.add_argument(
        "command",
        choices=["status", "guard", "check-claim", "steward-trust"],
        nargs="?",
        default="status",
    )
    p.add_argument("--claim", default="", help="Claim text for check-claim")
    p.add_argument("--note", default="", help="Optional note for steward-trust")
    p.add_argument("--json", action="store_true")
    p.add_argument("--renter-id", default="", help="Stateless renter identity for steward-trust")
    p.add_argument("--renter-class", default="stateless_renter")
    p.add_argument("--hood-ack", default="", help="Exact canonical renter acknowledgement")
    args = p.parse_args()

    admission: dict | None = None
    if args.command == "steward-trust":
        if not args.renter_id:
            p.error("steward-trust requires --renter-id")
        if not args.hood_ack:
            p.error("steward-trust requires --hood-ack")
        try:
            admission = admit_cli_renter(
                renter_id=args.renter_id,
                renter_class=args.renter_class,
                hood_ack=args.hood_ack,
                operation="cli:graduation_steward_trust",
            )
        except ValueError as exc:
            p.error(str(exc))

    if args.command == "status":
        out = graduation_bar_status()
    elif args.command == "guard":
        out = run_guard_verified_production()
    elif args.command == "check-claim":
        out = graduation_claim_allowed(claim=args.claim)
    else:
        out = record_steward_trust(note=args.note)
        out.update(admission or {})

    if args.json:
        print(json.dumps(out, indent=2))
    elif args.command == "status":
        print(
            f"Verified production: {out['verified_production']}/{out['public_graduation_bar']} | "
            f"bar_met: {out['production_bar_met']} | "
            f"operating_mesh_phase3: {out['operating_mesh_phase3_met']} | "
            f"public_graduated: {out['public_graduated']}"
        )
        print(f"External swarm receipt: {out['external_swarm']['receipt_present']}")
        print(out["guard_command"])
    elif args.command == "guard":
        print(out.get("stdout") or out.get("stderr"))
    elif args.command == "check-claim":
        print(f"allowed: {out['allowed']}")
        for r in out.get("reasons", []):
            print(f"  - {r}")
    else:
        print(out.get("summary", "steward trust recorded"))

    if args.command == "guard":
        return 0 if out.get("passed") else 1
    if args.command == "check-claim":
        return 0 if out.get("allowed") else 1
    if args.command == "status":
        return 0 if out.get("phase5_exit_met") else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
