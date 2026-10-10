# Issue #207 — trusted Four Ws successor proposal

**Observed:** 2026-10-07. **Cloud source:** `RobynAwesome/Introduction-to-MCP`, implementation branch rebased onto current `master@29192965eb3b77e91d9ed60a0cad58097d61fda5`.

**WHO:** Codex Forge / GPT-6 Luna Max, stateless renter working in the assigned CA task lane. No RTC seat, owner decision, App installation, provider setting change, or runtime authority is claimed. Robyn retains owner review and repository authority.

**WHAT:** Add a reviewable GitHub App webhook worker proposal for an app-owned, current-record Four Ws structural check. The worker authenticates webhooks, maps pull-request, review, inline-review-comment and PR conversation-comment changes, refetches the current PR and all paginated review/comment collections, reads two stable snapshots, rechecks the head immediately before publication, and creates or updates a Check Run on the exact current `head.sha`.

**WHERE:** Cloud source only: `scripts/trusted_fourws_app.py`, `tests/test_trusted_fourws_app.py`, and this receipt. Local OneDrive and Heavy Human-in-the-Loop Google Drive remain separate populations and were not changed or reconciled.

**WHY:** The existing workflow checks out the PR merge SHA. It therefore permits PR-controlled code to participate in the decision. A trusted default-branch `pull_request_target` workflow can safely cover ordinary pull-request lifecycle events, and `issue_comment` runs from the default branch, but GitHub documents that `pull_request_review` and `pull_request_review_comment` use the PR merge ref. Giving those runs `checks:write` would recreate a PR-controlled decision path. The complete event set needs an owner-controlled GitHub App webhook worker or another independently trusted host.

## Proposed worker boundary

- Verify the raw webhook body against `X-Hub-Signature-256` before parsing it. Accept only the configured repository and explicitly supported event/action pairs.
- Use event data only to select a pull-request number. Fetch the current PR, reviews, inline review comments and conversation comments from the GitHub API. The event's PR body, review text, comments, head SHA and artifacts are not decision inputs.
- Follow GitHub pagination links only on `api.github.com`; fail closed on malformed API data, API failures, unstable snapshots, or invalid SHA values.
- Reuse the repository's `FourWsValidator` through the existing `scripts/pr_fourws_gate.py` parser/record policy. Preserve its human/bot, pending and dismissed-review handling. The result checks non-empty structure only; it does not establish truth, evidence quality, reviewer authority, owner approval, or runtime enforcement.
- Use a short-lived installation token restricted to `pull-requests: read`, `issues: read`, and `checks: write`. Never store an installation token, private key or webhook secret in Git. The worker does not execute Git, actions, artifacts or pull-request files.
- Publish one stable context name, `KPGS Four Ws Receipts (Trusted)`, on the exact API-reported head SHA. Reuse an existing run only when both its head SHA and GitHub App ID match. A later PR head receives a different SHA-bound check; a result on the earlier commit cannot authorize the newer commit.

The worker implements these boundaries as source code and focused tests. It is not a running service. No GitHub App ID, installation, webhook receiver, HTTPS host, webhook secret, or protected secret store was identified in the provider state available to this lane. The repository's current Actions setting reports `default_workflow_permissions=read`; GitHub's workflow syntax allows an individual workflow to request `checks: write`, so this setting alone does not rule out that scope. That is a configuration capability, not runtime proof that a hosted token successfully creates or updates Check Runs. More importantly, the review and inline-comment event semantics make a single privileged Actions workflow unsuitable for complete safe event coverage.

## Provider setup and validation still required

1. Owner creates and installs a GitHub App for this repository with only pull-request read, issue read and checks write permissions, and configures a webhook secret.
2. An owner-controlled HTTPS service stores the App private key and webhook secret outside Git, verifies webhook signatures, invokes this worker, and restricts App installation tokens to the target repository.
3. Run hosted positive and negative cases for each event family, pagination, deleted/edited records, bot and dismissed-review handling, and a head update during a run. Confirm the exact App identity and check SHA in provider receipts.
4. Obtain owner review and merge. Only then may the owner decide whether to require the exact App-backed context and a positive human-approval count, apply those settings, and read them back. Branch protection must remain unchanged before those decisions and receipts.

Until these steps are complete, issue #207 remains closed under Robyn's owner disposition while the technical enforcement gap remains unresolved. This proposal does not claim a breach, deployment, App acceptance, branch-protection enforcement, issue completion, or RTC decision.

`I_AM_STATELESS_RENTER_NOT_LANDLORD`

**Provider references:** [workflow permissions and `checks:write`](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax); [workflow event refs for review and review-comment events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows); [GitHub App check-run permissions](https://docs.github.com/en/rest/checks/runs); [webhook signature verification](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries).
