# GitHub security and breach-enforcement receipt

- Date: 2026-09-29 SAST
- Actor: Codex Forge, stateless renter — `I_AM_STATELESS_RENTER_NOT_LANDLORD`
- Scope: live GitHub repository settings and alert snapshot for `RobynAwesome/Introduction-to-MCP`; this is a bounded repository-level receipt, not a whole-estate security audit or penetration test.
- Cloud source at inspection: `master@7245adafe08b31b2e70cae9c10b2e50ba2a0af8e`.

## Controls changed and verified

Before this work, the `master` branch protection endpoint returned **Branch not protected**. Repository metadata showed Secret Scanning and Dependabot security updates disabled. There were no active repository rulesets; an existing Copilot code-quality ruleset was disabled.

The following controls are now active and re-read from GitHub after applying them:

- `master` requires pull requests, one approval, approval after the latest push, stale-review dismissal, resolved review conversations, an up-to-date branch, and 14 named passing checks from GitHub Actions and GitGuardian. Administrators are included. Deletion and force pushes are disabled.
- Active repository ruleset **24144685**, targeted only at `refs/heads/master`, has no bypass actors. It requires CodeQL analysis and blocks new high or critical security findings identified on lines changed by the pull request.
- Secret scanning, push protection and Dependabot security updates are enabled. GitHub reports zero open secret alerts as of this check. The optional non-provider secret patterns setting remains disabled.

GitHub’s ruleset documentation specifies that code scanning merge protection applies when an alert is identified on lines included in the pull request diff; the new rule therefore gates new findings without treating the historical baseline as repaired. [GitHub Code Scanning merge protection](https://docs.github.com/en/code-security/concepts/code-scanning/merge-protection), [ruleset API](https://docs.github.com/en/rest/repos/rules).

## Open findings and incident boundary

At the inspected cloud head, GitHub listed **34 open high-severity CodeQL alerts**: 18 Rust clear-text logging/transmission findings in checked-in reference paths (17 logging, 1 transmission); 7 JavaScript DOM XSS alerts; and 9 other findings (2 JavaScript URL-sanitization, 2 Python clear-text logging, 1 Python URL-sanitization, 1 Python path-injection, 1 Python polynomial regular-expression denial-of-service, 1 Python reflected XSS, and 1 weak sensitive-data hash). Some findings touch current scripts, web assets or API code. The snapshot does not prove these findings were exploited. Existing alerts remain open pending path-by-path validation and remediation.

The high-severity Dependabot alert **#96** affects locked NLTK 3.10.3. The GitHub-reviewed advisory says affected versions include `<=3.10.3` and lists no patched version. In this checkout, repository search found the NLTK use in `kopano-core/kopano/tools/sentiment_analyzer.py` for VADER sentiment and lexicon download; it did not find the advisory’s named model-artifact APIs in application, script or test code. This narrows observed exposure; it does not resolve the dependency alert or prove every runtime path safe. [GitHub advisory GHSA-8mgp-746c-j5xp](https://github.com/advisories/GHSA-8mgp-746c-j5xp).

The P0 governance incident **#121** remains open. Its current disposition is Seat 10 suspended and recused, pending independent re-entry proof or a separately governed decommission decision. GitHub review protection adds an independent merge boundary. It does **not** implement the missing runtime recusal gate, test model behavior, prove authenticated browser routing or re-entry, or reinstate a seat.

PR **#213** remains open and blocked pending required checks and approval. After billing was fixed, the same-head rerun passed governance gates, both Python versions, JavaScript/Python/Actions CodeQL, CLI and GUI checks. The swarm proof and Agent build PoC failed; its artifact reports 19/20 checks, with boot_v1_status failing as active=None and governance_verdict=UNRESOLVED. Rust CodeQL was still running at this receipt snapshot. A separate post-job cleanup reported no URL for submodule path KasiLink in .gitmodules. Review and remediate those results on #213 before treating it as validated. GitGuardian and Vercel preview checks succeeded on the prior attempt and do not constitute a production deploy.

## Remaining work

1. Keep #121 open and preserve its recusal boundary. A separate implementation issue/PR must make a machine-readable recusal state block self-adjudication at each applicable runtime, then prove the gate with adversarial tests and independent review.
2. Complete Rust CodeQL on #213, then repair or explicitly disposition the boot_v1_status failure and the missing KasiLink submodule URL; rerun affected required checks before treating that PR as validated.
3. Triage each CodeQL alert against current deployment/exposure, fix the confirmed current-code paths first, and preserve precise dismissals only where source review proves a finding is false positive or unreachable.
4. Track NLTK upstream remediation. Until a fixed release exists, verify that no untrusted input can choose paths passed to the vulnerable model-artifact APIs; do not claim Dependabot resolved #96.
5. Recheck secret scanning after GitHub completes its initial scan; rotate any credential GitHub finds or any separately evidenced exposure. A new scanner setting does not revoke previously exposed credentials.

No production application was deployed as part of this receipt. The issue #231 materials are a manual field kit; no dispatcher or customer runtime exists in this change. The field kit itself has no consented participant data. Its private-ledger directory is Git-ignored.
