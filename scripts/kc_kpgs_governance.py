#!/usr/bin/env python3
"""KPGS governance — Schematics MAIN BRAIN compile, status, propagate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.kpgs_governance import (  # noqa: E402
    compile_kpgs_governance,
    governance_status_snapshot,
    propagate_governance_marker,
)
from kopano.kpgs_activation_gate import require_alp_receipt  # noqa: E402
from kopano.kpgs_renter_entry import (  # noqa: E402
    assert_and_log_entry,
    block_holder_brief,
    hood_entry_assertion,
    load_altar_block_holders,
    load_renter_entryway,
)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    compile_parser = sub.add_parser("compile", help="Compile full KPGS governance stack")
    compile_parser.add_argument("--renter-id", required=True)
    compile_parser.add_argument("--hood-ack", required=True)
    sub.add_parser("status", help="Governance status (boot API shape)")
    propagate_parser = sub.add_parser("propagate", help="Compile + log + Schematics comms marker")
    propagate_parser.add_argument("--renter-id", required=True)
    propagate_parser.add_argument("--hood-ack", required=True)

    e = sub.add_parser("entry", help="Stateless renter hood entry — who you are fucking with")
    e.add_argument("--renter-id", default="anonymous_stateless_renter")
    e.add_argument("--renter-class", default="linguistic_actor")
    e.add_argument("--hood-ack", default="", help="Exact canonical renter acknowledgement")
    e.add_argument("--assert", dest="hood_assert", action="store_true", help="Require hood_ack and log entry")

    bh = sub.add_parser("block-holders", help="List KPGS altar block holders and mesh brief duty")
    bh.add_argument("--agent-id", default="", help="Single agent brief (default: all mesh + altar proxies)")

    args = p.parse_args()
    try:
        if args.cmd in ("compile", "propagate"):
            entry = assert_and_log_entry(
                renter_id=args.renter_id,
                operation=f"cli:kpgs_governance_{args.cmd}",
                hood_ack=args.hood_ack,
            )
            alp_receipt = require_alp_receipt()
            out = compile_kpgs_governance() if args.cmd == "compile" else propagate_governance_marker()
            out["hood_entry"] = entry
            out["alp_receipt"] = alp_receipt
        elif args.cmd == "status":
            out = governance_status_snapshot()
        elif args.cmd == "entry":
            if args.hood_assert:
                if not args.hood_ack:
                    p.error("entry --assert requires --hood-ack; acknowledgements are never prefilled")
                out = assert_and_log_entry(
                    renter_id=args.renter_id,
                    renter_class=args.renter_class,
                    operation="cli:kpgs_governance_entry_assert",
                    hood_ack=args.hood_ack,
                )
            else:
                out = hood_entry_assertion(renter_id=args.renter_id, renter_class=args.renter_class)
            print(json.dumps(out, indent=2))
            return 0
        elif args.cmd == "block-holders":
            from kopano.phu_boot_governance import mesh_agent_ids  # noqa: E402

            registry = load_altar_block_holders()
            if args.agent_id:
                aids = [args.agent_id]
            else:
                aids = sorted(set(mesh_agent_ids()) | {"mirror_warden", "operational_general"})
            briefs = [block_holder_brief(agent_id=aid) for aid in aids]
            out = {
                "schema": "kpgs_block_holders_report_v1",
                "registry": registry.get("_source"),
                "altar_layers": registry.get("altar_layers", []),
                "agents": briefs,
            }
            print(json.dumps(out, indent=2))
            return 0
    except ValueError as exc:
        print(json.dumps({"schema": "kpgs_cli_admission_v1", "verdict": "BLOCK", "message": str(exc)}, indent=2))
        return 1

    print(json.dumps(out, indent=2))
    verdict = out.get("verdict") or out.get("compile_verdict")
    if verdict == "INCOMPLETE":
        return 1
    if args.cmd == "compile" and out.get("verdict") != "COMPILED":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
