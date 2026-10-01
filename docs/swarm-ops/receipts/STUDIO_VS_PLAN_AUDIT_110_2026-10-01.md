# STUDIO VS PLAN AUDIT #110 - 2026-10-01 (WAVE 2, ISSUE #110)

**Status:** OBSERVATION RECEIPT -> issue #110 box 2 (audit) evidenced; box 4 (build/tests) evidenced; boxes 3, 5, 6, 7, 8 stay OPEN. No code, CSS, workflow, or navigation change is made by this PR. Issue #110 stays OPEN.
**Scope:** Classify every GUI/UX plan artifact that exists on `master` against the current `kopano-core/studio` source as **implemented / stale / blocked / actionable**, and record a build, lint and smoke-test run of the Studio. Browser click-path QA is a runtime lane that stays owner-run. Actionable defects are listed, not fixed, so that each fix can be its own bounded PR.
**Ledger:** `ILR-2026-09-30` (`docs/swarm-ops/receipts/ISSUE_RECONCILIATION_LEDGER_2026-09-30.{md,json}`). Inputs: claims C-110-1 (compare pointer retired in NAVIGATION, POC_VALIDATED), C-110-2 (Studio-versus-plan audit not done, POC_PENDING) and the Wave 2 slice row `#110 | Studio-versus-plan audit document classifying each plan item implemented / stale / blocked / actionable. Browser QA and UX fixes stay separate runtime lanes.` The ledger itself is updated in Wave 3, not here.
**Base:** `master@2b8a58da` · **Branch:** `cursor/estate-studio-skills-observation-4e71` · **Live read time:** 2026-10-01T01:20Z-01:45Z (GitHub issue reads, Studio build log at 01:23Z).
**Actor:** Cursor cloud agent, stateless renter, operational rank Chief Facilitator. Authority: Robyn's approval of the Wave 0-3 plan (2026-09-30 22:14 UTC). No authority to resurrect a branch, change a deployment trigger, or declare browser QA passed.
**GSMB tier:** Cloud (this branch). Local and Google Drive: UNKNOWN. The owner's OneDrive checkout on the stale branch (`fcf5c96f…`, dirty, per the 2026-09-07 comment) is not readable from this VM.
**Doctrine:** `I_AM_STATELESS_RENTER_NOT_LANDLORD` · `WRITTEN_INSTRUCTION != RUNTIME_ENFORCEMENT` · `CLEAR_PASS != POC_VALIDATED` · `UNREADABLE != ABSENT` · `BUILD_GREEN != BROWSER_QA_PASSED` · SWFUS/RTC: historical `/Structure` or GUI plans are testimony, not automatic current truth.

---

## 0. Decision in one paragraph

The issue asked for eight things. The first (retire the stale compare pointer in canonical navigation) was already done in `docs/swarm-ops/NAVIGATION.md` on 2026-09-08 and the owner confirmed it on 2026-09-07. This receipt does the second (classify plan items against the Studio) and the fourth (build, lint, `test:ui` run; all three exit 0). Reading the plan artifacts that are actually on `master` - the 2026-05 wireframe spec, the 2026-05 architecture note, the 2026-04 dev-tracker checkpoints and the 2026-08-28 NAVIGATION lane - against `ConsolePage.tsx` shows that the console described in the wireframe is **implemented in source** in its main regions (mode rail, persona route, connectors, composer with tool chips, proof bar, git sync, CI deep links, mark-complete gate, two responsive breakpoints), with a seven-mode rail that is a superset of the four modes the spec drew. What is **not** done is split into three kinds: runtime-only work that a cloud renter cannot witness (browser QA of the seven modes, visual confirmation of the drawer/hamburger behaviour, server-side tool adapters); plan residue that is stale (the `/Structure`-class UI plans are not on `master`, the wireframe's `Settings` rail item and "worker cards" vocabulary never landed); and one actionable defect the first checkbox did not cover: the retired branch name `codex/kc-sovereign-gui-full-dev` is still **served live** by `kc_swarm_console_api.py` as `compare_url` and rendered at `ConsolePage.tsx:641`, still listed as a `push` trigger in `swarm-proof.yml`, still called "current / Active" in `SECURITY.md`, still the README deploy badge, and still the deploy path in the runbook. Those are bounded fixes for separate PRs, not for this observation. **Boxes 2 and 4 evidenced; boxes 3, 5-8 OPEN; issue stays OPEN.**

## 1. Governing record (verified live)

| Source | Id | Date (UTC) | What it says | Class |
|---|---|---|---|---|
| Issue #110 | state `open`, created `2026-08-28T17:30:19Z`, `updated_at 2026-09-07T00:42:51Z`, 1 comment, 0 labels | - | Title: "[KC GUI] Reconcile Structure/UI-UX plans with current Studio and retire stale GUI branch pointer" | E2 |
| Issue #110 body, "Repository truth recovered - 2026-08-28" | - | - | NAVIGATION pointed to `kopano-core/studio/src/pages/ConsolePage.tsx` + `GET /api/kc/swarm-console/status`; the GUI branch was "0 commits ahead and 347 commits behind `master`"; "Current `ConsolePage.tsx` already contains Context / Swarm / MAO / KPEFS / Proof / CI / Sovereign SIM modes" | E2 |
| Issue #110 body, "Required execution" | - | - | 8 boxes, 0 checked: (1) remove/replace stale pointer in canonical navigation; (2) audit plan artifacts vs studio, classify implemented/stale/blocked/actionable; (3) preserve canonical owner-interface target from Main Brain, no parallel GUI truth; (4) validate Studio build/tests; (5) browser/click-path QA for Context, Swarm, MAO, KPEFS, Proof, CI, SIM where runtime available; (6) fix actionable defects in bounded PRs; (7) keep runtime-only blockers explicit; (8) update receipts/Now | E2 |
| Comment by `RobynAwesome` | 2026-09-07T00:42:51Z | - | "first checkbox already satisfied; remainder OPEN"; "Parent audit: #122"; OneDrive checkout on the stale branch at `fcf5c96f…`, dirty; "do **not** commit or push the locally staged `tools/kpgs-browser-mcp` copy" (already on master via PR #118 `01ec0c5…`); "Remaining #110 work (Studio vs plan audit, browser QA, bounded UX slices) stays open and must start from `master`" | E2 |
| `docs/swarm-ops/NAVIGATION.md` L22, L43 | last touched `7d82ed81` | 2026-09-08 | L22 "KC GUI reconciliation lane \| Issue #110 \| ... replaces the obsolete `codex/kc-sovereign-gui-full-dev` compare pointer"; L43 "**GUI branch truth (2026-08-28):** ... retained only as historical testimony ... `0` commits ahead and `347` commits behind. Do not resurrect" | E2 |
| Ledger `ILR-2026-09-30` | C-110-1 POC_VALIDATED; C-110-2 POC_PENDING; row #110 POC_PENDING / HOLD | 2026-09-30 | Wave 2 output = this classification document; browser QA and UX fixes stay separate | E2 |

**Teach-back:** the owner closed the pointer question for the canonical navigation file and left everything else open, with the instruction that any further work starts from `master`, not from the stale branch. This receipt starts from `master@2b8a58da` and does not read, fetch, merge or push the stale branch.

## 2. Plan artifacts actually present on `master@2b8a58da`

The issue title says "Structure/UI-UX plans". On this base, `Structure/` contains exactly two entries, `discord_backup_codes.txt` and `07-Agents` (`ls Structure/`). Neither was opened (both are on the exclusion list in #122). There is **no UI/UX plan file under `Structure/`**. The plan artifacts that do exist are:

| # | Artifact | Lines | Last touched (commit, date) | What it plans | Class |
|---|---|---|---|---|---|
| P1 | `docs/swarm-ops/KC_SWARM_CONSOLE_WIREFRAME_SPEC.md` | 91 | `ff6886f4`, 2026-05-16 | Four-column layout: left rail (Console / Swarm / Proof / CI / Settings); left sidebar (workspace selector, persona router KC -> Cassey, connectors Web / GitHub / Kopano Context / JSONL, skill toggles); centre (single composer + tool chips Web / Fetch / Git / Swarm / Proof); right rail (Receipts & proof bar, Git sync ahead/behind, Logs, CI deep link). Responsive: <=1320px drawer, <=980px hamburger. Flows A prompt -> route -> execute; B swarm dispatch "worker cards"; C proof gate "Mark complete" disabled until PASS | E2 |
| P2 | `docs/swarm-ops/KC_SWARM_CONSOLE_ARCHITECTURE.md` | 109 | `1c5b4acc`, 2026-05-18 | §1 regions Context / Swarm / Proof / CI; §4 implementation order: 1 app shell, 2 streamed chat + BFF, 3 persona routing, 4 tool adapters server-side, 5 receipts store + validate/proof-check in Proof rail, 6 swarm controls | E2 |
| P3 | `docs/swarm-ops/tools/kc-swarm-console-wireframe.html` | 301 | `1c5b4acc`, 2026-05-18 | Static HTML mock of P1 | E2 |
| P4 | `Schematics/04-Updates/dev-tracker.md` | - | `7314fb41`, 2026-04-13 | L80 "GUI Demo Split" (2026-04-08); L160 "Redesign Checkpoint" (2026-04-09); L185 "live browser click-path QA is still pending"; L208 "browser QA now passes for live-event rendering across all three views, Forge create/edit/lane move, and MCP Console send/stream"; L226-234 App Insights / framer-motion notes | E2 (dated testimony about an earlier Studio) |
| P5 | `docs/swarm-ops/NAVIGATION.md` L22, L43 | - | `7d82ed81`, 2026-09-08 | The current, canonical pointer: #110 lane replaces the stale compare pointer | E2 |
| P6 | Main Brain "owner interface" target (#110 box 3) | - | - | `rg -il "owner interface\|god mode" Schematics/21-KOPANO-PHU\ GOVERNACE\ SYSTEMS/MAIN-BRAIN/` = 0 files; `Schematics/00-Home/Now.md` (47 lines) has 0 matches for `gui\|studio\|owner-interface`. The target the issue says to "preserve" is not locatable by those phrases | E4 |

P4's L208 "browser QA now passes" is dated 2026-04 and refers to a three-view Studio that predates the seven-mode `ConsolePage` (`d7ef6b39`, 2026-08-14). It is **not** evidence for box 5 today.

## 3. Studio surface read (source only, no runtime)

`kopano-core/studio/src/pages/ConsolePage.tsx` is 718 lines, last touched `d7ef6b39` (2026-08-14). Anchors cited below were re-read at this base with `rg -n`.

| Plan item (from P1/P2) | Where it is in source | Status | Class |
|---|---|---|---|
| Left rail: Console / Swarm / Proof / CI / Settings | `ConsolePage.tsx:9` `type ConsoleMode = 'context' \| 'swarm' \| 'mao' \| 'kpefs' \| 'proof' \| 'ci' \| 'sim';` `:132` `useState<ConsoleMode>('context')` | **IMPLEMENTED (superset)**: 7 modes vs 4 drawn. `Settings` is not a mode (`rg -c "Settings" ConsolePage.tsx` = 0) -> that rail item is **STALE** in the plan | E2 |
| Persona router KC -> Cassey | `:151-153` fetches `/api/kc/swarm-console/status`, `/api/kc/swarm-agents`, `/api/mao/status`; `:196` `agents.find((a) => a.id === 'cassey')`; `:225-226` `{status?.persona_route ?? 'Cassy -> Cassey · KC'}`; server side `kc_swarm_console_api.py:225` `"persona_route": "Cassy (student) -> Cassey (teacher) · KC (brain ledger)"` | **IMPLEMENTED** (server-provided string with client fallback) | E2 |
| Connectors panel (Web / GitHub / Kopano Context / JSONL) | `:281` `<h3>Connectors</h3>` | **IMPLEMENTED** as a panel; the exact connector list is rendered from `status` and is **BLOCKED** from verification without the API running | E2 / E4 |
| Single composer + tool chips Web / Fetch / Git / Swarm / Proof | `:338` and `:453` `className="glass-card console-composer"`; `:364` `['Web', 'Fetch', 'Git', 'Swarm', 'Proof'].map(...)` | **IMPLEMENTED**: chip list matches P1 exactly | E2 |
| Receipts & proof bar | `:327` `Proof bar: {status?.proof_bar_pass ? 'PASS' : 'OPEN'}`; server `kc_swarm_console_api.py:207` `proof_bar_pass = validate_code == 0 and proof_code == 0 and guard_code == 0` | **IMPLEMENTED** (P2 §4 step 5 "validate/proof-check in Proof rail" is wired to three exit codes) | E2 |
| Git sync ahead/behind | `:685` `<h3>Git sync</h3>` | **IMPLEMENTED** as a panel; values are runtime | E2 |
| CI deep link | `:638` `href={status.ci.actions_url}`; `:641` `href={status.ci.compare_url}` | **IMPLEMENTED**, but `compare_url` is served as the retired branch compare (see A1 in §5) | E2 |
| Flow C: "Mark complete" disabled until PASS | `:707` `<h3>Mark complete</h3>` | **IMPLEMENTED** as a panel; the disabled-until-PASS behaviour is **BLOCKED** from verification without runtime | E2 / E4 |
| Flow A: prompt -> route -> execute (P2 §4 step 3, 6) | `:515` `fetch(\`${apiRoot}/api/mao/route\`)`; `:486` `fetch(\`${apiRoot}/api/mao/execute\`)` | **IMPLEMENTED** as client wiring; the server-side tool adapters of P2 §4 step 4 are outside the Studio and **BLOCKED** from this read | E2 / E4 |
| Flow B: swarm dispatch "worker cards" | `rg -c "worker" ConsolePage.tsx` = 0 | **STALE** vocabulary; the `swarm` mode exists but the "worker cards" presentation named in P1 does not | E2 |
| Responsive <=1320px drawer, <=980px hamburger | `src/App.css:2466` `@media (max-width: 1320px)`; `:2476` `@media (max-width: 980px)`; `rg -c "hamburger\|drawer" src/` = 0 | **IMPLEMENTED** breakpoints at the exact widths; the drawer/hamburger behaviour is a visual claim that is **BLOCKED** from a source-only read | E2 / E4 |
| Streamed chat + BFF (P2 §4 step 2) | `src/apiBase.ts` exposes `getWsLiveUrl` -> `/ws/live`; `VITE_KC_API_BASE_URL` | **IMPLEMENTED** as a client helper; streaming is **BLOCKED** from verification without the API | E2 / E4 |
| Other routed pages (P4 "public/admin split") | `src/pages/{Admin,Council,Forge,Labs,Training}Page.tsx` present; `src/operator/operatorApi` calls `/api/kc/god/desktop-session \| overview \| actions/run \| git/run` | **IMPLEMENTED** as routes; outside #110's seven-mode QA list | E2 |

## 4. Build, lint and smoke test (box 4) - `/tmp/studio_build_110.log`, 2026-10-01T01:23Z

Run in this worktree at `kopano-core/studio` with the scripts declared in `package.json` (`"build": "tsc -b && vite build"`, `"lint": "eslint ."`, `"test:ui": "node tests/labs-ui-smoke.mjs"`). These are the same two commands CI runs in job `gui-check` (`.github/workflows/ci.yml` L125 job, L132 `working-directory: kopano-core/studio`, L150 `npm run lint`, L153 `npm run build`), plus the smoke test CI does not run.

| Step | Result | Class |
|---|---|---|
| `npm ci` | `added 177 packages in 2s`, `NPM_CI_EXIT=0` | E2 |
| `npm run build` | `vite v8.3.1 building client environment for production...`, `✓ 588 modules transformed`, `✓ built in 333ms`, `BUILD_EXIT=0`. Chunks: `index.html` 0.46 kB; index CSS 32.72 kB; `CouncilPage` 5.12 kB; `LabsPage` 5.50 kB; `AdminPage` 7.86 kB; `ForgePage` 9.22 kB; `TrainingPage` 10.60 kB; `ConsolePage` 32.14 kB; index JS **568.83 kB** (gzip 193.68 kB) with Vite's `(!) Some chunks are larger than 500 kB after minification` warning | E2 |
| `npm run lint` | `✖ 5 problems (0 errors, 5 warnings)`, `LINT_EXIT=0`. All five are `react-hooks/set-state-in-effect` on a `void refresh();` inside `useEffect`: `src/App.tsx:292:9`, `src/operator/KpefsConsolePanel.tsx:97:10`, `src/operator/OperatorProvider.tsx:93:10`, `src/operator/PhuLegacyCard.tsx:48:10`, `src/operator/SovereignSimCard.tsx:68:10`. `NOW.md` L124 already records "5 existing `react-hooks/set-state-in-effect` warnings"; the count is unchanged | E2 |
| `npm run test:ui` | `labs-ui smoke tests passed`, `TESTUI_EXIT=0` | E2 |
| `git status --short` after the run | clean (no generated file left in the tree) | E2 |

`BUILD_GREEN != BROWSER_QA_PASSED`. These three exit codes evidence box 4 only. They say nothing about box 5.

## 5. Classification summary and actionable list

### 5.1 Implemented (in source)

Seven-mode rail; persona route; connectors panel; single composer with the five P1 tool chips; proof bar driven by three validator exit codes; git-sync panel; CI deep links; mark-complete panel; MAO route/execute wiring; `/ws/live` helper; responsive breakpoints at 1320px and 980px; routed Admin / Council / Forge / Labs / Training pages. Build, lint and smoke test exit 0 at this base.

### 5.2 Blocked (runtime-only; owner or Vercel/API runtime lane)

- Browser click-path QA of the seven modes Context, Swarm, MAO, KPEFS, Proof, CI, SIM (box 5).
- Visual confirmation of drawer (<=1320px) and hamburger (<=980px) behaviour.
- "Mark complete" disabled-until-PASS behaviour under a live `proof_bar_pass`.
- Connector list, git-sync values and streamed chat as rendered from a live `/api/kc/swarm-console/status` and `/ws/live`.
- Server-side tool adapters (P2 §4 step 4) - outside the Studio tree.

These are the box 7 "runtime-only blockers". `tools/kpgs-browser-mcp` is on master (PR #118) and is the natural instrument, but it was not run here.

### 5.3 Stale (plan testimony that no longer describes the Studio)

- "Structure/UI-UX plans" as a location: no such files exist under `Structure/` on `master`.
- P1 `Settings` rail item; P1 "worker cards"; P1 "hamburger" / "drawer" as named components (0 source hits; breakpoints exist, names do not).
- P1/P2/P3 are dated 2026-05-16/18 and draw four modes; the Studio has had seven since at least `d7ef6b39` (2026-08-14).
- P4 dev-tracker 2026-04 checkpoints, including L208 "browser QA now passes" for a three-view Studio that no longer exists in that form.
- The stale branch `codex/kc-sovereign-gui-full-dev` itself: `STALE_PRESERVATION` only; not fetched, read, merged or pushed by this receipt.

### 5.4 Actionable (bounded fixes for separate PRs; **none performed here**)

**A1 - retired branch name still live outside NAVIGATION.** Box 1 was satisfied for `docs/swarm-ops/NAVIGATION.md`, but `rg -n "codex/kc-sovereign-gui-full-dev" --glob '!**/node_modules/**'` at this base still returns the following, grouped by what a fix would touch:

| Group | File:line | What it does today | Suggested bounded PR |
|---|---|---|---|
| Live-served / rendered | `kopano-core/kopano/kc_swarm_console_api.py:30-32` `_COMPARE_BRANCH = (".../compare/master...codex/kc-sovereign-gui-full-dev?expand=1")`, `:258` `"compare_url": _COMPARE_BRANCH`; rendered at `ConsolePage.tsx:641` | Every Console CI panel links to a compare against the retired branch | A1a: replace the compare target (owner to name it: `master...HEAD`, the current PR, or drop the link) |
| Live-served | `kopano-core/kopano/phu_ecosystem.py:291` | Same string in ecosystem data | A1a |
| CI trigger | `.github/workflows/swarm-proof.yml:59-60` `push: branches: - codex/kc-sovereign-gui-full-dev` | A push to the retired branch still triggers the swarm proof | A1b: retarget or remove (`pull_request` on `[master, main]` at L8 already exists) |
| Repo-facing governance docs | `README.md:4` deploy badge `deploy-web.yml/badge.svg?branch=codex/kc-sovereign-gui-full-dev` (`7a8b153b`, 2026-08-22); `SECURITY.md:19` "\| `codex/kc-sovereign-gui-full-dev` (current) \| ✅ Active \|" (`d7ef6b39`, 2026-08-14); `docs/swarm-ops/DEPLOYMENT_RUNBOOK.md:31` "Push to `codex/kc-sovereign-gui-full-dev` -> GitHub Actions -> FTP upload to IONOS" (`92f0b4f9`, 2026-06-24) | README and SECURITY present the retired branch as current; the runbook describes a deploy path from it | A1c: docs-only PR; SECURITY.md supported-branches row should name `master` |
| Scripts (11) | `scripts/kc_cf_comms_activate.py:21`, `kc_production_verify_run.py:19`, `kc_apprenticeship_activate.py:52`, `kc_cassy_activate.py:70`, `kc_wit_handlers.py:17`, `kc_cassy_wit_steward.py:25`, `kc_main_brain_roadmap.py:17`, `kc_apprenticeship_steward.py:32`, `kc_apprenticeship_handlers_extra.py:121` (`"KCA-0602": lambda: h_grep(".github/workflows/swarm-proof.yml", "codex/kc-sovereign-gui-full-dev", "Push trigger.")`), `kiro_autonomous_strep_order.py:98`, `kiro_session3_final_close.py:14` | Hard-coded branch constants; `KCA-0602` is an apprenticeship check that **asserts the stale trigger is present**, so A1b must land with its handler updated or the check fails | A1d: scripts PR, sequenced after A1b |
| Other docs / data | `docs/swarm-ops/apprenticeship/progress.json:22`; `docs/portfolio/RKC_MONDAY_EXECUTION.md:27`; `docs/portfolio/LIFESTYLE_GEMINI_HANDOFF.md:19`; `docs/swarm-ops/jiro/JIRO_STAP_SESSION4_TASKS.md:61`; `docs/swarm-ops/tools/git-sync-monitor.html:103,135,181,218,220` | Dated handoffs and a monitor page | A1e: owner decides which are historical (leave) and which are live tools (`git-sync-monitor.html`) |
| Historical records - **leave as-is** | `NOW.md:82,933,948`; `Schematics/04-Updates/comms-log.md:1013,1612,2104`; `docs/swarm-ops/logs/KC Review Log.jsonl` and `KC Main Brain Log.jsonl` `evidence_urls`; `docs/product-discovery/issue-231/PREPARATION-RECEIPT.md:5`; `CLASSROOM_ADMISSION_PACKET_115_116_2026-09-30.md:227,285,287,290`; `LOCAL_GSMB_CONTINUITY_AUDIT_2026-10-01.md:14`; the ledger | Append-only testimony | none |

**A2 - five lint warnings** (`react-hooks/set-state-in-effect`, §4). Known since NOW.md L124; a bounded Studio PR could move each `void refresh()` into an event/callback pattern. Not a build blocker (`LINT_EXIT=0`).

**A3 - main bundle 568.83 kB** (Vite warning). Informational; `ConsolePage` is already a separate 32.14 kB chunk. A manual-chunks or lazy-import PR is optional.

**A4 - owner-interface target (box 3) not locatable.** P6: the Main Brain "owner interface" the issue says to preserve could not be found by phrase. Owner to name the file so that box 3 can be checked against it; otherwise box 3 is UNKNOWN, not failed.

## 6. Box-by-box state after this receipt

| Box | Text (abridged) | State | Evidence |
|---|---|---|---|
| 1 | remove/replace stale pointer in canonical navigation | DONE for NAVIGATION (owner 2026-09-07; C-110-1); **residue elsewhere** = A1 | §5.4 |
| 2 | audit plan artifacts vs studio, classify | **EVIDENCED by this receipt** (C-110-2 -> candidate POC_VALIDATED on merge) | §2, §3, §5 |
| 3 | preserve canonical owner-interface target from Main Brain | UNKNOWN (target not locatable, A4) | §2 P6 |
| 4 | validate Studio build/tests | **EVIDENCED** (`BUILD_EXIT=0`, `LINT_EXIT=0`, `TESTUI_EXIT=0`) | §4 |
| 5 | browser/click-path QA, 7 modes | BLOCKED (runtime; owner-run) | §5.2 |
| 6 | fix actionable defects in bounded PRs | OPEN (A1-A3 listed, none fixed) | §5.4 |
| 7 | keep runtime-only blockers explicit | EVIDENCED as a list; stays open until box 5 runs | §5.2 |
| 8 | update receipts/Now | this receipt; NOW.md POST-SEED is Wave 3 | - |

## 7. C.L.E.A.R.

| Axis | Assessment |
|---|---|
| **Complete** | Every GUI plan artifact findable on `master` (P1-P6) is listed; every P1/P2 region is mapped to a source anchor or marked blocked; all eight boxes are restated; the full compare-pointer residue is enumerated with a repo-wide grep. |
| **Logical** | "Implemented" is claimed only where a source anchor exists; "blocked" only where the claim is about rendered or runtime behaviour; "stale" only where the plan names something with zero source hits or a superseded date; "actionable" only where a bounded diff is describable. |
| **Evidence** | Issue and comment reads, file line numbers, commit SHAs with dates, grep counts and the three exit codes are E2 and timestamped. Rendered behaviour is E4 and labelled. P4's 2026-04 QA line is E1/E2 testimony about an earlier Studio, not current proof. The owner-interface target is E4. |
| **Audience** | Owner (boxes 3, 5, 6 decisions; A1a compare target); future Studio renters (what exists, what not to re-plan); Wave 3 (ledger C-110-2 move). |
| **Relevant** | Bounded to #110. Does not touch #122's estate census (separate receipt) or #94. The only #122 overlap is the shared exclusion list for `Structure/`. |

`CLEAR_PASS != POC_VALIDATED`. This receipt validates that the plan-vs-source audit exists and that the Studio builds. It does not validate that the Studio works in a browser.

## 8. What this receipt does not claim

- No claim that browser QA passed for any of the seven modes (box 5).
- No claim that the drawer, hamburger, mark-complete gate or connector list behave as drawn; only that their source anchors and breakpoints exist.
- No claim about the stale branch's contents; it was not fetched. `STALE_PRESERVATION` stands.
- No claim that the five lint warnings or the bundle size are defects requiring action; they are listed as optional bounded slices.
- No claim about the owner's OneDrive checkout (`fcf5c96f…`) or its dirty state beyond the owner's 2026-09-07 testimony.
- No fix was applied: `git status --short` in this worktree shows only this receipt file.
- No claim that #110 can close.

## 9. Decisions requested (owner)

- [ ] Name the compare target that should replace `_COMPARE_BRANCH` in `kc_swarm_console_api.py` (A1a), or confirm the CI panel should drop the compare link.
- [ ] Approve A1b (remove the `push` trigger on the retired branch in `swarm-proof.yml`) together with the `KCA-0602` handler update (A1d), or keep the trigger and say why.
- [ ] Approve A1c (README badge branch, `SECURITY.md` supported-branch row, `DEPLOYMENT_RUNBOOK.md` deploy path) as a docs-only PR.
- [ ] Name the Main Brain file that holds the canonical owner-interface target (A4) so box 3 can be evaluated.
- [ ] Decide whether box 5 is run via `tools/kpgs-browser-mcp` against a local API, against a deployed Studio, or deferred.
- [ ] Decide whether A2 and A3 are wanted at all.

On merge of this PR, Wave 3 appends: `#110 -> audit receipt filed <sha>; boxes 2, 4 evidenced; A1-A4 open; C-110-2 POC_VALIDATED (audit exists), browser QA POC_PENDING`. #110 remains open.

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
