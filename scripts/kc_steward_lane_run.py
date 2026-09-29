#!/usr/bin/env python3
"""Activate KC + Cassy steward lane — profile, trust, Identi, Guardian."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.steward_lane import (  # noqa: E402
    run_steward_lane_activate,
    steward_lane_status,
)
from kopano.kpgs_cli_admission import admit_cli_renter  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="KC+Cassy steward lane status")

    act = sub.add_parser("activate", help="Activate profile + flows + trust receipt")
    act.add_argument("--note", default="", help="Optional note on steward trust")
    act.add_argument(
        "--department",
        default="kopano_labs_experimentation",
        help="Department for Identi/Guardian",
    )
    act.add_argument("--action", default="", help="Override default steward action")
    act.add_argument("--evidence", default="", help="Override default evidence path")
    act.add_argument("--no-identi", action="store_true")
    act.add_argument("--no-guardian", action="store_true")
    act.add_argument("--no-teacher-approve", action="store_true")
    act.add_argument("--renter-id", default="", help="Stateless renter identity")
    act.add_argument("--renter-class", default="stateless_renter")
    act.add_argument("--hood-ack", default="", help="Exact canonical renter acknowledgement")

    args = p.parse_args()

    if args.cmd == "status":
        print(json.dumps(steward_lane_status(), indent=2))
        return 0

    if not args.renter_id:
        act.error("activate requires --renter-id")
    if not args.hood_ack:
        act.error("activate requires --hood-ack")
    try:
        admission = admit_cli_renter(
            renter_id=args.renter_id,
            renter_class=args.renter_class,
            hood_ack=args.hood_ack,
            operation="cli:steward_lane_activate",
        )
    except ValueError as exc:
        act.error(str(exc))

    out = run_steward_lane_activate(
        note=args.note,
        department_id=args.department,
        run_identi=not args.no_identi,
        run_guardian=not args.no_guardian,
        teacher_approve=not args.no_teacher_approve,
        action=args.action or None,
        evidence=args.evidence or None,
    )
    out.update(admission)
    print(json.dumps(out, indent=2))
    return 0 if out.get("verdict") == "ACTIVE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
