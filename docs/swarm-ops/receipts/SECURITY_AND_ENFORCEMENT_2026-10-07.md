# Security and enforcement receipt — 2026-10-07

## Live revalidation addendum — 2026-10-07T12:59:47Z

Cloud master is `29192965eb3b77e91d9ed60a0cad58097d61fda5`. GitHub currently reports **32 open high-severity CodeQL alerts**, **0 critical CodeQL alerts**, **7 open Dependabot alerts** (#96 and #133–#138), and **0 open secret-scanning alerts**. This is a provider count, not proof that historical credentials were never exposed or that a deployment is safe.

- Protection still requires 14 strict contexts, enforces administrators, resolves conversations and blocks force-push/deletion. Required approvals are `0`; `Require current Four Ws receipts` is not required. Actions permissions read back as default workflow permissions `read`, `can_approve_pull_request_reviews=false`, `allowed_actions=all`, and `sha_pinning_required=false`.
- PR #285 is open at `08581a1b3e1206cdc3faf70e535d0ac2bee9a2d4`; its CodeQL and CI checks pass, but Vercel’s two status contexts report build-rate-limit failures. PR #286 is open at `860da3fb60614ea42b11d125106ab1d3f62d6616`; its targeted Rust/CodeQL/CI checks pass and its Four Ws run is cancelled because the branch is behind. PR #287 is open at `f60464150e5375a0a5920f5235e001a7214fbab7`; CodeQL and CI checks pass. PR #288 is open at `ba8488e4fd6a2496aa42579f80c638abe6b34f38` with hosted checks still running at this observation. None has an owner review or merge receipt.
- `.github/workflows/deploy-web.yml` is path-filtered to `public/**` and `kopano-labs-web/**` on `master` and calls the IONOS FTP production jobs. PR #285 therefore needs an explicit deployment boundary review; no merge, production attempt, served-SHA validation or production verification occurred here.
- Issue #207 remains owner-closed. The trusted Four Ws successor in PR #288 is not a hosted App, provider acceptance, branch-protection requirement or runtime enforcement. The source risk for #16 remains unremediated; #43 and #46 remain in review through #286 and #287. No breach was confirmed, no incident was closed, no credential was rotated and no alert was dismissed.

These results are a newer observation than the historical sections below; they do not rewrite those records.

**Status:** Cloud-source audit and provider revalidation complete for this checkpoint. Remediations remain in review; no incident closure or production claim.

**WHO / authority:** Codex Forge coordinating as a stateless CA task renter. No RTC identity seat is claimed. Robyn retains repository ownership and review authority. `I_AM_STATELESS_RENTER_NOT_LANDLORD`.

**WHAT:** Rechecked GitHub alert state, refreshed dependency PRs, current master protection, and the source paths behind CodeQL #16 and #43. Continued the bounded XSS remediation in PR #285. This receipt records security findings and control gaps; it does not attest to a hosted installation or establish that exploitation occurred.

**WHERE:** Cloud GSMB `RobynAwesome/Introduction-to-MCP`, master `cf6cdaa5769465f7c2f7b4c5797e60b7122e7ac9`, provider observations around `2026-10-06T22:58Z` (`2026-10-07` SAST). Local OneDrive and Heavy Human-in-the-Loop Google Drive were not inspected or modified for this receipt.

## Live provider state

GitHub reported **32 open high-severity CodeQL alerts**, **0 critical CodeQL alerts**, **7 open Dependabot alerts**, and **0 open secret-scanning alerts**. The open dependency alerts are #96 NLTK (high), #133 rustls (medium), #134/#135 source-map-js (high), #136 proxy-addr (critical), #137 fsspec (high), and #138 multidict (medium). NLTK #96 has no first-patched version in the current provider record; keep it open.

Dependabot PRs #277–#282 were refreshed to base `cf6cdaa5769465f7c2f7b4c5797e60b7122e7ac9`. The 14 required contexts pass on all six. PRs #277–#280 and #282 show `CLEAN` merge state. PR #281 reports an additional Four Ws job failure and `UNSTABLE` merge state. All six remain open without an owner review/merge, so provider alerts remain open. No dependency alert was dismissed.

Master protection currently requires 14 strict status contexts, enforces administrators, requires conversation resolution, and blocks force-pushes and branch deletion. The configured approving-review count is **0**. `Require current Four Ws receipts` is not in the required context list. The #207 issue remains closed by Robyn; its tracker disposition is not a receipt that the check is trusted or enforced. No branch-protection field was changed.

## Source findings and remediation boundaries

### CodeQL #16 — password storage and first-admin bootstrap

At Cloud master, `kopano-core/kopano/database.py` stores passwords using a salted SHA-256 construction rather than a password-specific slow hash. Registration, authentication, and operator updates use this path. The fresh-database admin bootstrap in `kopano-core/kopano/runtime.py` falls back to a publicly documented password when `KOPANO_ADMIN_PASSWORD` is unset; the value is also prefilled in the Studio UI and documented in the demo instructions. The API lifespan invokes the bootstrap. The direct API entrypoint binds to `0.0.0.0:8000`.

This establishes a source-level risk, not a reachable deployment, successful login, credential theft, or breach. No installation, database, provider runtime, access log, or session state was inspected. Setting `KOPANO_ADMIN_PASSWORD` does not rotate an existing administrator because the bootstrap returns once any admin exists. Treat any reachable instance initialized with the public default as exposed until an owner-led password reset and session review establish otherwise. A fix must include password-hash migration and an owner-reviewed first-run/reset flow; that work is not yet implemented.

### CodeQL #43 — configurable OAuth token URL

The Rust configuration accepts an arbitrary token URL, and the public OAuth config structure can be constructed directly. Code exchange and refresh requests send authorization or refresh credentials to that URL without enforcing HTTPS at every sink. Redirect downgrade behavior also needs an explicit control. This source path does not prove any OAuth exchange or token exposure occurred. A separate HTTPS-only implementation is in progress; no alert is dismissed.

### XSS findings #8–#14 and #46

PR [#285](https://github.com/RobynAwesome/Introduction-to-MCP/pull/285), based on current master, replaces affected user-controlled HTML sinks with text/node construction and moves the observability session value into an escaped DOM data attribute. The first hosted CodeQL run found a high-severity unsafe closing-tag matcher in the new regression test, not a reason to dismiss any source alert. The test matcher was corrected at head `70ca7c9f4abf541cde2ec662db69d8ada41cdd09`; fresh provider checks were still pending at this receipt. Focused local evidence on the prior head: pytest 2/2, Node regressions 7/7, targeted Ruff and compile checks passed. Do not claim these CodeQL alerts cleared until the corrected head receives fresh passing provider results.

### Trusted Four Ws check

The current `pull_request` workflow fetches the PR merge revision and executes the validator from that revision while a read-only token is present. A PR can therefore change the code evaluating its own submission. The check is also absent from branch protection, which currently has 0 required approvals. This identifies an enforcement gap; no confirmed token leak or breach was found in the bounded review. A trusted-base, exact-head check implementation is being prepared. Until its hosted behavior is reviewed, required by the owner through provider settings, and verified on accepted and rejected paths, Four Ws remains a structural check rather than enforced policy. Its nonempty fields do not prove the truth of a claim, RTC authority, or owner approval.

## Current review PRs

- [#283](https://github.com/RobynAwesome/Introduction-to-MCP/pull/283) — docs receipt, head `45d450afb866b1194a218960934ac97b45fea72c`; required contexts and Four Ws job pass; open, no review decision.
- [#284](https://github.com/RobynAwesome/Introduction-to-MCP/pull/284) — bounded Studio UI slice, head `b11c261985bc480d603d80865b90adb1acffa4ce`; 14 required contexts pass; open, no review decision, provider reports `UNSTABLE`. Vercel checks are preview deployments only.
- [#285](https://github.com/RobynAwesome/Introduction-to-MCP/pull/285) — XSS remediation, head `70ca7c9f4abf541cde2ec662db69d8ada41cdd09`; hosted checks rerunning after the test fix.
- OAuth #43 and trusted-base #207 successors are still being prepared in separate clean Cloud worktrees. No PR number is assigned until each PR actually exists.

Robyn's review policy is to receive PRs for approval. No PR above was merged by this renter. No production deployment, secret rotation, incident closure, alert dismissal, or local/Drive write occurred.

## Next admissible action

1. Review the corrected exact head and hosted checks of PR #285; preserve any remaining alert until the provider confirms its state.
2. Finish and review the HTTPS-only OAuth token endpoint PR for #43.
3. Finish and review a base-trusted Four Ws check candidate; do not edit branch protection before owner review and a concrete provider-setting plan.
4. Prepare owner review for the password-hash and default-admin first-run/reset behavior under #16.
5. Reconcile alerts after owner-approved merges. If an installation is found to have used the public default and was network reachable, investigate/reset credentials and sessions through its actual owner/provider surface.

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
