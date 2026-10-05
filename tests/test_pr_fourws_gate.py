from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import pr_fourws_gate as gate  # noqa: E402


GOOD_BODY = """WHO: AG, stateless renter
WHAT: reviewed the permission boundary
WHERE: .github/workflows/kpgs-fourws-review-gate.yml
WHY: confirm this event only reads pull-request records"""


def actor(login: str, actor_type: str = "User") -> dict:
    return {"login": login, "type": actor_type}


def test_parse_four_ws_accepts_explicit_markdown_labels_and_wrapped_values():
    fields, errors = gate.parse_four_ws(
        """**WHO:** AG renter
**WHAT:** checked the event boundary
**WHERE:**
  `.github/workflows/check.yml`
**WHY:**
  It only has read permissions."""
    )

    assert errors == []
    assert fields == {
        "who": "AG renter",
        "what": "checked the event boundary",
        "where": "`.github/workflows/check.yml`",
        "why": "It only has read permissions.",
    }


def test_missing_field_uses_canonical_four_ws_failure_receipt():
    records = gate.collect_records(
        {"number": 17, "user": actor("reviewer"), "body": "WHO: Renter\nWHAT: Audited\nWHERE: workflow"},
        [],
        [],
        [],
    )
    failure = gate.record_failures(records)[0]

    assert failure["validation"]["schema"] == "four_ws_v1"
    assert failure["validation"]["missing"] == ["why"]
    assert failure["validation"]["cbp_verdict"] == "CBP_DECLINE:missing=['why']"


def test_reviews_comments_and_inline_comments_require_four_ws_but_bots_are_exempt():
    records = gate.collect_records(
        {"number": 17, "user": actor("author"), "body": GOOD_BODY},
        [
            {"id": 1, "state": "APPROVED", "user": actor("human-reviewer"), "body": "WHO: reviewer"},
            {"id": 2, "state": "COMMENTED", "user": actor("actions[bot]", "Bot"), "body": "automated note"},
        ],
        [{"id": 3, "user": actor("inline-reviewer"), "body": GOOD_BODY, "pull_request_review_id": 1}],
        [{"id": 4, "user": actor("conversation-author"), "body": "WHO: author\nWHAT: replied"}],
    )

    assert [(r["kind"], r["id"]) for r in records] == [
        ("PR description", "#17"),
        ("review", "1"),
        ("inline review comment", "3"),
        ("PR conversation comment", "4"),
    ]
    assert len(gate.record_failures(records)) == 2


def test_review_dismissal_removes_its_review_and_inline_comments_from_current_gate():
    records = gate.collect_records(
        {"number": 17, "user": actor("author"), "body": GOOD_BODY},
        [{"id": 9, "state": "DISMISSED", "user": actor("reviewer"), "body": ""}],
        [{"id": 10, "pull_request_review_id": 9, "user": actor("reviewer"), "body": ""}],
        [],
    )

    assert len(records) == 1
    assert gate.record_failures(records) == []


def test_pending_review_and_its_inline_comments_are_not_submitted_receipts():
    records = gate.collect_records(
        {"number": 17, "user": actor("author"), "body": GOOD_BODY},
        [{"id": 11, "state": "PENDING", "user": actor("reviewer"), "body": ""}],
        [{"id": 12, "pull_request_review_id": 11, "user": actor("reviewer"), "body": ""}],
        [],
    )

    assert len(records) == 1
    assert gate.record_failures(records) == []


def test_gate_uses_edited_current_records_and_ignores_deleted_comments_omitted_by_api():
    pr = {"number": 17, "user": actor("author"), "body": GOOD_BODY, "base": {"ref": "master"}}
    empty_review = [{"id": 5, "state": "COMMENTED", "user": actor("reviewer"), "body": ""}]
    edited_review = [{"id": 5, "state": "COMMENTED", "user": actor("reviewer"), "body": GOOD_BODY}]

    assert gate.record_failures(gate.collect_records(pr, empty_review, [], []))
    assert gate.record_failures(gate.collect_records(pr, edited_review, [], [])) == []
    assert gate.record_failures(gate.collect_records(pr, [], [], [])) == []


def test_comment_event_maps_to_pr_but_regular_issue_comment_does_not():
    assert gate.pull_request_number({"issue": {"number": 22, "pull_request": {"url": "..."}}}) == 22
    assert gate.pull_request_number({"issue": {"number": 22}}) is None


def test_gate_reads_all_current_record_collections_and_reports_specific_failures():
    seen = []
    responses = {
        "repos/owner/repo/pulls/17": {
            "number": 17,
            "user": actor("author"),
            "body": GOOD_BODY,
            "base": {"ref": "master", "sha": "abc123"},
        },
        "repos/owner/repo/pulls/17/reviews?per_page=100": [
            {"id": 7, "state": "APPROVED", "user": actor("reviewer"), "body": "WHO: reviewer"}
        ],
        "repos/owner/repo/pulls/17/comments?per_page=100": [],
        "repos/owner/repo/issues/17/comments?per_page=100": [],
    }

    def get_object(endpoint):
        seen.append(endpoint)
        return responses[endpoint]

    def get_list(endpoint):
        seen.append(endpoint)
        return responses[endpoint]

    state, receipt = gate.evaluate_pull_request("owner/repo", 17, api_object=get_object, api_list=get_list)

    assert state == "fail"
    assert "review `7` by `reviewer`" in receipt
    assert "missing or empty `what, where, why`" in receipt
    assert seen == list(responses)


def test_gate_skips_non_master_pull_requests_without_fetching_comments():
    state, receipt = gate.evaluate_pull_request(
        "owner/repo",
        17,
        api_object=lambda _endpoint: {"base": {"ref": "release"}},
        api_list=lambda _endpoint: pytest.fail("comments should not be fetched for another base branch"),
    )

    assert state == "skip"
    assert "targets `release`" in receipt


def test_paginated_github_api_records_are_flattened_across_pages(monkeypatch):
    calls = []

    class Result:
        stdout = '[[{"id":1}],[{"id":2}]]'

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return Result()

    monkeypatch.setattr(gate.subprocess, "run", fake_run)

    assert gate._gh_list("repos/owner/repo/pulls/17/reviews?per_page=100") == [{"id": 1}, {"id": 2}]
    assert "--paginate" in calls[0][0]
    assert "--slurp" in calls[0][0]


def test_workflow_uses_only_unprivileged_events_read_permissions_and_trusted_checkout():
    workflow_path = REPO_ROOT / ".github" / "workflows" / "kpgs-fourws-review-gate.yml"
    workflow = yaml.load(workflow_path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    events = workflow["on"]
    job = workflow["jobs"]["fourws-review-gate"]
    event_fetch = job["steps"][0]

    assert set(events) == {"pull_request", "pull_request_review", "pull_request_review_comment", "issue_comment"}
    assert "pull_request_target" not in events
    assert workflow["permissions"] == {"pull-requests": "read", "issues": "read"}
    assert event_fetch["env"]["EVENT_SHA"] == "${{ github.sha }}"
    assert "git fetch --quiet --no-tags --depth=1 origin \"$EVENT_SHA\"" in event_fetch["run"]
    assert "git checkout --quiet --detach FETCH_HEAD" in event_fetch["run"]
    assert job["steps"][1]["env"]["GH_TOKEN"] == "${{ github.token }}"
    source = workflow_path.read_text(encoding="utf-8")
    assert "uses:" not in source
    assert "secrets." not in source
    assert "id-token: write" not in source
