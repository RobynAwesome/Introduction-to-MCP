from __future__ import annotations

import hashlib
import hmac
import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import trusted_fourws_app as worker  # noqa: E402


GOOD_BODY = "WHO: renter\nWHAT: checked records\nWHERE: trusted worker\nWHY: validate structure"
SHA_A = "a" * 40
SHA_B = "b" * 40
REPOSITORY = "RobynAwesome/Introduction-to-MCP"


def actor(login: str, actor_type: str = "User") -> dict:
    return {"login": login, "type": actor_type}


def pr_record(sha: str, body: str = GOOD_BODY, *, updated_at: str = "2026-10-07T00:00:00Z") -> dict:
    return {
        "number": 17,
        "body": body,
        "user": actor("author"),
        "base": {"ref": "master", "sha": SHA_A},
        "head": {"sha": sha},
        "updated_at": updated_at,
        "state": "open",
    }


def signed_body(payload: dict, secret: str = "test-secret") -> tuple[bytes, str]:
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    digest = hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
    return raw, f"sha256={digest}"


def payload(event: str, action: str, number: int = 17) -> dict:
    base = {"action": action, "repository": {"full_name": REPOSITORY}}
    if event == "issue_comment":
        base["issue"] = {"number": number, "pull_request": {"url": "https://api.github.com/repos/RobynAwesome/Introduction-to-MCP/pulls/17"}}
        base["comment"] = {"body": "event-supplied body must not be trusted"}
    else:
        base["number"] = number
        base["pull_request"] = {**pr_record(SHA_A), "body": "event-supplied body must not be trusted"}
    return base


class FakeApi:
    def __init__(self, prs: list[dict] | None = None, *, reviews=None, review_comments=None, issue_comments=None):
        self.prs = list(prs or [pr_record(SHA_A)])
        self.pr_calls = 0
        self.reviews = list(reviews or [])
        self.review_comments = list(review_comments or [])
        self.issue_comments = list(issue_comments or [])
        self.created: list[dict] = []
        self.updated: list[tuple[int, dict]] = []
        self.check_runs: list[dict] = []
        self.list_calls: list[str] = []
        self.app_id = 111

    def get_json(self, endpoint: str):
        if endpoint == f"repos/{REPOSITORY}":
            return {"default_branch": "master"}
        if endpoint == f"repos/{REPOSITORY}/pulls/17":
            index = min(self.pr_calls, len(self.prs) - 1)
            self.pr_calls += 1
            return self.prs[index]
        raise AssertionError(f"unexpected GET {endpoint}")

    def get_all(self, endpoint: str, *, collection_key: str | None = None):
        self.list_calls.append(endpoint)
        if endpoint.startswith(f"repos/{REPOSITORY}/commits/"):
            assert collection_key == "check_runs"
            return list(self.check_runs)
        if endpoint.startswith(f"repos/{REPOSITORY}/pulls/17/reviews"):
            return list(self.reviews)
        if endpoint.startswith(f"repos/{REPOSITORY}/pulls/17/comments"):
            return list(self.review_comments)
        if endpoint.startswith(f"repos/{REPOSITORY}/issues/17/comments"):
            return list(self.issue_comments)
        raise AssertionError(f"unexpected list {endpoint}")

    def create_check(self, repository: str, payload: dict):
        assert repository == REPOSITORY
        check = {
            **payload,
            "id": 900,
            "name": worker.CHECK_NAME,
            "head_sha": payload["head_sha"],
            "app": {"id": self.app_id},
        }
        self.created.append(check)
        return check

    def update_check(self, repository: str, check_run_id: int, payload: dict):
        assert repository == REPOSITORY
        self.updated.append((check_run_id, payload))
        return {**payload, "id": check_run_id, "head_sha": SHA_A, "app": {"id": self.app_id}}


@pytest.mark.parametrize(
    ("event_name", "action"),
    [
        ("pull_request", "opened"),
        ("pull_request", "edited"),
        ("pull_request", "reopened"),
        ("pull_request", "synchronize"),
        ("pull_request", "ready_for_review"),
        ("pull_request_review", "submitted"),
        ("pull_request_review", "edited"),
        ("pull_request_review", "dismissed"),
        ("pull_request_review_comment", "created"),
        ("pull_request_review_comment", "edited"),
        ("pull_request_review_comment", "deleted"),
        ("issue_comment", "created"),
        ("issue_comment", "edited"),
        ("issue_comment", "deleted"),
    ],
)
def test_webhook_router_covers_pr_review_inline_and_conversation_changes(event_name, action):
    raw, signature = signed_body(payload(event_name, action))

    delivery = worker.parse_webhook_delivery(
        raw,
        signature_header=signature,
        webhook_secret="test-secret",
        event_name=event_name,
        expected_repository=REPOSITORY,
    )

    assert delivery is not None
    assert delivery.pull_request_number == 17
    assert delivery.event_name == event_name
    assert delivery.action == action


def test_webhook_rejects_bad_signature_and_wrong_repository():
    raw, _ = signed_body(payload("pull_request", "opened"))
    with pytest.raises(worker.FourWsWorkerError, match="signature"):
        worker.parse_webhook_delivery(
            raw,
            signature_header="sha256=" + "0" * 64,
            webhook_secret="test-secret",
            event_name="pull_request",
            expected_repository=REPOSITORY,
        )

    wrong = payload("pull_request", "opened")
    wrong["repository"]["full_name"] = "attacker/other"
    wrong_raw, wrong_signature = signed_body(wrong)
    with pytest.raises(worker.FourWsWorkerError, match="does not match"):
        worker.parse_webhook_delivery(
            wrong_raw,
            signature_header=wrong_signature,
            webhook_secret="test-secret",
            event_name="pull_request",
            expected_repository=REPOSITORY,
        )


def test_issue_comment_router_ignores_regular_issue_comments():
    issue = {"action": "created", "repository": {"full_name": REPOSITORY}, "issue": {"number": 17}}
    raw, signature = signed_body(issue)
    assert worker.parse_webhook_delivery(
        raw,
        signature_header=signature,
        webhook_secret="test-secret",
        event_name="issue_comment",
        expected_repository=REPOSITORY,
    ) is None


def test_issue_comment_router_ignores_malformed_issue_record():
    issue = {"action": "created", "repository": {"full_name": REPOSITORY}, "issue": "not-an-object"}
    raw, signature = signed_body(issue)
    assert worker.parse_webhook_delivery(
        raw,
        signature_header=signature,
        webhook_secret="test-secret",
        event_name="issue_comment",
        expected_repository=REPOSITORY,
    ) is None


def test_process_reads_live_current_records_and_ignores_untrusted_event_body_and_head():
    raw, signature = signed_body(payload("pull_request", "opened"))
    delivery = worker.parse_webhook_delivery(
        raw,
        signature_header=signature,
        webhook_secret="test-secret",
        event_name="pull_request",
        expected_repository=REPOSITORY,
    )
    api = FakeApi([pr_record(SHA_A, "WHO: current author\nWHAT: only two fields")])

    outcome = worker.process_delivery(delivery, api, app_id=111)

    assert outcome is not None
    assert outcome.state == "failure"
    assert "where" in outcome.receipt
    assert "event-supplied body" not in outcome.receipt
    assert api.created[0]["head_sha"] == SHA_A
    assert api.created[0]["conclusion"] == "failure"
    assert api.list_calls[:6] == [
        f"repos/{REPOSITORY}/pulls/17/reviews?per_page=100",
        f"repos/{REPOSITORY}/pulls/17/comments?per_page=100",
        f"repos/{REPOSITORY}/issues/17/comments?per_page=100",
    ] * 2
    assert api.list_calls[6].startswith(f"repos/{REPOSITORY}/commits/{SHA_A}/check-runs?")


def test_current_human_bot_and_dismissed_record_policy_uses_canonical_validator():
    api = FakeApi(
        [pr_record(SHA_A)],
        reviews=[
            {"id": 1, "state": "COMMENTED", "user": actor("human"), "body": "WHO: only"},
            {"id": 2, "state": "COMMENTED", "user": actor("robot[bot]", "Bot"), "body": "automated"},
            {"id": 3, "state": "DISMISSED", "user": actor("former"), "body": ""},
        ],
        review_comments=[
            {"id": 4, "pull_request_review_id": 3, "user": actor("former"), "body": ""},
        ],
        issue_comments=[{"id": 5, "user": actor("conversation"), "body": GOOD_BODY}],
    )

    outcome = worker.process_delivery(
        worker.WebhookDelivery("pull_request_review", "submitted", {}, REPOSITORY, 17),
        api,
        app_id=111,
    )

    assert outcome is not None
    assert outcome.record_count == 3  # PR body, one human review, one human conversation comment.
    assert outcome.failed_count == 1
    assert "review `1` by `human`" in outcome.receipt
    assert "robot[bot]" not in outcome.receipt
    assert "former" not in outcome.receipt
    assert "four_ws_v1" in outcome.receipt
    assert "does not establish truth" in outcome.receipt


def test_head_change_during_pagination_retries_and_publishes_to_latest_api_sha():
    # Two snapshots observe A, then the immediate pre-write read sees B; the
    # next stable round reads B twice and verifies B again.
    api = FakeApi([pr_record(SHA_A), pr_record(SHA_A), pr_record(SHA_B), pr_record(SHA_B), pr_record(SHA_B)])
    delivery = worker.WebhookDelivery(
        "pull_request_review_comment",
        "created",
        {"pull_request": {"head": {"sha": SHA_A}}},
        REPOSITORY,
        17,
    )

    outcome = worker.process_delivery(delivery, api, app_id=111)

    assert outcome is not None
    assert outcome.head_sha == SHA_B
    assert api.created[0]["head_sha"] == SHA_B
    assert SHA_A != api.created[0]["head_sha"]


def test_non_default_base_is_not_published_as_a_required_default_branch_context():
    api = FakeApi([{
        **pr_record(SHA_A),
        "base": {"ref": "release", "sha": SHA_A},
    }])

    outcome = worker.process_delivery(
        worker.WebhookDelivery("pull_request", "opened", {}, REPOSITORY, 17),
        api,
        app_id=111,
    )

    assert outcome is None
    assert api.created == []


def test_check_update_selects_only_same_app_context_and_exact_head():
    api = FakeApi()
    api.check_runs = [
        {"id": 10, "name": worker.CHECK_NAME, "head_sha": SHA_A, "app": {"id": 222}},
        {"id": 11, "name": worker.CHECK_NAME, "head_sha": SHA_B, "app": {"id": 111}},
        {"id": 12, "name": worker.CHECK_NAME, "head_sha": SHA_A, "app": {"id": 111}},
    ]
    outcome = worker.GateOutcome("success", SHA_A, "receipt", 1, 0)

    check_id = worker._publish_check(api, REPOSITORY, 111, worker._check_payload(SHA_A, outcome, 17))

    assert check_id == 12
    assert [check[0] for check in api.updated] == [12]
    assert api.created == []


def test_worker_has_no_process_or_git_checkout_path_for_untrusted_head_content():
    source = (REPO_ROOT / "scripts" / "trusted_fourws_app.py").read_text(encoding="utf-8")
    assert "subprocess" not in source
    assert "git checkout" not in source
    assert "head_sha" in source  # SHA is used only as a Check Run target.


def test_github_app_api_follows_link_pagination_and_flattens_current_items(monkeypatch):
    class Headers(dict):
        def get(self, key, default=None):
            return super().get(key.lower(), default)

    class Response:
        def __init__(self, body, link=""):
            self._body = json.dumps(body).encode()
            self.headers = Headers({"link": link})

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return self._body

    first_url = "https://api.github.com/repos/owner/repo/pulls/7/reviews?per_page=100"
    second_url = "https://api.github.com/repos/owner/repo/pulls/7/reviews?per_page=100&page=2"
    responses = {
        first_url: Response([{"id": 1}], f'<{second_url}>; rel="next"'),
        second_url: Response([{"id": 2}]),
    }
    seen = []

    def fake_urlopen(request, timeout):
        assert timeout == 20
        seen.append(request.full_url)
        return responses[request.full_url]

    monkeypatch.setattr(worker.urllib.request, "urlopen", fake_urlopen)
    client = worker.GitHubAppApi("test-installation-token")

    assert client.get_all("repos/owner/repo/pulls/7/reviews") == [{"id": 1}, {"id": 2}]
    assert seen == [first_url, second_url]


def test_github_api_refuses_pagination_urls_outside_github_api(monkeypatch):
    class Response:
        headers = {"Link": '<https://attacker.invalid/steal?x=1>; rel="next"'}

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return b"[]"

    monkeypatch.setattr(worker.urllib.request, "urlopen", lambda *_args, **_kwargs: Response())
    client = worker.GitHubAppApi("test-installation-token")
    with pytest.raises(worker.FourWsWorkerError, match="unexpected pagination URL"):
        client.get_all("repos/owner/repo/pulls/7/reviews")
