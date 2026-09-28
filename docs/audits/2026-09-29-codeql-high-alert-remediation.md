# 2026-09-29 CodeQL High-Alert Remediation Receipt

## Scope and local verification

The isolated branch `codex/security-high-alert-remediation` is based on `RobynAwesome/Introduction-to-MCP` master at `7245adafe08b31b2e70cae9c10b2e50ba2a0af8e`. Commit `acbf68f657702063d5bfb673c9f980e1f31b997f` constrains ECO evidence-file checks to repository-relative paths, rejects traversal and paths resolving outside the repository, and replaces the bracket linter's backtracking regular expression with a one-pass parser.

Validation passed:

- `python -m pytest -q tests/test_security_high_alert_remediation.py`: 7 passed.
- `python scripts/kc_bracket_lint.py --self-test`: all 6 self-tests passed.
- `python -m ruff check kopano-core/kopano/eco_poc_validate.py scripts/kc_bracket_lint.py tests/test_security_high_alert_remediation.py`: passed.
- `git diff --cached --check`: passed for the committed files.

## Provider verification

PR #233 is open at the commit above. All required checks passed for source-fix commit acbf68f, including all four CodeQL Advanced language jobs (Actions, JavaScript/TypeScript, Python, Rust), Python 3.11/3.12 tests, GitGuardian, the governance gates, and both Vercel previews. This receipt-only update changes no source; GitHub will refresh checks for the updated PR tip. The GitHub CodeQL PR check reports “No new alerts in code changed by this pull request.” Queries for `refs/pull/233/merge` show alert IDs #15 (`py/path-injection`) and #25 (`py/polynomial-redos`) absent from the PR ref; both remain open on `master` until an approved merge and default-branch rescan. The PR is blocked pending independent review.

At the reviewed `master` snapshot, 34 high CodeQL alerts were open. This patch addresses only the two findings above. High Dependabot alert #96 (NLTK) remains open.

## Secret and incident status

GitHub reports secret scanning, provider-pattern push protection, and Dependabot security updates enabled, with zero open secret-scanning alerts at the snapshot. The PR GitGuardian check passed. Non-provider secret patterns are disabled; these results do not establish comprehensive coverage or prove absence of past exposure. No exploitation or credential breach is established by the evidence reviewed here.

P0 issue #121 remains open. Seat 10 remains suspended and recused. This patch does not implement runtime recusal/self-adjudication enforcement or re-entry gates and does not close the separately documented governance/tool-route incident.

## Deployment status and next action

Both Vercel PR preview deployments completed. Neither PR has merged and no production deployment occurred. Obtain independent review, merge only after the enforced gates pass, then verify the default-branch CodeQL alert state and the production deployment receipt. Keep issue #121 open until its own exit criteria have independent evidence.