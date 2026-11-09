# GSMB CROSS-ESTATE BULLETIN | 2026-11-09 SAST
Status: ACTIVE FINDINGS; NOT release authorization. Maintainer: Chat Forge, read-only investigation. No RTC endorsement claimed.
**FIRST READ FOR ALL AGENTS:** Read this bulletin, then target repo live root NOW.md, default SHA, PR head/checks and deployed SHA. If inconsistent, live evidence wins. Log what changed before starting work. Do not repeat an existing investigation without citing its receipt.

## P0 | Fives Arena / Bookit | NOT NATIVE-BOOKING READY
- GitHub: https://github.com/Kopano-Labs/Bookit-5s-Arena/issues/42 ; PRs #43, #51, #55 open draft at latest audit.
- Source-confirmed defect at production main 85e6e2b4aa2035552c396d8e7d632a706e524f2d: app/api/courts/route.js POST writes `pricePerHour`; models/Court.js requires `price_per_hour`. Court creation contract is broken.
- Production `/book` source embeds Setmore, not native booking. Production Vercel deployment mapped to main 85e6e2b. The 6 Nov readback in PR #55 reports `GET /api/courts` -> 200 `[]` and `X-FivesArena-Data-State: database-empty`.
- Exact PR heads observed: #43 f18444b0ce576ca6d1912ba060e7742759df9361; #51 385c0a6fb85a75f9c24e83f2b3d443fa3f044cfb; #55 fc15714d28bca791994c6eb5ef13af002ae8b966.
- UNRESOLVED: actual authorized Hellenic inventory/database identity, production native guest-to-operator receipt, hosted CI/acceptance.
- NEXT: run #55 `scripts/inspect-bookit-inventory.mjs --discover` read-only using authorized configured DB access, compare intended court inventory, test field-contract repair in isolated DB, then controlled client-endorsed journey. Keep Setmore fallback. Do not seed or switch production without consent.

## P0 | KasiLink | DATABASE REQUEST FAILURES OBSERVED
- Vercel runtime logs 6–7 Nov: `querySrv ENOTFOUND _mongodb._tcp.kasilink.zzuvwlo.mongodb.net` across `kasi-link` and `kasi-link.rsa` projects, routes `/api/gigs`, `/api/incidents`, `/api/water-alerts`, `/api/utility-schedule`.
- Both newest listed production deployment attempts at main c090e74fd9a19735b6a7034b2e55966f05aa97ca show ERROR; prior READY 13be1ba8df4a086394d998815d57c1c885f1ec2b emitted DNS errors.
- CONFIRMED: SRV lookup failure for observed requests. UNKNOWN: bad hostname vs Atlas cluster lifecycle vs DNS provider. Do not call this merely a Clerk issue.
- NEXT: authorized Atlas/secret-metadata verification without exposing credentials, correct proven config only, redeploy and capture route-specific response.

## P1 | Kopano Labs website | CUSTOMER JOURNEY UNVERIFIED
- Production Vercel READY at d6e5cc3fba6cd5d76e3a21e26bef9ae9ae6cdb04; no errors in queried 7-day runtime aggregation. Issues #39 and #41 remain open. READY is not proof of KC route/CTA acceptance.
- NEXT: witnessed served-page KC-to-action journey and acceptance evidence.

## P0 | GSMB CONTINUITY / SECURITY
- Introduction-to-MCP root NOW.md reports #327 merged, #326 superseded, #335 merged 2 Nov. Older orientation calling #335 draft is stale. Current master observed 0a8950277656266273b813ce85f93c4230d4b0ff on 9 Nov; re-read NOW.md for updates before action.
- Node2Shell: source triage exists; deployed runtime binary/Brotli exposure remains UNKNOWN/HOLD.
- RUNE verifier identity/subject binding tests T7b and T8 previously failed; no release endorsement from those tests. Do not substitute key possession for subject authorization.

## MEASURED REPORTING FAILURE
- 41/41 matching parseable issue records from consecutive 26 Oct and 2 Nov orientations retained the same classification; zero recommendation-status transitions. This is reporting stagnation, NOT proof no engineering changed.
- Monthly retrospective: https://docs.google.com/document/d/1Q7Jw041c2Rv10BOBmmSVdKg1fVy0MqvW_Nye9eVb7Kw/edit
- Weekly orientation 9–15 Nov: https://docs.google.com/document/d/1habZKkV9i32jrsgEgXPnFqDAcxTqJYbNRyEoM5o2kTw/edit

## BOOT CONTRACT FOR STATELESS RENTERS
1. Read this bulletin before creating issues, fixes or docs.
2. Read live target NOW.md, current branch/default SHA, PR head, tests, deployed SHA and linked issues.
3. Compare evidence timestamp and actor. Mark historical/contradicted facts SUPERSEDED; don't copy as current truth.
4. Search previous agent attempts and tests. Record a one-line evidence delta: new fact, disproven hypothesis, remaining missing fact.
5. Use EXECUTE only for a safe next experiment; HOLD requires precise unavailable access/authority; CLOSE only after verified user/client acceptance.
6. Post dated receipt back to issue and bulletin proposal; never claim Cloud/Drive has synchronized to inaccessible Local GSMB.
7. Local mirror required at Windows OneDrive Schematics when accessible. Current local mirror: NOT VERIFIED / NOT WRITTEN.
