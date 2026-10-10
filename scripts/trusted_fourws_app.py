"""Trusted GitHub App worker for the current Four Ws structural check.

This module is intended to run only in an owner-controlled webhook service. It
never checks out or executes pull-request content. The caller must supply a
short-lived GitHub App installation token with pull-requests:read,
issues:read, and checks:write permissions.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Protocol


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from kopano.ikp_engine import FourWsValidator  # noqa: E402
from pr_fourws_gate import collect_records, record_failures  # noqa: E402


API_ROOT = "https://api.github.com"
API_VERSION = "2026-03-10"
CHECK_NAME = "KPGS Four Ws Receipts (Trusted)"
WEBHOOK_EVENTS: dict[str, frozenset[str]] = {
    "pull_request": frozenset({"opened", "edited", "reopened", "synchronize", "ready_for_review"}),
    "pull_request_review": frozenset({"submitted", "edited", "dismissed"}),
    "pull_request_review_comment": frozenset({"created", "edited", "deleted"}),
    "issue_comment": frozenset({"created", "edited", "deleted"}),
}
_LINK_NEXT = re.compile(r'<([^>]+)>\s*;\s*rel="next"')
_REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class FourWsWorkerError(RuntimeError):
    """A fail-closed worker or provider error with no credential material."""


class GitHubApi(Protocol):
    def get_json(self, endpoint: str) -> Any: ...

    def get_all(self, endpoint: str, *, collection_key: str | None = None) -> list[dict[str, Any]]: ...

    def create_check(self, repository: str, payload: dict[str, Any]) -> dict[str, Any]: ...

    def update_check(self, repository: str, check_run_id: int, payload: dict[str, Any]) -> dict[str, Any]: ...


@dataclass(frozen=True)
class WebhookDelivery:
    event_name: str
    action: str
    payload: dict[str, Any]
    repository: str
    pull_request_number: int


@dataclass(frozen=True)
class GateOutcome:
    state: str
    head_sha: str
    receipt: str
    record_count: int
    failed_count: int


class GitHubAppApi:
    """Small standard-library REST client using an injected installation token."""

    def __init__(self, installation_token: str, *, api_root: str = API_ROOT) -> None:
        if not installation_token or "\n" in installation_token:
            raise FourWsWorkerError("A GitHub App installation token is required.")
        self._token = installation_token
        self._api_root = api_root.rstrip("/")

    def _request(self, method: str, endpoint: str, payload: dict[str, Any] | None = None) -> tuple[Any, str | None]:
        if endpoint.startswith("https://"):
            url = endpoint
        else:
            url = urllib.parse.urljoin(self._api_root + "/", endpoint.lstrip("/"))
        parsed = urllib.parse.urlsplit(url)
        api_host = urllib.parse.urlsplit(self._api_root).netloc
        if parsed.scheme != "https" or parsed.netloc != api_host or not parsed.path.startswith("/repos/"):
            raise FourWsWorkerError("GitHub API returned an unexpected pagination URL.")

        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            url,
            data=body,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
                "X-GitHub-Api-Version": API_VERSION,
                "User-Agent": "KPGS-Trusted-Four-Ws-Worker",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                raw = response.read()
                link = response.headers.get("Link", "")
                next_match = _LINK_NEXT.search(link)
        except urllib.error.HTTPError as error:
            # Do not include response bodies or request headers: either could
            # contain user content or security-sensitive provider diagnostics.
            raise FourWsWorkerError(f"GitHub API request failed with HTTP {error.code}.") from None
        except (urllib.error.URLError, TimeoutError) as error:
            raise FourWsWorkerError(f"GitHub API request failed ({type(error).__name__}).") from None

        try:
            decoded = json.loads(raw.decode("utf-8")) if raw else None
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise FourWsWorkerError("GitHub API returned invalid JSON.") from None
        return decoded, next_match.group(1) if next_match else None

    def get_json(self, endpoint: str) -> Any:
        value, next_url = self._request("GET", endpoint)
        if next_url:
            raise FourWsWorkerError("A non-paginated GitHub API request returned a next page.")
        return value

    def get_all(self, endpoint: str, *, collection_key: str | None = None) -> list[dict[str, Any]]:
        if "?" not in endpoint:
            endpoint += "?per_page=100"
        elif "per_page=" not in endpoint:
            endpoint += "&per_page=100"

        pages: list[dict[str, Any]] = []
        next_url: str | None = endpoint
        page_count = 0
        while next_url:
            page_count += 1
            if page_count > 100:
                raise FourWsWorkerError("GitHub API pagination exceeded 100 pages.")
            decoded, next_url = self._request("GET", next_url)
            records = decoded.get(collection_key) if collection_key and isinstance(decoded, dict) else decoded
            if not isinstance(records, list) or any(not isinstance(record, dict) for record in records):
                raise FourWsWorkerError("GitHub API returned an invalid paginated record collection.")
            pages.extend(records)
        return pages

    def create_check(self, repository: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = self._post_or_patch("POST", f"repos/{repository}/check-runs", payload)
        return response

    def update_check(self, repository: str, check_run_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        response = self._post_or_patch("PATCH", f"repos/{repository}/check-runs/{check_run_id}", payload)
        return response

    def _post_or_patch(self, method: str, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        value, _ = self._request(method, endpoint, payload)
        if not isinstance(value, dict):
            raise FourWsWorkerError("GitHub API returned an invalid check-run response.")
        return value


def verify_webhook_signature(raw_body: bytes, signature_header: str | None, secret: str) -> bool:
    """Verify GitHub's SHA-256 webhook signature using constant-time comparison."""
    if not secret or not signature_header or not signature_header.startswith("sha256="):
        return False
    supplied = signature_header.removeprefix("sha256=")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", supplied):
        return False
    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, supplied.lower())


def parse_webhook_delivery(
    raw_body: bytes,
    *,
    signature_header: str | None,
    webhook_secret: str,
    event_name: str,
    expected_repository: str,
) -> WebhookDelivery | None:
    """Authenticate a webhook and map only supported events to a PR number."""
    if len(raw_body) > 2_000_000:
        raise FourWsWorkerError("Webhook body exceeds the configured size limit.")
    if not verify_webhook_signature(raw_body, signature_header, webhook_secret):
        raise FourWsWorkerError("Webhook signature validation failed.")
    if not _REPOSITORY.fullmatch(expected_repository):
        raise FourWsWorkerError("Configured repository identity is invalid.")
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise FourWsWorkerError("Webhook body is not valid JSON.") from None
    if not isinstance(payload, dict):
        raise FourWsWorkerError("Webhook body must be a JSON object.")

    action = str(payload.get("action") or "")
    if action not in WEBHOOK_EVENTS.get(event_name, frozenset()):
        return None
    repository = payload.get("repository") or {}
    full_name = str(repository.get("full_name") or "") if isinstance(repository, dict) else ""
    if full_name.casefold() != expected_repository.casefold():
        raise FourWsWorkerError("Webhook repository does not match the configured repository.")

    number: Any = None
    pr = payload.get("pull_request")
    if isinstance(pr, dict):
        number = pr.get("number") or payload.get("number")
    elif event_name == "issue_comment":
        issue = payload.get("issue") or {}
        if isinstance(issue, dict) and issue.get("pull_request"):
            number = issue.get("number")
    if isinstance(number, bool) or not isinstance(number, int) or number < 1:
        issue = payload.get("issue")
        if event_name == "issue_comment" and not (isinstance(issue, dict) and issue.get("pull_request")):
            return None
        raise FourWsWorkerError("Webhook does not identify a valid pull request number.")

    return WebhookDelivery(event_name, action, payload, expected_repository, number)


def _project_pr(pr: dict[str, Any]) -> dict[str, Any]:
    user = pr.get("user") or {}
    base = pr.get("base") or {}
    head = pr.get("head") or {}
    return {
        "number": pr.get("number"),
        "body": pr.get("body"),
        "user": {"login": user.get("login"), "type": user.get("type")} if isinstance(user, dict) else {},
        "base": {"ref": base.get("ref")} if isinstance(base, dict) else {},
        "head": {"sha": head.get("sha")} if isinstance(head, dict) else {},
        "updated_at": pr.get("updated_at"),
        "state": pr.get("state"),
    }


def _project_records(records: list[dict[str, Any]], *, kind: str) -> list[dict[str, Any]]:
    projection: list[dict[str, Any]] = []
    for record in records:
        user = record.get("user") or {}
        item = {
            "id": record.get("id"),
            "body": record.get("body"),
            "user": {"login": user.get("login"), "type": user.get("type")} if isinstance(user, dict) else {},
        }
        if kind == "reviews":
            item["state"] = record.get("state")
        if kind == "review_comments":
            item["pull_request_review_id"] = record.get("pull_request_review_id")
        projection.append(item)
    return sorted(projection, key=lambda item: (str(item.get("id")), json.dumps(item, sort_keys=True)))


def _snapshot_fingerprint(snapshot: dict[str, Any]) -> str:
    payload = json.dumps(snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _read_snapshot(api: GitHubApi, repository: str, number: int) -> dict[str, Any]:
    prefix = f"repos/{repository}/pulls/{number}"
    pr = api.get_json(prefix)
    if not isinstance(pr, dict):
        raise FourWsWorkerError("GitHub did not return a pull-request record.")
    reviews = api.get_all(f"{prefix}/reviews?per_page=100")
    review_comments = api.get_all(f"{prefix}/comments?per_page=100")
    issue_comments = api.get_all(f"repos/{repository}/issues/{number}/comments?per_page=100")
    return {
        "pull_request": _project_pr(pr),
        "reviews": _project_records(reviews, kind="reviews"),
        "review_comments": _project_records(review_comments, kind="review_comments"),
        "issue_comments": _project_records(issue_comments, kind="issue_comments"),
    }


def _receipt(number: int, base_branch: str, records: list[dict[str, Any]]) -> tuple[str, str, int]:
    failures = record_failures(records)
    lines = [
        "## Trusted Four Ws structural receipt",
        "",
        f"- Pull request: #{number}",
        f"- Base branch: `{base_branch}`",
        f"- Validator: `{FourWsValidator().validate({'who': 'gate', 'what': 'gate', 'where': 'GitHub App worker', 'why': 'canonical contract'})[1]['schema']}`",
        f"- Current records inspected: {len(records)}",
        f"- Passing records: {len(records) - len(failures)}",
        f"- Failed records: {len(failures)}",
        "",
        "This check validates non-empty WHO, WHAT, WHERE, and WHY structure only. It does not establish truth, evidence quality, owner approval, reviewer authority, or runtime enforcement.",
    ]
    if failures:
        lines.extend(["", "### Records needing correction", ""])
        for item in failures:
            validation = item["validation"]
            name = f"{item['kind']} `{item['id']}` by `{item['actor']}`"
            if validation["missing"]:
                lines.append(f"- {name}: missing or empty `{', '.join(validation['missing'])}`.")
            for error in item["parse_errors"]:
                lines.append(f"- {name}: {error}.")
            lines.append(f"  Validator result: `{validation['cbp_verdict']}`.")
        lines.append("\nUse one explicit line for each field: `WHO: ...`, `WHAT: ...`, `WHERE: ...`, and `WHY: ...`.")
    else:
        lines.append("\nEvery current human-authored record has non-empty WHO, WHAT, WHERE, and WHY fields.")
    return ("failure" if failures else "success", "\n".join(lines), len(failures))


def _check_payload(head_sha: str, outcome: GateOutcome, number: int) -> dict[str, Any]:
    return {
        "name": CHECK_NAME,
        "head_sha": head_sha,
        "external_id": f"fourws-pr-{number}",
        "status": "completed",
        "conclusion": outcome.state,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "output": {
            "title": "Four Ws structure passes" if outcome.state == "success" else "Four Ws structure needs correction",
            "summary": outcome.receipt,
        },
    }


def _publish_check(api: GitHubApi, repository: str, app_id: int, payload: dict[str, Any]) -> int:
    sha = payload["head_sha"]
    endpoint = f"repos/{repository}/commits/{sha}/check-runs?check_name={urllib.parse.quote(CHECK_NAME)}&filter=latest&per_page=100"
    existing = api.get_all(endpoint, collection_key="check_runs")
    own = [
        run
        for run in existing
        if run.get("name") == CHECK_NAME
        and run.get("head_sha") == sha
        and isinstance(run.get("app"), dict)
        and run["app"].get("id") == app_id
        and isinstance(run.get("id"), int)
    ]
    if own:
        current = max(own, key=lambda run: run["id"])
        update_payload = {key: value for key, value in payload.items() if key != "head_sha"}
        updated = api.update_check(repository, current["id"], update_payload)
        if updated.get("head_sha", sha) != sha:
            raise FourWsWorkerError("GitHub updated a check run for an unexpected commit.")
        if not isinstance(updated.get("app"), dict) or updated["app"].get("id") != app_id:
            raise FourWsWorkerError("GitHub updated a check run under an unexpected App identity.")
        return int(updated.get("id", current["id"]))
    created = api.create_check(repository, payload)
    if created.get("head_sha") != sha or created.get("name") != CHECK_NAME:
        raise FourWsWorkerError("GitHub returned a check run for an unexpected commit or context.")
    if not isinstance(created.get("app"), dict) or created["app"].get("id") != app_id:
        raise FourWsWorkerError("GitHub created a check run under an unexpected App identity.")
    check_id = created.get("id")
    if isinstance(check_id, bool) or not isinstance(check_id, int):
        raise FourWsWorkerError("GitHub returned a check run without a valid identifier.")
    return check_id


def process_delivery(
    delivery: WebhookDelivery,
    api: GitHubApi,
    *,
    app_id: int,
    stable_read_attempts: int = 3,
) -> GateOutcome | None:
    """Evaluate live current PR records, then publish only to the latest head SHA."""
    if not _REPOSITORY.fullmatch(delivery.repository):
        raise FourWsWorkerError("Configured repository identity is invalid.")
    if isinstance(delivery.pull_request_number, bool) or delivery.pull_request_number < 1:
        raise FourWsWorkerError("Pull-request number is invalid.")
    if isinstance(app_id, bool) or app_id < 1:
        raise FourWsWorkerError("GitHub App ID is invalid.")
    if stable_read_attempts < 1 or stable_read_attempts > 10:
        raise FourWsWorkerError("Stable-read attempt count must be between 1 and 10.")
    default_branch_record = api.get_json(f"repos/{delivery.repository}")
    if not isinstance(default_branch_record, dict) or not isinstance(default_branch_record.get("default_branch"), str):
        raise FourWsWorkerError("Repository default branch is unavailable.")
    default_branch = default_branch_record["default_branch"]
    prefix = f"repos/{delivery.repository}/pulls/{delivery.pull_request_number}"

    for _attempt in range(stable_read_attempts):
        first = _read_snapshot(api, delivery.repository, delivery.pull_request_number)
        second = _read_snapshot(api, delivery.repository, delivery.pull_request_number)
        if _snapshot_fingerprint(first) != _snapshot_fingerprint(second):
            continue

        pr = second["pull_request"]
        base = pr.get("base") or {}
        head = pr.get("head") or {}
        head_sha = head.get("sha")
        base_branch = base.get("ref")
        if base_branch != default_branch or pr.get("state") != "open":
            return None
        if not isinstance(head_sha, str) or not re.fullmatch(r"[0-9a-fA-F]{40,64}", head_sha):
            raise FourWsWorkerError("The current pull-request head SHA is invalid.")

        # Recheck the current API head immediately before writing. If the head
        # moved during pagination, restart against the new SHA. A check written
        # to an old SHA can never satisfy the newer commit's required context.
        latest = api.get_json(prefix)
        latest_head = ((latest or {}).get("head") or {}).get("sha") if isinstance(latest, dict) else None
        latest_base = ((latest or {}).get("base") or {}).get("ref") if isinstance(latest, dict) else None
        latest_state = latest.get("state") if isinstance(latest, dict) else None
        if latest_head != head_sha or latest_base != default_branch or latest_state != "open":
            continue

        # Evaluate the original, canonical parser/validator and human-vs-bot
        # policy over the complete live API collections represented by the
        # stable snapshot. Event payload text is never used as a receipt.
        live_pr = {
            "number": delivery.pull_request_number,
            "body": pr.get("body"),
            "user": pr.get("user") or {},
        }
        records = collect_records(
            live_pr,
            _read_snapshot_records(second["reviews"], "reviews"),
            _read_snapshot_records(second["review_comments"], "review_comments"),
            _read_snapshot_records(second["issue_comments"], "issue_comments"),
        )
        conclusion, receipt, failed = _receipt(delivery.pull_request_number, default_branch, records)
        outcome = GateOutcome("success" if conclusion == "success" else "failure", head_sha, receipt, len(records), failed)
        _publish_check(api, delivery.repository, app_id, _check_payload(head_sha, outcome, delivery.pull_request_number))
        return outcome

    raise FourWsWorkerError("Pull-request records or head changed during each stable-read attempt; no check was published.")


def _read_snapshot_records(records: list[dict[str, Any]], kind: str) -> list[dict[str, Any]]:
    """Expand a stable fingerprint projection into the input shape the canonical gate consumes."""
    return [dict(record) for record in records]
