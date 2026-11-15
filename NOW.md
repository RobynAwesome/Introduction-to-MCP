# NOW — Current Operational State (`2026-11-11` · `2026-W46`)

```text
I_AM_STATELESS_RENTER_NOT_LANDLORD
```

Repository-root `NOW.md` is the **volatile salience / temporal truth** layer.
As mandated by `AGENTS.md` and `STATELESS_RENTER_ENTRYWAY.md`, repo root NOW.md is the comms lane and current-state authority that every stateless renter must read before execution and update before handoff.

## CURRENT STATE — `2026-11-11T18:16:30+02:00` (`AG | RESTORE ORIGINAL MISSION | CCP-FIRST + REV-01`)

- **Active Mission:** KPGS and Kopano Labs Engineering Recovery across Accountability (`W1`), `Introduction-to-MCP` Security (`W2`), `Bookit-5s-Arena` (`W3`), `KasiLink` (`W4`), `Kopano-Labs-Website` (`W5`), `NOW.md` Weekly Continuity (`W6`), Studio Reliability (`#110` / PR `#365`), and Spatial Studio Dashboard (`#110` / PR `#397`).
- **Current Weekly Board:** [`NOW/2026-11/2026-W46/WEEK.md`](NOW/2026-11/2026-W46/WEEK.md)
- **Current Machine Receipts:** [`NOW/2026-11/2026-W46/RECEIPTS.jsonl`](NOW/2026-11/2026-W46/RECEIPTS.jsonl)
- **Lossless Full Archive (`182,978` bytes):** [`NOW/ARCHIVE/NOW_PRE_W46_2026-11-11.md`](NOW/ARCHIVE/NOW_PRE_W46_2026-11-11.md)
  - **Archive SHA-256:** `66b74627c792b1182937002a6bfe7ea92889f62b0ccf457a38bd6d598a13064d`
  - **Archive Byte Size:** `182978`

### Active Workstream Summary (`2026-W46`)

1. **`W1-ACCT-REV01` (`RobynAwesome/Introduction-to-MCP`, branch `ag/rev01-enforcement-proof-2026-w46`, SHA `623eb87b`):** `TESTS PASSED` (`56/56`). Enforces 5-stage restriction lifecycle, BlackMask explicit acknowledgement (`require_explicit_ack=True`), `stateless_renter.py` cycle guard, and `.agents/hooks.json` `PreToolUse` gate (`ACTIVE_COUNT 0 / LATENT_COUNT 0`).
2. **`W2-ITMCP-SEC` (`RobynAwesome/Introduction-to-MCP`, branch `ag/spp-366-and-codeql-16-2026-w46`, SHA `07af97d2`):** `TESTS PASSED` (`49/49`). Reconciles Security Playground PR `#366` and `#369` duplicate-JSON-key parity (`BLOCK` exit 4), upgrades `kopano-core/kopano/database.py` password hashing to `PBKDF2-HMAC-SHA256` (`600,000` iterations, CodeQL `#16`), removes `"demo-admin"` fallback in `runtime.py`, and restores `.gitmodules` for `KasiLink`.
3. **`W3-BOOKIT-COURTS` (`Kopano-Labs/Bookit-5s-Arena`, branch `ag/bookit-court-schema-and-cve-2026-w46`, SHA `55b757e5`):** `TESTS PASSED` (`18/18` unit tests + `4` courts asset guard). Read-only Atlas inspection (`inspect-bookit-inventory.mjs --discover`) proved `bookit-5s-arena.reqjuuf.mongodb.net` is online and holds all 4 courts (`Premier`, `Secondary`, `Third`, `Fourth` @ R400/hr) in database `bookit`, whereas `MONGODB_URI` lacked `/bookit` and defaulted Mongoose to `test` (`0` courts). Fixed via `resolveMongoConnectOptions` in `lib/mongodb.js` + merged PR `#55` (`price_per_hour` compatibility) and PR `#58` (`next@15.5.29`, `sharp@0.35.5`, `undici@7.30.2`).
4. **`W4-KASILINK-RECOVERY` (`RobynAwesome/KasiLink`, branch `ag/kasilink-pr34-srv-and-cve-2026-w46`, SHA `16452f43`):** `TESTS PASSED` (`14/14` Vitest). Confirmed `_mongodb._tcp.kasilink.zzuvwlo.mongodb.net` is `NXDOMAIN`; hardened `lib/db.ts` on top of PR `#34` (`d5a44862`) to reset `cache.promise = null` on failure and classify `MONGODB_SRV_UNAVAILABLE` with credential redaction.
5. **`W5-WEB-JOURNEY` (`RobynAwesome/Kopano-Labs-Website`, branch `ag/website-lockfile-and-journey-2026-w46`, SHA `d6e5cc3fba`):** `TESTS PASSED` (`companion:verify`, `journey:verify`, `identity:verify` all `PASS` for Issues `#39` and `#41`; zero Three.js/visual modifications per 2 Nov KMBP directive).
6. **`W6-NOW-CONTINUITY` (`RobynAwesome/Introduction-to-MCP`, branch `ag/now-weekly-pilot-2026-w46`):** `TESTS PASSED`. Lossless weekly continuity structure (`NOW/2026-11/2026-W46/WEEK.md` + `RECEIPTS.jsonl`) verified under `<10 KB` root budget (merged on `master` as `55efbe34`).
7. **`#110 / PR #365 Studio reliability` (`RobynAwesome/Introduction-to-MCP`, branch `codex/issue-110-console-status-contract`, merged `9b746564`):** Validates Console status, isolates failed/malformed startup and refresh payloads (`startupContracts.mjs`), guards connector POST responses (`isConnectorActionResult`, fixing `TypeError` on malformed `commands` and HTTP 500 handling), and runs `test:ui` in CI. Hosted Vercel deployment routing, real chat response, and cross-process receipt remain `HOLD`.
8. **`#110 / PR #397 Spatial Studio Dashboard` (`RobynAwesome/Introduction-to-MCP`, branch `codex/issue-110-spatial-studio`):** Sets Dashboard (`#/console`) as Studio's default entrance with CSS 3D focal navigation to seven direct detail routes (`#/console/<mode>`), closes `GodModeDock` by default on `/console`, respects reduced motion, and carries `#365` reliability guards forward. See [spatial Studio spec](docs/swarm-ops/ISSUE_110_SPATIAL_STUDIO_SPEC.md); hosted backend, durable receipt store selection, live chat response, and restart retrieval remain `HOLD`.

### Next Admissible Action & Owner Gates

- **Awaiting Owner Approval (`USER ACCEPTED` / Push & Merge Gate):** Push isolated branches to GitHub remotes, merge PRs (`#365`, `#399`, `#400`, `#366`, `#55`/`#58`, `#34`), set `MONGODB_DB_NAME=bookit` (or `/bookit` URI path) on Vercel for `fivesarena.com`, and repoint `MONGODB_URI` for `kasilink.com` to an active Atlas cluster.

---

## PRIOR STATE — HISTORICAL LOG — PRESERVED PROVENANCE

- **Pre-W46 Full Ledger (`2026-06-22T06:39 SAST` through `2026-11-11`):** Preserved byte-for-byte in [`NOW/ARCHIVE/NOW_PRE_W46_2026-11-11.md`](NOW/ARCHIVE/NOW_PRE_W46_2026-11-11.md) (`182978` bytes, SHA-256 `66b74627c792b1182937002a6bfe7ea92889f62b0ccf457a38bd6d598a13064d`).
- **Verification Command:** `python scripts/now_archive_pilot.py --verify`

## 2026-11-15 — W3 Bookit court restoration and release state (SAST)

- Live GitHub status on this date: [PR #55](https://github.com/Kopano-Labs/Bookit-5s-Arena/pull/55) and [PR #58](https://github.com/Kopano-Labs/Bookit-5s-Arena/pull/58) are open drafts; [PR #60](https://github.com/Kopano-Labs/Bookit-5s-Arena/pull/60) is open for review. None is merged. This corrects the W46 summary above, which described #55 and #58 as merged.
- Production currently runs 85e6e2b on fivesarena.com. On 2026-11-15, GET https://fivesarena.com/api/courts returned HTTP 200 with [] and X-FivesArena-Data-State: database-empty. A non-decrypting Vercel environment-variable listing found no COURT_CATALOGUE_MONGODB_URI configured.
- [Draft PR #61](https://github.com/Kopano-Labs/Bookit-5s-Arena/pull/61) proposes restoring the four public Hellenic courts through a separately scoped catalogue reader, with an allowlist of the observed court IDs and public fields. Existing booking/admin writes remain on the current operations connection. The court cards and detail page keep Setmore as the booking destination. The /bookings court CTA correction is included in #61.
- For [issue #42](https://github.com/Kopano-Labs/Bookit-5s-Arena/issues/42), the first release acceptance is the four real courts with correct images/rates and Setmore booking links. Preview and production need a dedicated Atlas principal restricted to find on bookit.courts before this can be verified with live data. The shared operations URI remains unchanged.
- Native booking remains on hold until existing Setmore and manual reservations are reconciled, overlapping requests cannot both succeed, and one persisted booking reference matches the customer confirmation and venue operator record.

### Follow-up verification · 15 November 2026 (SAST)

- [Bookit #61 at `cf754ed`](https://github.com/Kopano-Labs/Bookit-5s-Arena/commit/cf754edaa7065250d25c1f3d69eb5b8492eb9c29) routes the homepage court cards’ “Book Now” and the visible “Book Court” action on /bookings to the existing Setmore page at /book. The homepage photo/title opens court details through a separate link.
- [Bookit #61 at `b4d6f60`](https://github.com/Kopano-Labs/Bookit-5s-Arena/commit/b4d6f60d287d428ba1c9f87686ebf6f440b4133b) updates `lib/publicCourtCatalogue.js` so that when `COURT_CATALOGUE_MONGODB_URI` is unset, it reuses the existing `connectDB()` `MongoClient` against `bookit.courts` while keeping `mongoose.connection.name` on `test` for operations and still honoring `COURT_CATALOGUE_MONGODB_URI` if configured. Verified against live Atlas (`listPublicCourts()` returns all 4 Hellenic courts at `R400/hr` with `court-1.jpg`–`court-4.jpg`, non-allowlisted IDs return `null`, and `validate-court-assets` passed).
- The Vercel preview for `b4d6f60` ([`bookit-5s-arena-e3uozv59v-robynawesomes-projects.vercel.app`](https://bookit-5s-arena-e3uozv59v-robynawesomes-projects.vercel.app)) is READY. Check-run annotations (`132737101820`) confirm the three zero-step GitHub Actions failures on `Kopano-Labs/Bookit-5s-Arena` are due to an org runner billing lock (`The job was not started because your account is locked due to a billing issue`), not code or test regressions.
