#!/usr/bin/env python3
"""Phase 3 operating mesh — promote flagship sub-brains with PROOF-01..03."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.operating_mesh import (  # noqa: E402
    promote_all_flagships,
    promote_flagship,
    operating_mesh_status,
)
from kopano.kpgs_cli_admission import admit_cli_renter  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="KPEFS operating mesh (Phase 3)")
    p.add_argument(
        "command",
        choices=["status", "promote-all", "promote-one"],
        nargs="?",
        default="status",
    )
    p.add_argument("--agent-id", help="Sub-brain id for promote-one")
    p.add_argument("--force", action="store_true", help="Re-run promotion even if operating")
    p.add_argument("--json", action="store_true")
    p.add_argument("--renter-id", default="", help="Stateless renter identity for promotion")
    p.add_argument("--renter-class", default="stateless_renter")
    p.add_argument("--hood-ack", default="", help="Exact canonical renter acknowledgement")
    args = p.parse_args()

    skip = not args.force
    admission: dict | None = None
    if args.command == "status":
        out = operating_mesh_status()
    else:
        if args.command == "promote-one" and not args.agent_id:
            p.error("promote-one requires --agent-id")
        if not args.renter_id:
            p.error(f"{args.command} requires --renter-id")
        if not args.hood_ack:
            p.error(f"{args.command} requires --hood-ack")
        try:
            admission = admit_cli_renter(
                renter_id=args.renter_id,
                renter_class=args.renter_class,
                hood_ack=args.hood_ack,
                operation=f"cli:phu_operating_mesh_{args.command.replace('-', '_')}",
            )
        except ValueError as exc:
            p.error(str(exc))

        if args.command == "promote-all":
            out = promote_all_flagships(skip_if_operating=skip)
        else:
            out = promote_flagship(args.agent_id, skip_if_operating=skip)

        out.update(admission)

    if args.json:
        print(json.dumps(out, indent=2))
    elif args.command == "status":
        print(
            f"Operating mesh: {out['operating_count']}/{out['flagships_total']} | "
            f"phase3_exit: {out['phase3_exit_met']}"
        )
        for row in out.get("flagships", []):
            print(f"  {row['sub_brain_id']}: {row.get('status')} | PoC {row.get('poc_verdict') or '—'}")
    elif args.command == "promote-all":
        print(
            f"Promote all — operating: {out['operating']}/{out['flagships_total']} | "
            f"exit: {out['phase3_exit_met']}"
        )
    else:
        print(f"{out.get('sub_brain_id')}: {out.get('status', out.get('error', '—'))}")

    if args.command == "promote-all":
        return 0 if out.get("phase3_exit_met") else 1
    if args.command == "promote-one" and out.get("status") != "operating" and not out.get("skipped"):
        return 1 if out.get("error") or out.get("status") == "incomplete" else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
