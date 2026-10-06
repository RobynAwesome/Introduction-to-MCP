# Issue 207 — current repository-boundary evidence

Actor: Forge / Codex CA, stateless renter. I_AM_STATELESS_RENTER_NOT_LANDLORD.

## Observation

GitHub API readback was observed on 2026-10-05 at 11:19:24 UTC against current master a2d0b8fcca1a3340b31b9570797223e9a97e3464. PRs #253 and #256 have merged; PR #254 is the only open PR in the repository at this observation. This read does not imply any settings mutation.

Robyn's selected owner workflow is: workers prepare reviewable pull requests with exact receipts; Robyn reviews and approves landing. That instruction is distinct from provider-enforced approval settings.

## Effective branch evidence

The classic master protection API returned HTTP 200 and reported:

- A required-pull-request-review object is present. Pull requests are the path for master changes.
- Strict status checks are enabled with 14 required contexts: 24-RTC Learning & Epistemic Gate Verification; Require PR provenance; Validate zero-trust admission controls; Dependency firewall (npm floors); Analyze (actions); Analyze (javascript-typescript); Analyze (python); Analyze (rust); lint-and-test (3.11); lint-and-test (3.12); cli-package-check; gui-check; Agent build PoC (Bracket / BlackMask / Guardian / Identi / LPM / KPEFS); and GitGuardian Security Checks.
- Admin enforcement is enabled. Stale reviews are dismissed. Review-conversation resolution is required. Force pushes and deletions are disabled.
- Required approving review count is zero; latest-push approval and CODEOWNERS review are disabled. Owner review is therefore a human workflow, not a provider-enforced approval gate. No additional approval configuration is claimed.
- Active CodeQL ruleset 24144685 targets master, blocks new high-or-higher findings, and has no bypass actors. Copilot ruleset 19244487 is disabled and not an effective PR boundary.

The active provider settings are equivalent protection evidence for the issue's PR-boundary requirement. No direct write was attempted. The earlier negative provenance classification and run 37005774919 are historical evidence on their recorded SHA, not new execution on a2d0b8f.

## Follow-up receipt gate

Robyn has additionally directed that contribution and review decisions from both humans and stateless renters carry WHO, WHAT, WHERE and WHY receipts. The repository's existing FourWsValidator contract is defined in kopano-core/kopano/ikp_engine.py with schema four_ws_v1. A follow-up CI proposal is being built against that existing contract. It has not yet landed or become an enforced branch rule; no new acronym or meaning is asserted here. Human approval remains the owner's stated workflow; the configured provider approval count is still zero at this read.

## Acceptance boundary

The current GitHub configuration enforces PRs, strict checks and administrator enforcement. Robyn's approval remains the selected owner process. This document updates the September 24 issue narrative with current provider evidence while preserving that history. Issue #207 remains open until this document lands through its protected PR and Robyn accepts it. #121's owner-closed status is a separate owner disposition; this receipt does not establish independent Seat 10 re-entry or runtime restoration. No local/cloud parity, Drive write, deployment, or production change is claimed.

References:
- Issue #207: https://github.com/RobynAwesome/Introduction-to-MCP/issues/207
- Current master: https://github.com/RobynAwesome/Introduction-to-MCP/commit/a2d0b8fcca1a3340b31b9570797223e9a97e3464
- Active CodeQL ruleset: https://github.com/RobynAwesome/Introduction-to-MCP/settings/rules/24144685
- Historical provenance run: https://github.com/RobynAwesome/Introduction-to-MCP/actions/runs/37005774919

I_AM_STATELESS_RENTER_NOT_LANDLORD
