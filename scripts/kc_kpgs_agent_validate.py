#!/usr/bin/env python3
"""KPGS Agent Initialization — Altar Integration validator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.kpgs_agent_validate import (  # noqa: E402
    compile_kpgs_thesis,
    synthesize_agent_manifest,
    validate_kpgs_agent,
    validate_kpgs_mesh,
)
from kopano.kpgs_telemetry_route import (  # noqa: E402
    classify_telemetry_signal,
    compile_black_beast_thesis,
)
from kopano.kpgs_cli_admission import admit_cli_renter  # noqa: E402


def _add_renter_admission_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--renter-id", required=True, help="Stateless renter identity")
    parser.add_argument("--renter-class", default="stateless_renter")
    parser.add_argument(
        "--hood-ack", required=True, help="Exact canonical renter acknowledgement"
    )


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("mesh", help="PoC — validate full boot mesh against KPGS core")
    m.add_argument("--json", action="store_true")
    _add_renter_admission_arguments(m)

    t = sub.add_parser("thesis", help="Compile-check KPGS thesis payload X8020")
    t.add_argument("--json", action="store_true")
    _add_renter_admission_arguments(t)

    b = sub.add_parser("black-beast", help="Compile-check Black Beast thesis payload V1")
    b.add_argument("--json", action="store_true")
    _add_renter_admission_arguments(b)

    c = sub.add_parser("classify", help="Classify raw signal before interpretation")
    c.add_argument("signal", help="Raw telemetry text to route")
    c.add_argument("--json", action="store_true")

    v = sub.add_parser("validate", help="Validate one agent manifest")
    v.add_argument("agent_id")
    v.add_argument("payload_path", nargs="?", help="Optional kpgs manifest JSON path")
    v.add_argument("--synthetic", action="store_true", help="Use synthesized mesh manifest")
    _add_renter_admission_arguments(v)

    s = sub.add_parser("synthesize", help="Print default manifest for agent_id")
    s.add_argument("agent_id")

    args = p.parse_args()

    admission = None
    if args.cmd in {"mesh", "thesis", "black-beast", "validate"}:
        try:
            admission = admit_cli_renter(
                renter_id=args.renter_id,
                renter_class=args.renter_class,
                hood_ack=args.hood_ack,
                operation=f"cli:kc_kpgs_agent_validate:{args.cmd}",
            )
        except ValueError as exc:
            p.error(str(exc))

    if args.cmd == "black-beast":
        out = compile_black_beast_thesis()
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print(out["summary"])
            if out.get("errors"):
                for e in out["errors"]:
                    print(f"  ERROR: {e}")
        return 0 if out["verdict"] == "COMPILED" else 1

    if args.cmd == "classify":
        out = classify_telemetry_signal(args.signal)
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print(out["summary"])
            print(f"  note: {out['note']}")
        return 0 if out["verdict"] != "RECLASSIFY" else 1

    if args.cmd == "thesis":
        out = compile_kpgs_thesis()
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print(out["summary"])
            if out.get("errors"):
                for e in out["errors"]:
                    print(f"  ERROR: {e}")
        return 0 if out["verdict"] == "COMPILED" else 1

    if args.cmd == "mesh":
        report = validate_kpgs_mesh()
        report["renter_admission"] = admission
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"KPGS mesh PoC: {report['verdict']}")
            print(f"  agents: {report['agents_total']} SHIP={report['ship']} HOLD={report['hold']} REJECT={report['reject']}")
            print(f"  report: {report['report_path']}")
        return 0 if report["verdict"] == "PASS" else 1

    if args.cmd == "synthesize":
        print(json.dumps(synthesize_agent_manifest(args.agent_id), indent=2))
        return 0

    if args.synthetic or not args.payload_path:
        out = validate_kpgs_agent(args.agent_id)
    else:
        out = validate_kpgs_agent(args.agent_id, manifest_path=args.payload_path)
    out["renter_admission"] = admission
    print(f"STATUS: {out.get('verdict', 'HOLD')}")

    print(json.dumps(out, indent=2))
    return 0 if out.get("verdict") == "SHIP" else 1


if __name__ == "__main__":
    raise SystemExit(main())
