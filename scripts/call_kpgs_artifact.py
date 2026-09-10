#!/usr/bin/env python3
"""Resolve and inspect a KPGS callable artifact by ID or alias.

Examples:
  python scripts/call_kpgs_artifact.py --list
  python scripts/call_kpgs_artifact.py "depict nature and society"
  KPGS_INTERFACE_SELECTED_MODEL=<resolved-model> \
    python scripts/call_kpgs_artifact.py "depict nature and society" --runtime
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
KOPANO_CORE = REPO_ROOT / "kopano-core"
sys.path.insert(0, str(KOPANO_CORE))

from kopano.callable_artifact_registry import (  # noqa: E402
    ArtifactContractError,
    discover_artifacts,
    resolve_artifact,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve a KPGS callable artifact")
    parser.add_argument("query", nargs="?", help="Artifact ID or invocation alias")
    parser.add_argument("--list", action="store_true", help="List implemented callable artifacts")
    parser.add_argument("--runtime", action="store_true", help="Resolve and print runtime identity/model envelope")
    args = parser.parse_args()

    artifacts = discover_artifacts(REPO_ROOT)

    if args.list:
        for artifact in artifacts:
            print(f"{artifact.artifact_id}\t{artifact.document['metadata']['status']}\t{artifact.path}")
        return 0

    if not args.query:
        parser.error("query is required unless --list is used")

    try:
        artifact = resolve_artifact(artifacts, args.query)
    except (KeyError, ArtifactContractError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    result = {
        "artifact_id": artifact.artifact_id,
        "name": artifact.document["metadata"]["name"],
        "group": artifact.document["metadata"]["group"],
        "version": artifact.document["metadata"]["version"],
        "status": artifact.document["metadata"]["status"],
        "path": str(artifact.path.relative_to(REPO_ROOT)),
        "adk_adapter": artifact.document["spec"].get("adk", {}).get("adapter"),
        "aliases": list(artifact.aliases),
    }

    if args.runtime:
        try:
            result["runtime"] = artifact.resolve_runtime().to_dict()
        except ArtifactContractError as exc:
            result["runtime_error"] = str(exc)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 3

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
