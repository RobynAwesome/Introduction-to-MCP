# Node2Shell estate triage and AG takeover — 2026-11-02

**Finding:** multiple source-level Brotli input candidates and four repositories with Node 20 CI declarations were found. No exact running production/local Node patch was measured. Production vulnerability, reachability and compromise therefore remain UNKNOWN; this is not estate-wide security clearance.

**WHO:** Fox Forge / Codex, owner-directed stateless CA task renter; two bounded read-only peer source reviews supported integration. No RTC seat, Cassey approval or independent security signoff is claimed. `I_AM_STATELESS_RENTER_NOT_LANDLORD`.
**WHAT:** repaired root NOW salience as a reviewable documentation change; inspected Node2Shell applicability, public source snapshots and authenticated deployment metadata.
**WHERE:** core source baseline `RobynAwesome/Introduction-to-MCP@5a5ffd1836c2abe83baf3a154ad1bf70f6047ef5`; app commits are listed below. Local OneDrive/Windows is unavailable. Private source detail was retained outside this public report.
**WHY:** a returning builder needs the current goal, actual completed work, evidence gaps and one next action. Preserved history must not repeatedly reactivate already-merged PR work.

## 1. What changed in continuity

Current GitHub receipts confirm [#327 merged](https://github.com/RobynAwesome/Introduction-to-MCP/pull/327), [#326 superseded and closed unmerged](https://github.com/RobynAwesome/Introduction-to-MCP/pull/326), and [#335 merged](https://github.com/RobynAwesome/Introduction-to-MCP/pull/335) as `5a5ffd1836c2abe83baf3a154ad1bf70f6047ef5` on November 2 at 18:10:23 UTC.

The old NOW already contained a correct #326/#327 reconciliation inside its October 28 block. The defect was selection/placement: October 29/28 review-candidate instructions and the October 26 merge order still looked current. The new first block foregrounds current receipts, the security objective, AG's next evidence collection and explicit HOLD boundaries. Every pre-existing NOW byte remains below a historical-snapshot boundary. No new salience protocol or identity/authority registry was created.

The owner’s present instruction selects security investigation and Playground experimentation as active work. Durable governance remains in AGENTS/Legacy/the existing continuity contract; NOW supplies temporal selection. The previous synthesis and the owner’s salience proposal are contextual evidence, not ratification of a new runtime capability.

## 2. Threat identity and patch boundary

The [official Node security release](https://nodejs.org/en/blog/vulnerability/october-2026-security-releases) identifies **CVE-2026-111497**, an out-of-bounds write in Node’s bundled Brotli decoder. Untrusted data must reach decompression; outcomes can include crash, memory disclosure or code execution. Minimum fixed Node releases are **22.23.4, 24.22.1 and 26.12.1**. Use a maintained patched release in the selected line; move unsupported lines, including Node 20, to a supported line.

[Imperva’s original research](https://www.imperva.com/blog/node2shell-from-brotli-data-to-remote-code-execution/) demonstrates the distinction between incoming parser paths and outgoing fetched responses. Express 5/body-parser 2 can inflate incoming Brotli bodies; server-side HTTP clients may decode responses. An installed dependency is a candidate path, not evidence that its server/parser is running. Browser-rendered JavaScript and Chromium navigation do not by themselves establish a Node decoder path.

This concerns the runtime binary. Updating `@types/node`, npm packages or lockfiles alone does not replace the bundled decoder. A Brotli library version string alone is also insufficient to resolve a vendor-backported runtime; capture exact runtime/vendor evidence.

## 3. Coverage and its limits

- Enumerated **169 unique accessible repository IDs** across two installation pages (100 + 69). Returned owner metadata identifies 168 under RobynAwesome/Kopano-Labs plus one group repository. Owner-qualified search strings returned identical global pages; ownership was not inferred from those filters.
- Source-inspected **12 app repositories plus the core Introduction-to-MCP repo**. Eleven app repositories are public; one private Node application was inspected but its name, routes, code and commit are omitted from this public report.
- Inspected **33 Vercel project configurations**. All returned `nodeVersion=24.x`. This is a family setting, not a measured patch version, application runtime, active service count or vulnerability count.
- Resolved seven production aliases to deployment IDs, source SHAs and creation times. Inspected four build-log samples; no exact running Node binary version was obtained.
- Local Node installations, IDE/agent embedded runtimes, Windows services, WSL, containers, external hosts and Python/Brotli libraries are not covered by the Cloud source scan. No exploit payload, external scan, credential access or production mutation was performed.

## 4. Source evidence — public application scope

| Public repo / exact source | Source finding | Remaining proof / patch target |
| --- | --- | --- |
| [Kopano-Labs/Bookit-5s-Arena @ 85e6e2b4](https://github.com/Kopano-Labs/Bookit-5s-Arena/tree/85e6e2b4aa2035552c396d8e7d632a706e524f2d) | package.json: next ^15.5.18, start next start; lock next15.5.19 undici7.29.0; lib/media/news.js:80 fetch feed URL; :107 fetch article URL parsed from feed; :119 consumes response.text(); vercel.json framework nextjs, app/api functions | No source Node patch floor; actual production binary/served SHA/provider rollout unknown. |
| [RobynAwesome/5s-Arena-Blog @ c5b145d3](https://github.com/RobynAwesome/5s-Arena-Blog/tree/c5b145d344f4a88d8a7009cf9d1214186eee48bd) | package-lock.json express5.2.1 body-parser2.2.2; server/index.js:19 app.use(express.json()) before routes/DB/auth; :60 export app; server/routes/organism.js:30 fetch Fives upstream | Whether Express server is hosted/reachable, runtime patch and deployment mapping unknown; Vercel source rewrites alone do not prove backend mounted. |
| [RobynAwesome/KasiLink @ c090e74f](https://github.com/RobynAwesome/KasiLink/tree/c090e74fd9a19735b6a7034b2e55966f05aa97ca) | lock next16.3.4; express4.22.2/body-parser1.20.5 are transitive and do not by themselves prove Express5 incoming Brotli path; app/api/orch/[...path]/route.ts:24 fetch upstream; :35/:39 consume response; route auth gate retained; app/api/load-shedding/schedule/route.ts:93,:119,:147 fetch remote data | Actual provider Node patch, deployed SHA, upstream response encoding unknown. |
| [RobynAwesome/Project-Jennifer @ cc74b56b](https://github.com/RobynAwesome/Project-Jennifer/tree/cc74b56b879881defbbb885167b1b75a4a26f6db) | apps/api/package.json:11 start node dist/server.js; :28 express^4.19.2; pnpm-lock express4.22.2 body-parser1.20.6; apps/api/src/server.ts:71 express.json(); root engines node>=20; CI/deploy/proof NODE_VERSION20 | No Express5/body-parser2 path established; need source fetch inventory and actual API/provider/runtime patch. |
| [RobynAwesome/Portfolio @ a8c98033](https://github.com/RobynAwesome/Portfolio/tree/a8c980337176a69e2c96dda014fe89430130822c) | package.json vite build; api/contact.js:40 fetch Resend; api/cv-download.js:19 fetch Mailchimp; CI .github/workflows/ci.yml:20 Node20 | Static homepage cannot clear API functions; function runtime patch and production deployment unknown. |
| [RobynAwesome/kopano-sovereign-hub @ f109bf87](https://github.com/RobynAwesome/kopano-sovereign-hub/tree/f109bf87b94a788ed97468bc74d8dc91bef3da7a) | api/lefa/market-status.ts:100,:101 fetch fixed Alpaca endpoints; api/lefa/alpaca-status.ts:125 fetch account endpoint; API exports fetch object; no runtime edge marker in inspected files; CI major22 | Confirm actual handler hosting/runtime (Node vs other); cannot assume Vite means static-only or Node deployment proven. |
| [RobynAwesome/amaphu-app @ e1596383](https://github.com/RobynAwesome/amaphu-app/tree/e15963833fd3722deebd30829528521309934d7b) | next16.3.2; start next start; engines node>=20.9.0; CI major24 | No production Node or reachable untrusted Brotli path established. |
| [RobynAwesome/starfall-salvage @ 763380b0](https://github.com/RobynAwesome/starfall-salvage/tree/763380b01819a4b38c6fe048a33333fbc7c8d208) | vercel.json:3 no dependency install; :4 no build; outputDirectory .; root engines node>=20.0.0; monorepo/local tooling and Python backend | No live Node service established by inspected deployment config; local/dev/build runtimes still inventory. |
| [RobynAwesome/Kopano-Labs-Website @ d6e5cc3f](https://github.com/RobynAwesome/Kopano-Labs-Website/tree/d6e5cc3fba6cd5d76e3a21e26bef9ae9ae6cdb04) | vercel.json framework vite/output dist; scripts build sync evidence/projection; CI major22 | Build-time outbound sync may run Node; deployed static asset serving is not an app Node decoder path; production provider mapping unverified. |
| [RobynAwesome/lefa-ai @ 7c4576fb](https://github.com/RobynAwesome/lefa-ai/tree/7c4576fb653663d8a557f4960814db10bfc62b0f) | vercel.json output dist and /api rewrite /api/index.py; CI major22; Vite Node dev/build | No production Node API source path established here; Python Brotli dependency applicability separate. |
| [RobynAwesome/KasiMargin @ 85d3cc93](https://github.com/RobynAwesome/KasiMargin/tree/85d3cc9398701c451734eafe62aa1d15770fc6d1) | package.json TypeScript only devDependency; build tsc; test node --test; CI major24; Python tests | Node tests/build version not exact; no internet-facing Node decoder path found in this bounded source inspection. |

**Confirmed Node 20 CI configuration:** Bookit `court-assets.yml:25`; KasiLink `ci.yml:22` and `kpgs-branch-proof.yml:33`; Project Jennifer CI/deploy/multiple proof workflows; Portfolio `ci.yml:20`. These are source defects/toolchain candidates. They do not establish the Node version of production functions. Floating 22/24 selectors also do not attest an exact runtime patch.

**Bookit identity:** canonical `Kopano-Labs/Bookit-5s-Arena` is nonfork repository ID 1178783579. `RobynAwesome/Bookit-5s-Arena` is a separate, older fork (ID 1319737503, parent Kopano-Labs). Evidence from the fork cannot clear canonical production. The inspected canonical default head and production SHA are `85e6e2b4aa2035552c396d8e7d632a706e524f2d`; a newer native-recovery preview is a separate branch/deployment, not proof it serves production.

### Core Introduction-to-MCP

At `5a5ffd1`, root lock resolves `braintrust@3.37.2 → express@5.2.1 → body-parser@2.3.0`; actual Braintrust server/parser use is unverified. The Browser MCP is a local Node stdio process with loopback CDP, not an identified public HTTP parser; its `engines.node >=22` permits vulnerable patches. The root dashboard and separate Studio are Vite frontends. Root Vercel config builds `apps/kc-dashboard/dist`; Browser MCP config emits a static LOCAL_ONLY page. Neither config establishes a hosted Node backend. SDK/local/build decoder use still needs runtime inventory.

The current dependency firewall inspects npm package floors; it does not verify Node/Brotli runtime patches. The source audit found no app-owned exact fixed Node patch declaration in this bounded scope. Imported SDK use and global `fetch` can exist without a standalone Brotli package in a lockfile.

## 5. Production alias observations

| Production mapping | Created UTC | Source SHA | Evidence boundary |
| --- | --- | --- | --- |
| bookit-production | 2026-10-20T08:24:33.919Z | `85e6e2b4aa20` | Provider mapping only; exact Node patch not returned. |
| kasilink-production | 2026-09-14T11:08:00.815Z | `13be1ba8df4a` | Provider mapping only; exact Node patch not returned. |
| kasilink-rsa-production | 2026-09-14T11:08:00.791Z | `13be1ba8df4a` | Provider mapping only; exact Node patch not returned. |
| kc-production | 2026-11-02T18:10:27.886Z | `5a5ffd1836c2` | Provider mapping only; exact Node patch not returned. |
| browser-mcp-production | 2026-11-02T18:10:27.898Z | `5a5ffd1836c2` | Provider mapping only; exact Node patch not returned. |
| starfall-production | 2026-10-30T17:55:25.705Z | `763380b01819` | Provider mapping only; exact Node patch not returned. |
| blog-production | 2026-09-09T01:32:02.227Z | `c5b145d344f4` | Provider mapping only; exact Node patch not returned. |

These are authenticated provider mappings, not HTTP journey tests or process-version measurements. `READY` does not establish that the advertised application works, that a runtime has been patched, or that no older deployment remains reachable. The newest preview was not substituted for the production alias during this audit.

The [Vercel bulletin](https://vercel.com/kb/bulletin/node-js-security-advisory) states that all new deployments use patched Node from **October 28, 11:00 PT (18:00 UTC)**. It describes automatic inbound WAF protection and limits: WAF does not cover externally fetched responses. Redeployment is its required path to managed-runtime protections; external backends need their own runtime replacement. Bookit and both KasiLink production builds predate that cutoff. Current family settings and recent previews do not clear those production builds. Core/Browser MCP and Starfall mappings postdate it, with static source configurations; record this provider assurance separately from an actual process measurement.

## 6. Remediation sequence — one accountable next action

**AG first measures runtime + reachability on priority public services.** Forge coordinates the evidence packet; the human owner controls production release. Record the actual AG embodiment and builder scope before execution. Do not wait for Robyn to reconstruct the prior chat when local access returns.

1. **Map binaries to services.** For each priority surface, record source/deployed SHA, provider/project/alias/environment, Node full patch, architecture, executable/image identity, time and collector. Distinguish build runner from request-serving process, local tool from deployed function, and provider assertion from measurement. No public diagnostic endpoint or environment dump is needed. Keep sensitive paths/private inventory private.
2. **Map two decoder inputs.** Determine whether inbound middleware inflates `Content-Encoding: br` and whether server-side fetches/SDKs/image optimizers can decode untrusted upstream responses. Preserve existing authentication. A fixed upstream hostname reduces some attacker control; it does not prove the remote response is permanently trustworthy. Merely accepting a JSON request is not proof of Brotli decompression.
3. **Replace affected runtime.** Choose a maintained fixed runtime for each owning app; rebuild images/artifacts and restart/redeploy the same reviewed source. For Vercel managed projects already selecting 24.x, prepare a reviewed rebuild/redeployment, not an unrelated framework rewrite. Update external hosts and all bundled/embedded binaries separately. Do not promote the native Bookit preview or change the KasiLink domain split under cover of a runtime patch.
4. **Repair declarations.** Replace Node 20 workflow declarations through app-owned reviewed changes and emit exact version receipts. Add supported patch constraints/toolchain pins where appropriate; choose a compatible maintained runtime, not an unbounded `>=20`/`>=22`. Keep Node type definitions separate from the executable binary.
5. **Verify behavior and evidence.** Capture new process/image identity plus served source SHA; exercise relevant booking, API, contact or tool behavior and harmless ordinary Brotli handling. Preserve failed tests and rollback artifacts. A change to `Accept-Encoding` alone is not a complete fix; any interim compressed-body restriction must cover the actual path and be compatibility-tested.

The smallest read-only local collection example is `node -p 'JSON.stringify({node:process.version,arch:process.arch,platform:process.platform,brotli:process.versions.brotli})'`. It identifies only the binary executing that command. It does not prove another service, IDE, container or function uses that binary. Collect from each actual owning process/image through its authorized operator surface; do not infer from PATH.

## 7. Playground experiment, then procurement replay

Extend the existing fixture admission/test surfaces after AG confirms ownership and independently verifies any required execution isolation. Do not relabel the current assertion-only gate as runtime enforcement.

Proposed harmless runtime-evidence cases: vulnerable supported release; fixed release; unsupported Node 20; missing exact version; patched family selector without process proof; source SHA/deployment mismatch; static frontend with separate Node API; and conflicting provider/runtime receipts. Expected classifications must preserve HOLD for missing evidence and separate confirmed vulnerable binaries from decoder reachability. These are **SPECIFIED / NOT_RUN** here; an arbitrary new field ignored by the current evaluator must never count as a validated Node check.

Then continue existing [#342](https://github.com/RobynAwesome/Introduction-to-MCP/issues/342): fictional tender/bids, separate advisory/human decision, test-bound approval verification, seven positive/negative scenario groups, tamper/completeness detection and fresh-ledger restart/idempotency. Retain original recommendation, override reason/policy basis, denied transitions and redacted appeal trail. No new playground/protocol, live exploit, genuine reviewer authentication or production graduation is claimed.

**Exit condition:** each priority deployment has a measured decision and remediation/behavior receipt, or an explicit unknown, accountable owner and decisive next probe. Each experiment has expected/observed results at exact source/fixture revisions. Independent Cassey/security review and founder signoff remain separate.

## 8. Validation of this change

This patch changes documentation/evidence only. Validation checks exact preservation of old NOW/history, valid machine-readable data, public/private redaction, linked file presence and the four-file scope. Existing renter entry returned ACKNOWLEDGED for this actor; bracket lint self-test passed six cases. No application, procurement, exploit or production-runtime tests were run; no fresh 42-test pass is invented. The historical fixture job remains [40243913921 / 121321371361](https://github.com/RobynAwesome/Introduction-to-MCP/actions/runs/40243913921/job/121321371361).

The [machine-readable companion](NODE2SHELL_ESTATE_INVENTORY_2026-11-02.json) preserves source revisions, provider observations, explicit null runtime versions, exclusions and this review's session-closeout fields. It is an investigation artifact on an existing receipt surface, not a newly promoted protocol.
