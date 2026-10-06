"""Validate current pull-request evidence records with the canonical FourWsValidator."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

from kopano.ikp_engine import FourWsValidator  # noqa: E402


DEFAULT_BASE_BRANCH = "master"
FIELD_LINE = re.compile(
    r"^\s*(?:[-*]\s+|>\s*)?\*{0,2}\s*(WHO|WHAT|WHERE|WHY)\s*\*{0,2}\s*:\s*\*{0,2}\s*(.*?)\s*$",
    re.IGNORECASE,
)


def parse_four_ws(body: str | None) -> tuple[dict[str, str], list[str]]:
    """Read explicit Four Ws lines, allowing markdown emphasis and wrapped values."""
    fields = {field: "" for field in FourWsValidator.REQUIRED}
    errors: list[str] = []
    seen: set[str] = set()
    active: str | None = None

    for line in (body or "").splitlines():
        match = FIELD_LINE.match(line)
        if match:
            field = match.group(1).lower()
            if field in seen:
                errors.append(f"duplicate {field.upper()} field")
                active = None
                continue
            seen.add(field)
            fields[field] = match.group(2).strip()
            active = field
            continue

        if active and line.strip():
            fields[active] = "\n".join(part for part in (fields[active], line.strip()) if part)

    return fields, errors


def _actor(record: dict[str, Any]) -> str:
    user = record.get("user") or {}
    return str(user.get("login") or "unknown-user")


def _is_bot(record: dict[str, Any]) -> bool:
    user = record.get("user") or {}
    login = str(user.get("login") or "")
    return str(user.get("type") or "").lower() == "bot" or login.endswith("[bot]")


def _make_record(kind: str, record_id: str | int, actor: str, body: str | None) -> dict[str, Any]:
    signal, parse_errors = parse_four_ws(body)
    _, validation = FourWsValidator().validate(signal)
    return {
        "kind": kind,
        "id": str(record_id),
        "actor": actor,
        "validation": validation,
        "parse_errors": parse_errors,
    }


def collect_records(
    pull_request: dict[str, Any],
    reviews: list[dict[str, Any]],
    review_comments: list[dict[str, Any]],
    issue_comments: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Validate the PR description and all current human-authored review/comment records."""
    number = pull_request.get("number", "unknown")
    author = _actor(pull_request)
    records = [
        _make_record(
            "PR description",
            f"#{number}",
            author,
            pull_request.get("body"),
        )
    ]

    inactive_review_ids = {
        review.get("id")
        for review in reviews
        if str(review.get("state") or "").upper() in {"DISMISSED", "PENDING"}
    }
    for review in reviews:
        if str(review.get("state") or "").upper() in {"DISMISSED", "PENDING"} or _is_bot(review):
            continue
        records.append(
            _make_record(
                "review",
                review.get("id", "unknown"),
                _actor(review),
                review.get("body"),
            )
        )

    for comment in review_comments:
        if _is_bot(comment) or comment.get("pull_request_review_id") in inactive_review_ids:
            continue
        records.append(
            _make_record(
                "inline review comment",
                comment.get("id", "unknown"),
                _actor(comment),
                comment.get("body"),
            )
        )

    for comment in issue_comments:
        if _is_bot(comment):
            continue
        records.append(
            _make_record(
                "PR conversation comment",
                comment.get("id", "unknown"),
                _actor(comment),
                comment.get("body"),
            )
        )

    return records


def record_failures(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failures = []
    for item in records:
        validation = item["validation"]
        if not validation["valid"] or item["parse_errors"]:
            failures.append(item)
    return failures


def _gh_api(endpoint: str, *, paginate: bool = False) -> Any:
    command = ["gh", "api"]
    if paginate:
        command.extend(["--paginate", "--slurp"])
    command.append(endpoint)
    result = subprocess.run(command, check=True, capture_output=True, text=True, env=os.environ.copy())
    return json.loads(result.stdout)


def _gh_list(endpoint: str) -> list[dict[str, Any]]:
    pages = _gh_api(endpoint, paginate=True)
    if not isinstance(pages, list):
        raise ValueError(f"GitHub API did not return paginated records for {endpoint}")
    flattened: list[dict[str, Any]] = []
    for page in pages:
        if not isinstance(page, list):
            raise ValueError(f"GitHub API returned a non-list page for {endpoint}")
        flattened.extend(page)
    return flattened


def pull_request_number(event: dict[str, Any]) -> int | None:
    pull_request = event.get("pull_request")
    if isinstance(pull_request, dict):
        number = pull_request.get("number") or event.get("number")
        return int(number) if number is not None else None

    issue = event.get("issue")
    if isinstance(issue, dict) and issue.get("pull_request"):
        number = issue.get("number")
        return int(number) if number is not None else None
    return None


def evaluate_pull_request(
    repository: str,
    number: int,
    *,
    api_object: Callable[[str], dict[str, Any]] = _gh_api,
    api_list: Callable[[str], list[dict[str, Any]]] = _gh_list,
) -> tuple[str, str]:
    """Return a skip/pass/fail state and a human-readable receipt from live GitHub records."""
    prefix = f"repos/{repository}/pulls/{number}"
    pull_request = api_object(prefix)
    base_branch = str((pull_request.get("base") or {}).get("ref") or "")
    if base_branch != DEFAULT_BASE_BRANCH:
        return "skip", f"Four Ws gate skipped: PR #{number} targets `{base_branch or 'unknown'}`, not `{DEFAULT_BASE_BRANCH}`."

    reviews = api_list(f"{prefix}/reviews?per_page=100")
    review_comments = api_list(f"{prefix}/comments?per_page=100")
    issue_comments = api_list(f"repos/{repository}/issues/{number}/comments?per_page=100")
    records = collect_records(pull_request, reviews, review_comments, issue_comments)
    failures = record_failures(records)

    lines = [
        "## Four Ws evidence gate receipt",
        "",
        f"- Pull request: #{number}",
        f"- Base branch: `{base_branch}`",
        f"- Validator: `{FourWsValidator().validate({'who': 'gate', 'what': 'gate', 'where': 'CI', 'why': 'canonical contract'})[1]['schema']}`",
        f"- Current records inspected: {len(records)}",
        f"- Passing records: {len(records) - len(failures)}",
        f"- Failed records: {len(failures)}",
    ]
    if failures:
        lines.extend(["", "### Records needing correction", ""])
        for item in failures:
            validation = item["validation"]
            record_name = f"{item['kind']} `{item['id']}` by `{item['actor']}`"
            if validation["missing"]:
                lines.append(f"- {record_name}: missing or empty `{', '.join(validation['missing'])}`.")
            for error in item["parse_errors"]:
                lines.append(f"- {record_name}: {error}.")
            lines.append(f"  Validator result: `{validation['cbp_verdict']}`.")
        lines.extend(
            [
                "",
                "Use one explicit line for each field: `WHO: ...`, `WHAT: ...`, `WHERE: ...`, and `WHY: ...`.",
                "The gate reads the current GitHub records again after edits, deletions, and review dismissals.",
            ]
        )
        return "fail", "\n".join(lines)

    lines.extend(["", "Every current human-authored record has non-empty WHO, WHAT, WHERE, and WHY fields."])
    return "pass", "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", required=True, help="Path to the GitHub webhook event JSON")
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"), help="owner/repository")
    args = parser.parse_args()

    with Path(args.event).open(encoding="utf-8") as event_file:
        event = json.load(event_file)
    number = pull_request_number(event)
    if number is None:
        print("Four Ws gate skipped: event is not associated with a pull request.")
        return 0
    if number < 1:
        print("Four Ws gate failed: invalid pull request number.")
        return 1
    if not args.repository:
        print("Four Ws gate failed: repository identity is unavailable.")
        return 1

    try:
        state, receipt = evaluate_pull_request(args.repository, number)
    except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError) as error:
        print(f"Four Ws gate could not read current GitHub records: {type(error).__name__}.")
        return 1

    print(receipt)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with Path(summary_path).open("a", encoding="utf-8") as summary_file:
            summary_file.write(receipt + "\n")
    return 1 if state == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
