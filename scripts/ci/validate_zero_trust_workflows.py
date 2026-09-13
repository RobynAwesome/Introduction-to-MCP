#!/usr/bin/env python3
"""Validate the KPGS zero-trust policy and selected GitHub workflows.

The validator is deliberately standard-library only. It checks the high-risk
properties that can be proven from repository text without pretending that a
workflow file establishes branch protection, cloud credentials, DNS, or a
provider deployment. Existing workflows may retain migration debt; callers
choose which workflows are in the immutable-action enforcement set.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


class ZeroTrustValidationError(ValueError):
    """Raised when a policy or workflow violates an explicit control."""


REMOTE_ACTION_RE = re.compile(r"^([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@([^\s#]+)$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
USES_RE = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)", re.MULTILINE)


def _without_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        quote = None
        cut = None
        for index, character in enumerate(line):
            if character in {"'", '"'}:
                quote = None if quote == character else character if quote is None else quote
            elif character == "#" and quote is None:
                cut = index
                break
        lines.append(line if cut is None else line[:cut])
    return "\n".join(lines)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ZeroTrustValidationError(message)


def validate_policy(policy_path: Path) -> dict[str, Any]:
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ZeroTrustValidationError(f"missing policy: {policy_path}") from exc
    except json.JSONDecodeError as exc:
        raise ZeroTrustValidationError(f"invalid policy JSON: {exc}") from exc

    _require(isinstance(policy, dict), "policy must be an object")
    _require(policy.get("schema") == "kpgs.zero-trust-policy.v1", "unsupported policy schema")
    _require(policy.get("authority") == "governance/kpgs-vnext/security", "policy authority drift")

    source = policy.get("source_of_truth")
    _require(isinstance(source, dict), "source_of_truth must be an object")
    _require(source.get("repository") == "RobynAwesome/Introduction-to-MCP", "source repository drift")
    _require(source.get("default_branch") == "master", "source default branch drift")
    canonical_files = source.get("canonical_files")
    _require(isinstance(canonical_files, list) and canonical_files, "canonical_files must be non-empty")
    _require(all(isinstance(item, str) and item for item in canonical_files), "canonical file paths must be strings")

    controls = policy.get("controls")
    _require(isinstance(controls, list) and controls, "controls must be non-empty")
    control_ids: set[str] = set()
    for control in controls:
        _require(isinstance(control, dict), "each control must be an object")
        control_id = control.get("id")
        _require(isinstance(control_id, str) and control_id, "each control needs an id")
        _require(control_id not in control_ids, f"duplicate control id: {control_id}")
        control_ids.add(control_id)
        _require(control.get("enforcement") in {"enforced", "staged"}, f"invalid enforcement for {control_id}")
        requirements = control.get("requirements")
        _require(isinstance(requirements, list) and requirements, f"empty requirements for {control_id}")

    admission = policy.get("production_admission")
    _require(isinstance(admission, dict), "production_admission must be an object")
    _require(set(admission.get("required_manifest_states", [])) == {"validated", "approved"}, "production states drift")
    for key in (
        "require_capability_lease",
        "require_provenance",
        "require_exact_head_ci",
        "require_preview_or_production_evidence",
        "require_human_review",
    ):
        _require(admission.get(key) is True, f"production admission must require {key}")
    _require(admission.get("required_license_status") == "verified-compatible", "license admission drift")

    for collection_name in ("known_holds", "unknowns"):
        _require(isinstance(policy.get(collection_name), list), f"{collection_name} must be a list")

    serialized = json.dumps(policy, sort_keys=True)
    _require("sk-" not in serialized and "BEGIN PRIVATE KEY" not in serialized, "policy contains credential material")
    return policy


def _workflow_has_event(text: str, event: str) -> bool:
    return re.search(rf"(?m)^\s{{0,2}}{re.escape(event)}\s*:", text) is not None


def _has_top_level_permissions(text: str) -> bool:
    return re.search(r"(?m)^permissions:\s*$", text) is not None


def _has_contents_read_permission(text: str) -> bool:
    match = re.search(r"(?ms)^permissions:\s*\n(?P<body>(?:^[ \t]+[^\n]*\n?)*)", text)
    if not match:
        return False
    return re.search(r"(?m)^\s+contents:\s*read\s*$", match.group("body")) is not None


def validate_workflow(workflow_path: Path, *, require_pinned_actions: bool = False) -> list[str]:
    try:
        original = workflow_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ZeroTrustValidationError(f"missing workflow: {workflow_path}") from exc
    text = _without_comments(original)
    findings: list[str] = []

    if _workflow_has_event(text, "pull_request_target"):
        findings.append("forbidden privileged trigger pull_request_target")
    if _workflow_has_event(text, "workflow_run"):
        findings.append("forbidden privileged trigger workflow_run")

    has_pull_request = _workflow_has_event(text, "pull_request")
    if has_pull_request and "secrets." in text:
        findings.append("pull_request workflow references repository secrets")
    if has_pull_request and re.search(r"(?m)^\s+id-token:\s*write\s*$", text):
        findings.append("pull_request workflow requests an OIDC token")
    if "permissions:" not in text:
        findings.append("workflow has no explicit permissions block")
    if re.search(r"(?m)^\s*permissions:\s*write-all\s*$", text) or "write-all" in text:
        findings.append("workflow grants write-all permissions")

    if require_pinned_actions:
        for reference in USES_RE.findall(text):
            if reference.startswith("./"):
                continue
            match = REMOTE_ACTION_RE.match(reference)
            if not match:
                findings.append(f"invalid action reference: {reference}")
            elif not SHA_RE.fullmatch(match.group(2)):
                findings.append(f"action is not pinned to an immutable SHA: {reference}")

    if findings:
        joined = "; ".join(findings)
        raise ZeroTrustValidationError(f"{workflow_path}: {joined}")
    return findings


def validate(
    *,
    root: Path,
    policy: Path,
    workflows: Iterable[str],
    pinned_workflows: Iterable[str],
) -> None:
    validate_policy(policy)
    pinned = set(pinned_workflows)
    selected = list(workflows)
    _require(selected, "at least one workflow must be selected")
    for relative in selected:
        validate_workflow(root / relative, require_pinned_actions=relative in pinned)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--workflow", action="append", required=True)
    parser.add_argument("--pinned-workflow", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        validate(
            root=args.root,
            policy=args.root / args.policy if not args.policy.is_absolute() else args.policy,
            workflows=args.workflow,
            pinned_workflows=args.pinned_workflow,
        )
    except ZeroTrustValidationError as exc:
        print(f"ZERO_TRUST_FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"ZERO_TRUST_PASS: policy and {len(args.workflow)} workflow(s) satisfy selected controls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

