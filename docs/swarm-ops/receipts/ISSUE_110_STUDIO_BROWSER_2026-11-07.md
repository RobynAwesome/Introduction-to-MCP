# Issue #110 Studio browser receipt — 2026-11-07 SAST

**Status** — Source candidate and local browser verification. Hosted chat and durable receipt remain `HOLD`.

**Who** — Codex Forge, owner-directed stateless renter for the Cloud repair. `I_AM_STATELESS_RENTER_NOT_LANDLORD`. The hood gate returned `ACKNOWLEDGED` with `ack_verified=true` at `2026-11-07T15:57:26Z`.

**What and where** — GitHub's open-issue list ordered by least recent update placed [#110](https://github.com/RobynAwesome/Introduction-to-MCP/issues/110) first. The Cloud base was `0a8950277656266273b813ce85f93c4230d4b0ff`. I extended the existing [PR #365](https://github.com/RobynAwesome/Introduction-to-MCP/pull/365), which started this pass at `499c88a3d449abf8cbca181e361b18678c615533`. The browser used a locally built copy of `kopano-core/studio` in Edge Chromium with intercepted loopback and hosted-origin HTTP responses. The `App.tsx` and `DesktopBootOverlay.tsx` blobs exercised were `ca6d36940d82b90eb94cb2ae83e2187d9ad26ae0` and `fea7f8756923fc12e7737a83e7d0323cd5ce0d59`.

**Why** — Shared Studio startup put error response bodies into render state. With bootstrap endpoints returning HTTP 503 JSON, the original candidate threw while reading `.find` and `.length`. After isolating startup reads, the browser exposed a second issue. The local startup overlay intercepted every click while `/health` was unavailable. The candidate validates startup responses before applying them, lets other startup reads succeed independently, and keeps the desktop startup panel dismissible. The hosted Studio shell renders directly.

## Plan reconciliation

| Item | Status and evidence |
| --- | --- |
| Old GUI branch compare pointer | **Stale and retired** in canonical [swarm navigation](../NAVIGATION.md). PR #365 also replaces the CI panel's separate compare URL. |
| Seven-mode Studio and responsive layout | **Implemented in Cloud source.** Context, Swarm, MAO, KPEFS, Proof, CI and Sovereign SIM are present in the existing Console. Previous plan classifications are in the [October 1 audit](STUDIO_VS_PLAN_AUDIT_110_2026-10-01.md) and [October 7 reconciliation](ISSUE_110_STUDIO_RECONCILIATION_2026-10-07.md). The current repair stays in that Studio. |
| Status shape, startup error handling and overlay | **Actionable and repaired in PR #365.** The evidence below covers the candidate. |
| Hosted application choice, chat response and durable receipt | **Blocked.** The checked-in Vercel build selects `apps/kc-dashboard`. The canonical Studio implementation under `kopano-core/studio` is a distinct application. The production target and approved receipt storage need an owner disposition and a runtime witness. |

The Local OneDrive root `NOW.md` and available `Structure` directory names were consulted within the existing privacy hold. The plan classification above uses Cloud artifacts. Google Drive was outside this bounded source and browser check.

## Validation

| Check | Observation |
| --- | --- |
| Studio build and UI checks | TypeScript and Vite build succeeded. Labs smoke, status envelope and responsive/unavailable UI tests passed. ESLint reported zero errors and five existing warnings. Vite reported an existing bundle-size warning. |
| Desktop browser at 1550 px | Context, Swarm, MAO, KPEFS, Proof, CI and Sovereign SIM each opened with bootstrap HTTP 503 fixtures and status HTTP 404. Proof and CI showed unavailable and the header did not display a production count. A successful Microsoft readiness fixture loaded alongside failed startup reads. |
| Browser response and viewport checks | A malformed HTTP 200 status response kept Proof unavailable after retry. Malformed HTTP 200 bootstrap payloads kept the Console usable. The 1190 px proof drawer opened and closed with Escape. Selecting CI from the 420 px navigation drawer closed the drawer. The local startup overlay could be dismissed while `/health` failed. A hosted-origin fixture opened Proof without the overlay. No browser page errors were recorded after the repair. |
| FastAPI locally | The real swarm status API test passed. A synthetic chat POST returned `REFERENCE_GUIDANCE` with `receipt_storage=PROCESS_MEMORY`. A GET found the assertion in the same store. A fresh store returned 404 for that assertion. |
| Hosted readback | `https://kopano-context-studio.vercel.app/` returned HTTP 200 with title `KC · KPGS Observer / Landlord`. GET returned 404 for `/api/kc/swarm-console/status` and `/api/kc/chat`. The October 28 [journey receipt](PRODUCTION_JOURNEYS_2026-10-28.md) separately records a hosted POST 404. This pass used read-only hosted probes. |

KPEFS primary vector V2_ANIMAL for reliability, with V4_DIASPORA for continuity. Bracket and BlackMask scope covers bounded browser fixtures and a local synthetic API turn. Browser requests were intercepted and the mode clicks did not execute operational actions. Evidence review applies to this slice. Production promotion requires its own authority and receipts.

## Remaining acceptance

Review the source candidate and its GitHub checks. For the hosted journey, resolve the serving application and approved backend/receipt store. [#211](https://github.com/RobynAwesome/Introduction-to-MCP/issues/211) still holds the Azure production deployment path. On the admitted target, obtain one real chat response, then retrieve the same receipt across a process restart or replica change. Keep the production acceptance gate open until those observations are recorded.
