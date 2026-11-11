#!/usr/bin/env python3
"""Offline, research-only ingestion of non-Oya discoveries into the EXISTING AI Frontier Map.

Does not fetch, execute, score, install, approve or infer upstream authorship.
The existing Oya collector, schema, validator and downstream membrane remain authoritative.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from collect_oya_corpus import blank_score
from validate_corpus import validate

REPO_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*$")
ORIGINS = {"founder_fork", "external_discovery"}


def checked_repo(value: object) -> str:
    if not isinstance(value, str) or not REPO_RE.fullmatch(value):
        raise ValueError("repository must be GitHub owner/name (no URL or shell syntax)")
    if any(piece in {".", ".."} for piece in value.split("/")):
        raise ValueError("dot-only repository path segments are forbidden")
    return value


def make_record(row: dict) -> dict:
    if not isinstance(row, dict):
        raise ValueError("discovery row must be an object")
    repo = checked_repo(row.get("repo"))
    origin = row.get("origin_kind")
    if origin not in ORIGINS:
        raise ValueError("origin_kind must be founder_fork or external_discovery")
    observed_at = row.get("observed_at")
    if not isinstance(observed_at, str) or not observed_at.strip():
        raise ValueError("observed_at must be an explicit nonempty source observation date")
    upstream = row.get("upstream_repo")
    if origin == "founder_fork":
        upstream = checked_repo(upstream)
        if upstream == repo:
            raise ValueError("founder fork cannot be its own upstream")
    elif upstream is not None:
        raise ValueError("independent upstream cannot claim a fork parent")
    issue = row.get("intake_issue")
    if issue is not None and (
        not isinstance(issue, str)
        or not issue.startswith("https://github.com/")
        or not re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/issues/[0-9]+", issue)
    ):
        raise ValueError("intake_issue must be a canonical GitHub issue URL")
    observed_url = "https://github.com/" + repo
    evidence = [{
        "kind": "observed_repository",
        "url": observed_url,
        "note": "Repository URL supplied for research. Authorship, licence, commit and suitability not yet attested.",
    }]
    if issue:
        evidence.append({"kind": "governed_intake", "url": issue, "note": "Research intake; no implementation authority."})
    return {
        "provenance": {
            "origin_kind": origin, "observed_repo": repo, "observed_repo_id": None,
            "observed_at": observed_at, "classification": "unresolved" if origin == "external_discovery" else origin,
            "upstream_repo": upstream, "upstream_owner": None,
            "upstream_owner_type": None, "upstream_repo_id": None,
            "original_repo_created_at": None, "upstream_commit_sha": None,
        },
        "discovery": {
            "signal": "agent-skills" if row.get("signal") == "agent-skills" else "unknown",
            "candidate_signals": ["agent-skills"] if row.get("signal") == "agent-skills" else [],
            "evidence": "Owner-directed/manual discovery; not a GitHub metadata or licence attestation.",
            "discovered_at": observed_at,
        },
        "safeskill": {
            "scan_branch": None, "scan_score": None, "scan_grade": None, "findings": {},
            "pr_url": None, "pr_number": None, "pr_created_at": None,
            "maintainer_response": "unknown",
        },
        "technical_intelligence": {
            "problem": None, "architecture": None, "protocols": [],
            "dependencies": [], "integrations": [], "agent_pattern": None,
            "security_pattern": None, "novel_mechanism": None,
        },
        "capability_surface": {
            "filesystem": None, "network": None, "secrets": None,
            "database": None, "browser": None, "process_execution": None,
            "repository_mutation": None, "cloud_access": None, "authentication": None,
            "external_apis": [], "prompt_injection": None, "taint_flow": None,
        },
        "reuse_governance": {
            "mode": "research_only", "license": None, "spdx": None,
            "reusable_code": None, "attribution_required": None, "architecture_only": None,
            "restrictions": "HOLD on import, execution or ADOPT pending source SHA, licence, independent risk review and owner's scoped approval.",
            "provenance_url": observed_url, "source_commit": None,
        },
        "frontier_score": blank_score(),
        "convergence": {
            "target_systems": ["GSMB"], "reusable_primitive": None,
            "integration_pattern": None,
            "gaps": "Source/license/authorship, internal overlap and bounded falsifying experiment required.",
            "decision": "STUDY",
        },
        "evidence": evidence,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="UTF-8 JSONL discovery manifest")
    parser.add_argument("--output", required=True, help="UTF-8 JSONL Frontier Map records")
    args = parser.parse_args()
    records = []
    seen = set()
    try:
        for lineno, raw in enumerate(Path(args.input).read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip():
                continue
            record = make_record(json.loads(raw))
            repo = record["provenance"]["observed_repo"].lower()
            if repo in seen:
                raise ValueError(f"duplicate repository on line {lineno}: {repo}")
            seen.add(repo)
            problems = validate(record, lineno)
            if problems:
                raise ValueError("; ".join(problems))
            records.append(record)
        if not records:
            raise ValueError("empty input is not a valid intake")
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print("HOLD: no output written; " + str(exc), file=sys.stderr)
        return 2
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records), encoding="utf-8")
    print(f"STUDY_ONLY: {len(records)} validated discovery records -> {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
