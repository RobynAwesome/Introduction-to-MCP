# Production journey receipt — 2026-10-28

Status: **RUNTIME_HOLD / REVIEW_CANDIDATE**. Neither deployment earns production-function, end-to-end receipt, or security signoff.

WHO: Codex Forge, stateless renter, no RTC seat claimed. `I_AM_STATELESS_RENTER_NOT_LANDLORD`.
WHAT: Owner-directed inspection of two production promotions and the 13 open issues; no application implementation, merge, provider setting change, or issue closure.
WHERE: Cloud `RobynAwesome/Introduction-to-MCP@4dfe0bc7008ce97f9e033a2851384b79257b47fb`; production observations on 2026-10-28 between 12:15 and 12:18 UTC (14:15–14:18 SAST).
WHY: Distinguish deployment metadata, observed runtime behavior, source contracts and missing proof.
KPEFS: V2_ANIMAL primary (uptime/reliability); V4_DIASPORA secondary (sovereignty and continuity). Bracket: bounded observation and documentation. PKA: missing proof remains HOLD. Teacher/RTC review is not supplied by this receipt.

## Promotion metadata

The latest reviewed Vercel notice arrived at 11:02:42 UTC / 13:02:42 SAST on October 28. The connected deployment API resolved both current production aliases to the same repository SHA above, branch `master`.

| Project | Production deployment | Serving alias |
|---|---|---|
| kopano-context-studio | `dpl_7ynLnxMXx3ahQThkUaFXFGA6afcs` | https://kopano-context-studio.vercel.app/ |
| kpgs-browser-mcp | `dpl_wPkytmAFVuzdKz4mEdVEwQWjaDFE` | https://kpgs-browser-mcp.vercel.app/ |

Deployment pages: [Studio](https://vercel.com/robynawesomes-projects/kopano-context-studio/dpl_7ynLnxMXx3ahQThkUaFXFGA6afcs), [Browser MCP](https://vercel.com/robynawesomes-projects/kpgs-browser-mcp/dpl_wPkytmAFVuzdKz4mEdVEwQWjaDFE).

Both reported `READY`, `target=production`, `aliasError=null`. These are provider metadata. The build region is `iad1`; the dashboard's displayed ZA-CPT receipt does not independently establish data residency.

## Studio: render → Ask KC → backend response → receipt

Confirmed:
- Connected HTTP fetch of root returned 200 HTML, JavaScript asset `/assets/index-C8V8mDXJ.js`, request ID `syd1:iad1::m7fpg-1793189706262-f630aac09ca5`, Date `2026-10-28 12:15:06 GMT`.
- A browser loaded and rendered the actual interface at the production alias. This is stronger than the HTML fetch alone.
- Submitted synthetic text: `Production verification 2026-10-28: reply with RECEIPT-PROBE-1028.`
- UI returned: `I'm with you, my boy! Let's get to work on: "Production verification 2026-10-28: reply with RECEIPT-PROBE-1028.".`
- Direct POST to `https://kopano-context-studio.vercel.app/api/kc/chat`, JSON `{"message":"Production verification 2026-10-28: reply with RECEIPT-PROBE-1028.","rtc_identity":"GUEST_SEEKER"}`, returned **404**, `x-vercel-error: NOT_FOUND`, Date `2026-10-28 12:18:16 GMT`, request ID `cle1::9rk2g-1793189896670-abf3a99cf293`.
- Separate connected GET to that API path returned 404 at 12:16:17 UTC, ID `syd1:iad1::xtt8c-1793189777595-bf78631b7e34`.

Source corroboration:
- Root `vercel.json` builds `apps/kc-dashboard` and outputs `apps/kc-dashboard/dist`. This alias is not evidence that `kopano-core/studio` is served.
- `apps/kc-dashboard/src/components/KCMyBoyHero.tsx` posts to the relative `/api/kc/chat` path. Non-OK responses produce the exact local fallback observed above.
- The same component initializes `AST-8F2B10A4`, `VERIFIED_ON_LEDGER`, `ZA-CPT (South Africa North)` and hash `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` in client state.
- Browser expansion of that stamp displayed `VERIFIED_ON_LEDGER` and the claim `Sovereign companion active and listening at front door`. No ledger write/read/verification was observed. That hash is the SHA-256 digest of an empty byte string.

Verdict: **UI_RENDER_CONFIRMED; CHAT_JOURNEY_FAIL; LEDGER_PROOF_NOT_ESTABLISHED**.
First broken boundary: UI → usable backend. Stop before claiming inference or durable receipt success.
Next bounded implementation: reconcile which application this production alias should serve under #110; wire the admitted backend, expose unavailable/error states honestly, and remove unsupported ledger verification defaults. Re-run one chat → real response → persisted/retrieved receipt journey. Do not silently switch the alias or publicize backend endpoints from this audit.

## Browser MCP: HTTP entry → MCP discovery → browser observation

Confirmed:
- Connected HTTP fetch of root returned **500 Internal Server Error**, `x-vercel-error: FUNCTION_INVOCATION_FAILED`, Date `2026-10-28 12:15:10 GMT`.
- Body: `A server error has occurred\n\nFUNCTION_INVOCATION_FAILED\n\nsyd1:iad1::gvb98-1793189710060-86085a6ff924`.
- Provider build log says `Build complete — Using src/server.ts as the root entrypoint.` and `Deployment completed`.
- Exact deployed `tools/kpgs-browser-mcp/src/server.ts` ends with `await serveStdio(() => buildServer());`.
- Deployed README describes a **local** stdio MCP process, loopback-only Chromium CDP, local on-disk ledger, and separate human TTY approval. It explicitly retains `HARDENED_POC_CANDIDATE`, `METAL = REQUIRED`, `PRODUCTION_AUTHORITY = NOT_GRANTED`.

Inference: the configured hosted entrypoint and the documented local transport/authority contract are mismatched. The HTTP 500 is observed; its exception/root cause is not proven by this inference.
A 30-minute deployment-scoped runtime-log query returned no records; a one-hour grouped runtime-error query also returned none. These empty queries do not negate the directly observed 500 or prove health.

Verdict: **HOSTED_ENTRY_FAIL; MCP_DISCOVERY_AND_BROWSER_JOURNEY_UNVERIFIED**.
Next bounded work: reproduce the startup exception and determine whether this project should have a hosted service at all. Preserve loopback, human approval and local-ledger boundaries. The smallest intended local proof is real MCP discovery → `browser_status` → `list_pages` → `read_page`; graduation still requires the README's one-use approval, drift denial, uncertainty quarantine, scrubbing and receipt-verification metal tests. This cloud session does not provide the owner's dedicated Windows Chromium/TTY environment.

## Dependency/CI evidence and limits

Fresh GitHub pull records confirm merged Dependabot PRs #302, #300, #298, #297, #295, #292, #293, #291, #290 and #289, among the reviewed recent records. #302's merge is the shared deployed SHA. Source-level dependency progress is real.

The exact deployed SHA has 16 returned check runs: 15 success, 1 skipped. The skipped check is `Deploy authorized production change`; its skipped state does not close Azure #211. CodeQL analysis success is a workflow result, not a current alert inventory or security signoff. No new full security audit or authorized-browser execution test was performed.

Root NOW's October 26 handoff is stale relative to current PR records: #326 is closed without merge; #327 is merged (reviewed PR head `70f0516...`). Preserve the dated text as history; do not repeat its review order as current live PR state.

## The exact 13 open issues: next proof-bearing slices

This is an observation/closure-routing queue, not a claim that all implementation is absent. Issue bodies and comments were read. Dated comments are discovery leads; downstream source/runtime must be revalidated before closure.

| Issue | Next bounded slice / evidence still required |
|---|---|
| [#110](https://github.com/RobynAwesome/Introduction-to-MCP/issues/110) KC GUI | **Started here:** distinguish deployed dashboard from Studio, receipt chat failure and unsupported stamp. Stale GUI compare pointer is already retired. Build/test the intended Studio and exercise Context/Swarm/MAO/KPEFS/Proof/CI/SIM before closing. |
| [#211](https://github.com/RobynAwesome/Introduction-to-MCP/issues/211) Azure deploy | Revalidate OIDC configuration and an authorized deployment with Azure login and `azd up` both passing; a skipped job cannot satisfy it. No secret values were read. |
| [#122](https://github.com/RobynAwesome/Introduction-to-MCP/issues/122) 22-repo audit | This receipt refreshes only two Vercel aliases in one repo. Remaining 22-repo identity/CI/local census and HOLD reconciliation require their own bounded refresh; Local is unavailable here. |
| [#102](https://github.com/RobynAwesome/Introduction-to-MCP/issues/102) estate operations | Re-probe KasiLink host/API convergence and Starfall rollback/admission gates. September failure receipts are dated, not a fresh outage claim. Provider cutover remains separately governed. |
| [#158](https://github.com/RobynAwesome/Introduction-to-MCP/issues/158) FivesArena | Re-read existing Bookit PR #33 and its current landing/runtime evidence. Do not open a duplicate relaunch PR; owner inspection before merge/deploy remains explicit. |
| [#103](https://github.com/RobynAwesome/Introduction-to-MCP/issues/103) Sepedi inference | Reconcile current Mzansi data-engine implementation against PR1/PR2 tracking, then prove consent/provenance persistence before language/speech/native-speaker evaluation. September “PR2 not started” is not promoted as current source truth. |
| [#107](https://github.com/RobynAwesome/Introduction-to-MCP/issues/107) KMEC/PKA/ledger | Revalidate owning implementation lanes KMEC #15, PKA #18, Jennifer #78; prove linked observation → admission → offline/reconnect → authoritative receipt with duplicate replay prevented. |
| [#183](https://github.com/RobynAwesome/Introduction-to-MCP/issues/183) SAP/RUNE runtime | Start with the admitted AuthorityScope/lifetime slice; prove descendant cancellation, authority-chain verification and persisted restart before the broader runtime/evolution claims. |
| [#115](https://github.com/RobynAwesome/Introduction-to-MCP/issues/115) Forge Orchard | Obtain recorded independent review and bounded admission contract; dry-run one real Classroom artifact to ADMIT/HOLD/FOC with provenance. Preserve Interns #12 routing. |
| [#116](https://github.com/RobynAwesome/Introduction-to-MCP/issues/116) Temporal Data | RTC discussion and canonical-owner audit precede an admitted temporal contract/POC; current status is discussion, not permission to redesign NOW semantics. |
| [#163](https://github.com/RobynAwesome/Introduction-to-MCP/issues/163) provenance incident | Independently reconcile incident-artifact landing and required disposition. Forge cannot turn its own audit into incident clearance. |
| [#167](https://github.com/RobynAwesome/Introduction-to-MCP/issues/167) Jennifer authority incident | Independent RTC inquest/disposition and re-entry evidence; no self-adjudication or weakening fail-closed persistence. Preserve later owner role corrections rather than reviving old seat-vacancy language. |
| [#231](https://github.com/RobynAwesome/Introduction-to-MCP/issues/231) driver discovery | Human-led opt-in shift-estimate test, minimized field ledger, seven-day second-contact denominator and separate review; no driver utility, savings, dispatcher or buyer claim from code/deployment status. |

No issue was closed, and no production setting was changed. The first executable repair lane is #110's application/backend and truthful receipt boundary; it must precede any new success language.

## Validation / handoff

Renter ingress: `python scripts/kc_kpgs_governance.py entry --renter-id codex_production_receipt_review_2026_10_28 --renter-class stateless_renter --assert --hood-ack I_AM_STATELESS_RENTER_NOT_LANDLORD` returned exit 0, `ACKNOWLEDGED`, `ack_verified=true` at 12:19:37 UTC.
Local checkout is isolated and pinned to the shared deployed SHA. Only documentation/observation receipts are proposed. No application build or local unit-test run is claimed by this slice. Historical issue comments, application UI stamps and empty provider log queries never replace the actual request receipts above.


Documentation checks: `python scripts/kc_log_append.py validate`, `python scripts/kc_log_append.py proof-check`, and `git diff --check` returned exit 0. These validate receipt structure and patch hygiene; they do not turn the observed 404/500 into a pass.
