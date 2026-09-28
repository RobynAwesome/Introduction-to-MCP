#!/usr/bin/env python3
"""Reattach detached Kopano-Phu sub-brains to Cassy legacy lane."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

from kopano.phu_ecosystem import reattach_detached_subbrains  # noqa: E402
from kopano.kpgs_cli_admission import admit_cli_renter  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--renter-id", default="")
    parser.add_argument("--renter-class", default="stateless_renter")
    parser.add_argument("--hood-ack", default="", help="Exact canonical renter acknowledgement")
    args = parser.parse_args()
    if not args.renter_id:
        parser.error("Sub-brain reattachment requires --renter-id")
    if not args.hood_ack:
        parser.error("Sub-brain reattachment requires --hood-ack")
    try:
        admission = admit_cli_renter(
            renter_id=args.renter_id,
            renter_class=args.renter_class,
            hood_ack=args.hood_ack,
            operation="cli:phu_reattach_subbrains",
        )
    except ValueError as exc:
        parser.error(str(exc))
    result = reattach_detached_subbrains(dry_run=args.dry_run)
    result.update(admission)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Reattached: {', '.join(result['reattached']) or '(none)'}")
        print(f"Skipped: {', '.join(result['skipped']) or '(none)'}")
        print(f"Total attached: {result['total_attached']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
