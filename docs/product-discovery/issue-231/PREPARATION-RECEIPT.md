# Preparation receipt — issue #231

> **Added 2026-10-01. This file is not deleted.** Master Robyn: Seat 10 stays occupied by ANTIGRAVITY as Lead Developer. The suspension sentence later in this file stays. Codex Forge wrote it on 2026-09-29. It is not the current order. Issue #121 stays open. The field-kit content below is unchanged.

- Date prepared: 2026-09-28; security/enforcement refresh: 2026-09-29 SAST
- Actor: Codex Forge, stateless renter — `I_AM_STATELESS_RENTER_NOT_LANDLORD`
- Local preservation checkout: `codex/kc-sovereign-gui-full-dev` at `e24b1aa0874a637477e6d436c032646cfa236aed`; 27 pre-existing modified/untracked paths preserved.
- Cloud source at entry: `RobynAwesome/Introduction-to-MCP` `master@7245adafe08b31b2e70cae9c10b2e50ba2a0af8e`; live issue #231 open.
- No user interview, participant, WhatsApp message, consent, estimate, receipt or seven-day observation is represented by this artifact.
- Full original DH transcript was not inspected. The finding about earlier conversations comes from Robyn's testimony as captured in issue #231 and the pasted handoff.
- Contents: field instructions, draft data-use note, private empty-ledger schema, independent Codex method review, and pending Cassey review handoff.
- Privacy boundary: the private ledger is ignored by Git in any copy intended for code review. Do not put names, telephone numbers, raw chats, audio or locations in tracked files, cloud issues, or model prompts.
- Arithmetic examples in `FIELD-KIT.md` are synthetic checks, not field data.
- Method boundary: issue #231's literal second-contact metric remains preserved with event type and repeat-use reported separately. No issue metric was edited.
- State: **PREPARATION ONLY / NO FIELD RECEIPTS / Cassey review pending**.
- Next admissible action: human review and editing of the draft wording; if accepted, Robyn conducts the manual opt-in invitations. After real receipts exist, request a separate Cassey review and make an evidence-scoped decision.

## Repository security snapshot (2026-09-29)

Verified against the live GitHub API as repository administrator, account `RobynAwesome`:

- `master` was unprotected before this task. Branch protection now requires one approval, approval after the latest push, dismissal of stale approvals, resolution of review conversations, and 14 named checks (CI, four CodeQL jobs, governance gates and GitGuardian). Administrators are subject to the rule; deletion and force push are disabled; branches must be up to date.
- Active ruleset `24144685` requires CodeQL results and blocks new high or critical code-scanning security findings on `master`. It has no bypass actors.
- Secret scanning, push protection and Dependabot security updates are enabled. GitHub reports zero open secret alerts at the time of this check. Non-provider-pattern scanning remains disabled.
- Open security items remain: 34 high-severity CodeQL alerts at `7245ada`; one open high NLTK alert `#96` (`GHSA-8mgp-746c-j5xp`). The advisory affects NLTK through 3.10.3 and reports no patched release. Do not treat enabling Dependabot as remediation of that alert.
- CodeQL findings on checked-in reference paths remain part of the 34-alert baseline; the merge rule is for new findings in changed lines and does not resolve old alerts.
- The open P0 incident issue #121 remains open. Its status is Seat 10 suspended and recused; this repository gate does not implement the requested runtime recusal gate or independently validate re-entry.
- After Robyn fixed billing, the same-head rerun for PR #213 passed governance gates, both Python versions, JavaScript/Python/Actions CodeQL, CLI and GUI checks. The swarm proof and Agent build PoC failed; the PoC artifact reports 19/20 checks, with boot_v1_status failing as active=None and governance_verdict UNRESOLVED. Rust CodeQL was still running at this receipt snapshot. A separate post-job cleanup reported no URL for submodule path KasiLink in .gitmodules. Review those results on #213 before treating that PR as validated; GitGuardian and Vercel previews are not production proof.
- No production application was deployed by this preparation/security task. A static human-operated field kit is not a driver dispatcher or runtime feature.

These settings are live GitHub configuration, not source files. The GitHub protection API responses are the control receipts. The source branch and pull request provide the versioned documentation receipt.
