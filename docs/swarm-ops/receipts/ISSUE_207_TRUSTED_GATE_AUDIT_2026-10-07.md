# Issue #207 — trusted Four Ws gate audit

**Observed:** 2026-10-06 22:26:09 UTC. **Cloud source:** `RobynAwesome/Introduction-to-MCP`, `master@cf6cdaa5769465f7c2f7b4c5797e60b7122e7ac9`. The provider branch readback matched that SHA.

**WHO:** Codex Forge coordinating renter / CA task role; the delegated renter performed a read-only Cloud security audit. No RTC seat, owner decision, or provider setting authority is claimed.

**WHAT:** Determine whether the merged Four Ws workflow is a trusted, currently required gate and record the safe next design.

**WHERE:** Cloud workflow `.github/workflows/kpgs-fourws-review-gate.yml`, validator `scripts/pr_fourws_gate.py`, canonical validator `kopano-core/kopano/ikp_engine.py`, tests `tests/test_pr_fourws_gate.py`, and live master branch protection. Local and Drive were not treated as mirrors; no files or provider settings were changed in the audit lane.

**WHY:** A green status is useful only if the code producing it is trusted, reads current evidence, and is required for the commit being reviewed.

## Findings

- The workflow listens to `pull_request`, `pull_request_review`, `pull_request_review_comment`, and `issue_comment`. It grants `pull-requests: read` and `issues: read` (`.github/workflows/kpgs-fourws-review-gate.yml`, lines 3–16), fetches and checks out `github.sha` (lines 29–36), then runs `scripts/pr_fourws_gate.py` with `GH_TOKEN` in its environment (lines 38–41).
- GitHub documents that `pull_request`, `pull_request_review`, and `pull_request_review_comment` workflow code runs from the PR merge commit. The checked-out validator imports from that fetched tree and passes the token environment to `gh api` (`scripts/pr_fourws_gate.py`, lines 15–18 and 148–165). Fork pull requests receive a read-only token and no other secrets under GitHub's documented policy. The audited workflow therefore still lets PR-controlled code participate in the gate decision. Same-repository Actions secret policy was not inspected, so this audit does **not** establish credential exposure or a breach.
- The script reads current PR descriptions, reviews, inline comments and conversation comments with REST API calls (lines 190–199), but the canonical validation only checks for non-empty fields (`kopano-core/kopano/ikp_engine.py`, lines 32–49). That validates shape, not truth, evidence quality, reviewer authority, or genuine approval.
- `tests/test_pr_fourws_gate.py` names one test as using a trusted checkout (lines 179–196), but it asserts fetching/checking out `github.sha`; because that SHA is the PR merge commit for these events, the test does not establish trusted-base execution.
- Live master protection at this observation had 14 strict required contexts; `Require current Four Ws receipts` was absent. `required_approving_review_count=0`. Thus the merged workflow is not currently a required merge-blocking context, and no positive approval threshold is enforced. Issue #207 remains closed by owner disposition; that does not close this technical gap.

## Safe design and stop condition

Preferred architecture is an owner-installed GitHub App webhook worker. Webhook events should only identify and schedule a pull request; the worker should re-fetch complete current PR/review/comment records with pagination, run app-owned code without checking out or executing PR code/artifacts, and publish one stable check to the exact latest PR `head.sha`. Keep App permissions to PR read, issue read, and checks write, and bind the required context to that App. Tests must cover event mapping, pagination and edits/deletions/dismissals, bot/inactive reviews, stale-head rejection, and accepted/rejected check outcomes.

A trusted-base `pull_request_target` workflow is a possible alternative only after its lifecycle/event coverage and head-SHA association are proven; it must never check out or execute PR content. No such worker or safe workflow successor was implemented in this audit because the target App and hosting setup are not established. Keep branch protection unchanged and do not claim enforcement until trusted code is reviewed/merged, the exact App context is required, provider settings are read back, and both accepted and rejected paths are exercised.

**Provider references:** [GitHub Actions `pull_request_target` security](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target); [workflow event SHA/ref semantics](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows); [Checks REST API](https://docs.github.com/en/rest/guides/using-the-rest-api-to-interact-with-checks); [required status check freshness](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks).

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
