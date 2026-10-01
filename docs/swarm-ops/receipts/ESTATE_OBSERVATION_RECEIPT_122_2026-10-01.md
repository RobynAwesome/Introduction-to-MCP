# ESTATE OBSERVATION RECEIPT #122 - 2026-10-01 (WAVE 2, ISSUE #122)

**Status:** OBSERVATION RECEIPT -> cloud-readable subset of #122 refreshed and filed **in the repository** (the 2026-09-07 receipts the issue cites are not on `master`). Boxes 2, 5 (cloud part), 7 evidenced; boxes 1 (cloud variant), 3, 4, 6 stay OPEN or human/provider gated. Issue #122 stays OPEN; the owner decides close-as-superseded versus keep-as-umbrella.
**Scope:** Read-only GitHub census of the 22 named repositories (identity, default branch, head SHA, open PRs, workflow runs **at the head SHA**) under both `RobynAwesome` and `Kopano-Labs`; HTTPS HEAD probe of the public serving surfaces named in the 2026-09-07 comments plus the KasiLink API routes. Nothing was pushed, merged, deployed, aliased or opened from the exclusion list. Anything not verifiable from this VM is written as `UNKNOWN`, not inferred.
**Ledger:** `ILR-2026-09-30` (`docs/swarm-ops/receipts/ISSUE_RECONCILIATION_LEDGER_2026-09-30.{md,json}`). Inputs: claims C-122-1 (22-repo refresh, POC_PENDING), C-122-2 (local census and Vercel proof, UNKNOWN), observation O-16 (cited receipt files absent from master), finding F-8 (keep #122 open as umbrella until an owner-local census exists) and the Wave 2 slice row `#122 | fresh read-only cloud-subset receipt ... unreadable rows marked UNKNOWN. Boxes 3 and 4 remain human or provider gated. Owner decides close versus keep.` The ledger itself is updated in Wave 3, not here.
**Base:** `master@2b8a58da` · **Branch:** `cursor/estate-studio-skills-observation-4e71` · **Live read time:** census window 2026-10-01T01:25:12Z-01:26:02Z (`/tmp/estate_census_122.sh`, output `/tmp/estate_census_122.tsv`, per-SHA run detail `/tmp/census_ci_detail.txt`); HTTPS probe 2026-10-01T01:40:13Z-01:40:33Z (`/tmp/http_probe_122.tsv`); issue re-read 2026-10-01T01:4xZ.
**Actor:** Cursor cloud agent, stateless renter, operational rank Chief Facilitator. Authority: Robyn's approval of the Wave 0-3 plan (2026-09-30 22:14 UTC). No authority over local clones, Vercel, DNS or issue state.
**GSMB tier:** Cloud (this branch). Local: UNKNOWN (the owner's OneDrive trees are not readable from this VM). Google Drive: UNKNOWN.
**Doctrine:** `I_AM_STATELESS_RENTER_NOT_LANDLORD` · `UNREADABLE != ABSENT` · `HTTP_200 != SERVING_SHA_PROVEN` · `NXDOMAIN_FROM_ONE_RESOLVER != ALIAS_ABSENT` · `CLEAR_PASS != POC_VALIDATED` · hard exclusions of #122 honoured verbatim.

---

## 0. Decision in one paragraph

Issue #122 is the declared parent audit of eight issues (#94, #102, #103, #107, #110, #115, #116, #121) and its two comments describe a completed 2026-09-07 cloud census plus a Vercel/HTTP probe, but both receipt files those comments cite (`Schematics/Audits_and_Guardrails/CA_ESTATE_AUDIT_2026-09-07.md`, `docs/governance/CA_ESTATE_AUDIT_2026-09-07_VERCEL_HTTP.md`) live only in an isolated local tree and are **absent from `master`** (ledger O-16). This receipt re-runs the cloud-readable part from this branch so that a dated, in-repo record exists: 21 of 22 repositories are readable under `RobynAwesome` (Partial-Knowable-Algebra returns 404 under both owners and is UNKNOWN, not absent); at default-branch head, 11 show a latest first-party or Dependabot run `success`, 3 show a latest run `failure` (cars4mars-landingpage first-party gate; lefa-ai a **scheduled** Dependency Audit while its six other workflows at the same SHA are green; starfall-salvage two Dependabot updater runs only), 7 have **no run at head**; separately `Kopano-Labs/Bookit-5s-Arena` has a first-party `APWA Proof Gate` failure at its own head and `Kopano-Labs/classroom50` has twenty consecutive scheduled `Collect Scores` failures. The 2026-09-06 "14 / 3 / 5" numbers are therefore superseded, and the failing-head list has changed (Harvest no longer fails - it has a newer head with no run; lefa-ai joined on a scheduled audit). Thirteen public hosts answered HTTP 200, one 404, nine did not resolve from this VM, and the three KasiLink API routes still return 500. Local census (box 3) and alias-versus-serving-SHA proof (box 4) cannot be done from here and stay UNKNOWN. **Boxes 2, 5-cloud, 7 evidenced; 1-cloud, 3, 4, 6 open; owner decides whether #122 closes as superseded by this receipt plus a later owner-local census, or stays as the umbrella.**

## 1. Governing record (verified live)

| Source | Id | Date (UTC) | What it says | Class |
|---|---|---|---|---|
| Issue #122 | state `open`, created `2026-09-07T00:26:50Z`, `updated_at 2026-09-07T01:38:06Z`, 2 comments | - | Title: "[Estate Audit] 2026-09-07 fresh 22-repo identity, local, CI, and Vercel witness refresh" | E2 |
| Body, "Observation frame" | - | - | Canonical cloud `RobynAwesome/Introduction-to-MCP` (repo id `1188724145`); `Kopano-Labs/Introduction-to-MCP` "is the same transferred identity, not a second mirror"; observation in an isolated tree from re-verified `master`; OneDrive checkout `codex/kc-sovereign-gui-full-dev` @ `fcf5c96f…` is STALE_PRESERVATION; `tools/kpgs-browser-mcp` already on master via PR #118 (`01ec0c5…`) | E2 |
| Body, "22 repositories" | - | - | The 22 names used in §2; "Dated 2026-09-06 window (must be refreshed): 14 CI success / 3 fail / 5 no run. Failing heads were Cars4Mars landing, Starfall, Harvest. Missing local clones: lefa-ai, KPGS-Agent-Mission-Control, kopano-contacts." | E2 |
| Body, "Hard exclusions" | - | - | Do not open `Structure/discord_backup_codes.txt`, `Structure/07-Agents`, any `.env`; do not route Aya into hackathons; do not invent DIRISA attendance, Cars4Mars physical state, KasiLink Atlas health, Jennifer production recovery; no nested `NOW.md` to fill a count; no alias change, cutover, merge to master, or deployment | E2 |
| Body, "Acceptance" | - | - | 7 boxes, 0 checked: (1) isolated tree pinned to re-verified `master` SHA; (2) 22/22 identities, SHAs, open PRs, CI-at-head refreshed; (3) local census exact-clean / exact-dirty / cloud-ahead / diverged / missing; (4) Vercel alias vs source SHA re-proven; (5) HOLD register written, August and 09-06 snapshots preserved first; (6) root `NOW.md` handoff only after receipts exist; (7) no push/merge/deploy of the stale GUI checkout | E2 |
| Body, "Next admissible action" | - | - | "Review receipts. Do not promote Jennifer `2220172e…`, Website `beb37f85…`, or Bookit fixtures `465d612…` without a separate authorization." | E2 |
| Comment 1 by `RobynAwesome` | 2026-09-07T01:21:47Z | - | Isolated tree `GSMB-estate-audit-2026-09-07` @ `c98dc235…` clean; receipt comments on 8 issues, none closed; Bookit main `9c06ef72…` -> `c5a4bd19…` (+20, PR #30 merged, PR #13 open); LEFA `0849af70…` -> `27bd6485…` ci success; still HOLD: Vercel aliases, Jennifer production, KasiLink Atlas, Starfall, Cars4Mars physical, DIRISA, Seat 10, skills MAYBE; "Detail: `Schematics/Audits_and_Guardrails/CA_ESTATE_AUDIT_2026-09-07.md` in the isolated tree" | E2 (testimony about local files: E1) |
| Comment 2 by `RobynAwesome` | 2026-09-07T01:38:06Z | - | "Vercel CLI is **logged out**. Serving Git SHAs were not refreshed; 09-06 revisions stay `DATED_CANDIDATE`"; HEAD 200 on Studio, kopanolabs.com + www, fivesarena.com + www, bookit-5s-arena.vercel.app, kasilink.com + www, starfallsalvage.kopanolabs.com, lefa-core-live.vercel.app; "Bookit ids still show `fra1`"; KasiLink `/api/incidents`, `/api/water-alerts`, `/api/gigs` HTTP 500 (6/6); "Receipt: isolated `docs/governance/CA_ESTATE_AUDIT_2026-09-07_VERCEL_HTTP.md`" | E2 (testimony about local files: E1) |
| `master@2b8a58da` tree | - | - | `Schematics/Audits_and_Guardrails/` does not exist; `docs/governance/` contains no `CA_ESTATE_AUDIT*` file; the only in-repo mention of either path is the ledger (`rg -l "CA_ESTATE_AUDIT"` = ledger `.md` and `.json` only) | E2 |
| Ledger `ILR-2026-09-30` | O-16; F-8 (L140-144); C-122-1 POC_PENDING; C-122-2 UNKNOWN | 2026-09-30 | "#122's cited receipt is absent and it is the declared parent audit of eight issues ... keep #122 open as umbrella until an owner-local census exists" | E2 |

**Teach-back:** on 2026-09-07 the owner did the work and wrote it down in a tree this repository never received. The issue is therefore "done" by testimony and "undone" by repository evidence. A cloud renter can replace the cloud half of that testimony with repository evidence; it cannot replace the local half or the Vercel half. This receipt does the first and names the second and third as UNKNOWN.

## 2. GitHub census at default-branch head (box 2)

Method: for each name and each owner, `gh api repos/<owner>/<name>` (metadata), `commits/<default_branch>` (head SHA, committer date), `pulls?state=open` (count), `actions/runs?head_sha=<head>` (all runs **for that exact SHA**; the "latest" column is the first run returned, newest first). A 404 is recorded as `UNKNOWN` in every other column because a private or renamed repository is indistinguishable from an absent one with this token (`UNREADABLE != ABSENT`). Full TSV: `/tmp/estate_census_122.tsv`; all runs per SHA: `/tmp/census_ci_detail.txt`.

### 2.1 `RobynAwesome` rows (the canonical owner per the issue)

| # | Repository | Private | Default | Head SHA (short) | Head date | Open PRs | Latest run at head | All runs at head | Class |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Introduction-to-MCP | false | master | `2b8a58da` | 2026-10-01T01:11:26Z | 1 | KPGS Branch Proof Gate **success** `36799902614` | + Zero-Trust Admission Gate, Kopano Context Production Hardening Deployment, 24-RTC Learning Proof Gate, Kopano CI Pipeline, CodeQL Advanced - all success | E2 |
| 2 | kpgs-morning-engine-core--kmec- | **true** | main | `bf9988ab` | 2026-09-02T01:35:34Z | 0 | KMEC Validation **success** `33580015192` | single run | E2 |
| 3 | Partial-Knowable-Algebra | - | - | - | - | - | - | **HTTP 404** -> UNKNOWN | E4 |
| 4 | ayakha-ai (ring-fenced) | false | main | `a20e6d5c` | 2026-08-26T20:35:03Z | 0 | **NO_RUN** | - | E2 |
| 5 | amaphu-app | false | main | `e1596383` | 2026-08-22T15:24:02Z | 0 | Scaffold CI **success** `32581579983` | single run | E2 |
| 6 | Project-Jennifer | false | main | `cc74b56b` | 2026-09-14T13:49:42Z | 0 | React Persisted Read-through Proof **success** `34851670693` | + CI success, Deploy success; `pushed_at` 2026-09-19T04:46:54Z (non-main push) | E2 |
| 7 | kopano-sovereign-hub | false | main | `f109bf87` | 2026-09-04T12:53:49Z | 0 | Validate Hub **success** `33875118500` | single run | E2 |
| 8 | Kopano-Labs-Website | false | main | `d6e5cc3f` | 2026-09-03T05:05:30Z | 0 | production-gate **success** `33717446307` | single run | E2 |
| 9 | Search-Entity-Architecture | **true** | main | `f67b5718` | 2026-08-28T08:31:38Z | 0 | **NO_RUN** | - | E2 |
| 10 | Kopano-Labs-Interns | false | main | `5773f7e3` | 2026-08-26T10:31:21Z | 0 | **NO_RUN** | - | E2 |
| 11 | cars4mars-project | false | main | `74fa057f` | 2026-08-18T17:42:53Z | 0 | Engineering Evidence Gate **success** `32167070202` | single run | E2 |
| 12 | cars4mars-landingpage | **true** | main | `4169630b` | 2026-08-08T07:30:13Z | 0 | Cars4Mars production gates **failure** `31246311094` | single run; `pushed_at` 2026-08-18T17:28:46Z | E2 |
| 13 | Bookit-5s-Arena | false | main | `c5a4bd19` | 2026-09-06T20:14:03Z | 0 | APU Progressive Sync Proof **success** `34057360954` | + APWA Proof Gate success; `pushed_at` 2026-09-24T09:14:34Z (non-main push); head unchanged since the 09-07 comment | E2 |
| 14 | KasiLink | false | main | `c090e74f` | 2026-09-19T04:35:53Z | 0 | **NO_RUN** | - | E2 |
| 15 | crisis-connect | false | main | `97de0b60` | 2026-08-18T23:48:07Z | 0 | KPGS CrisisConnect Source Gate **success** `32198688789` | single run | E2 |
| 16 | paws-and-potjie | false | main | `e0d6944b` | 2026-08-17T06:17:00Z | 1 | **NO_RUN** | - | E2 |
| 17 | starfall-salvage | false | main | `fc01b643` | 2026-09-08T06:36:14Z | 1 | Dependabot updater `npm_and_yarn in /. for baseline-browser-mapping, esbuild, ...` **failure** `34541350395` | + a second Dependabot updater run failure `34195403085`; **no first-party workflow run at head** | E2 |
| 18 | classroom50 | false | main | `1ca4604c` | 2026-06-18T01:12:23Z | 0 | **NO_RUN** | - (but see 2.2 row for `Kopano-Labs/classroom50`) | E2 |
| 19 | lefa-ai | false | main | `7c4576fb` | 2026-09-14T11:15:58Z | 0 | Dependency Audit **failure** `36422676994` | + Dependency Audit success `35567610236` (earlier run, same SHA), Frontend Quality Gate, ci, Zero-Trust Security Gate, MCP Boundary Verification, Security & Lint Gate - all success. The failing run is the newest of two runs of a workflow on an unchanged SHA, i.e. a scheduled re-run (E3) | E2 / E3 |
| 20 | Harvest-4-All | false | main | `25496595` | 2026-09-21T06:02:12Z | 1 | **NO_RUN** | - | E2 |
| 21 | KPGS-Agent-Mission-Control | false | main | `cef5733b` | 2026-09-03T19:25:06Z | 0 | KPGS WebMCP CI **success** `33796318081` | single run | E2 |
| 22 | kopano-contacts | false | main | `ff1025b6` | 2026-09-02T10:27:03Z | 0 | Kopano Contacts Proof Gate **success** `33619533316` | single run | E2 |

**Totals (RobynAwesome rows, 22 names):** 21 readable, 1 UNKNOWN (404). Of the 21: latest run at head `success` **11**; latest run at head `failure` **3** (rows 12, 17, 19 - with the qualifications in the "All runs" column); **no run at head 7** (rows 4, 9, 10, 14, 16, 18, 20). Open PRs: 4 repositories have exactly 1 (rows 1, 16, 17, 20), the rest 0. Private: 3 (rows 2, 9, 12).

### 2.2 `Kopano-Labs` rows

| Repository | Result | Interpretation | Class |
|---|---|---|---|
| Introduction-to-MCP, KasiLink, starfall-salvage, classroom50, Harvest-4-All | HTTP 200 with **identical** head SHA, head date, open-PR count and `pushed_at` to the `RobynAwesome` row | Consistent with the issue's "same transferred identity" statement for Introduction-to-MCP; for the other four, consistent with a transfer redirect, but redirect-versus-mirror was not probed (E3) | E2 / E3 |
| **classroom50** | at the same head `1ca4604c`, **20 runs of `Collect Scores`, all `failure`**, newest `36702780449`, oldest listed `34457947990` | Run ids span roughly 2026-09-13 to 2026-09-30 on a head dated 2026-06-18: a scheduled workflow failing on every run (E3). Reached only via the `Kopano-Labs` path; the `RobynAwesome` path returned no runs for the same SHA | E2 / E3 |
| **Bookit-5s-Arena** | HTTP 200, **different repository**: head `ae40d1df` 2026-09-28T15:50:45Z, **13 open PRs**, `pushed_at` 2026-09-30T15:32:06Z; runs at head: Dependabot updater js-yaml success `36737320176`, Dependabot updater nodemailer **failure** `36723223149`, Dependabot updater undici success `36617922506`, **`APWA Proof Gate` failure `36446672960`** | The workspace holds two distinct clones (`Kopano-Labs/Bookit-5s-Arena.git` and `RobynAwesome/Bookit-5s-Arena`), so two Bookit repositories exist. The Kopano-Labs one has a first-party gate failing at head. Which is canonical for "Bookit-5s-Arena" in the issue's list is **not stated in the issue** -> owner decision | E2 |
| kpgs-morning-engine-core--kmec-, Partial-Knowable-Algebra, ayakha-ai, amaphu-app, Project-Jennifer, kopano-sovereign-hub, Kopano-Labs-Website, Search-Entity-Architecture, Kopano-Labs-Interns, cars4mars-project, cars4mars-landingpage, crisis-connect, paws-and-potjie, lefa-ai, KPGS-Agent-Mission-Control, kopano-contacts | HTTP 404 | UNKNOWN; not evidence of absence | E4 |

### 2.3 Delta against the 2026-09-06 / 09-07 testimony

| Item | 09-06 / 09-07 said | 2026-10-01 reads | Class |
|---|---|---|---|
| Totals | 14 success / 3 fail / 5 no run | 11 success / 3 fail / 7 no run / 1 UNKNOWN (different method: runs **at head SHA**, so a repository whose only runs are on older commits counts as "no run at head") | E2 |
| Failing heads | Cars4Mars landing, Starfall, Harvest | Cars4Mars landing (unchanged head `4169630b`, same failing gate); Starfall (unchanged head `fc01b643`, Dependabot updater failures only); **Harvest no longer fails** - new head `25496595` (2026-09-21) with no run; **lefa-ai newly fails** on a scheduled Dependency Audit at head `7c4576fb` while `ci` and five other gates pass at that SHA | E2 |
| LEFA | `0849af70…` -> `27bd6485…` ci success | head is now `7c4576fb` (2026-09-14); `ci` still success at head | E2 |
| Bookit main | `9c06ef72…` -> `c5a4bd19…`, PR #13 open | `RobynAwesome` head unchanged `c5a4bd19`, 0 open PRs via API (the "PR #13" of the comment is not open on this repository today); `Kopano-Labs` head `ae40d1df`, 13 open PRs, APWA Proof Gate failing | E2 |
| classroom50 | not mentioned as failing | scheduled `Collect Scores` failing 20/20 on the `Kopano-Labs` path | E2 |
| Kopano-Labs/Bookit `APWA Proof Gate` | not mentioned | failure `36446672960` at head | E2 |

## 3. Public surface probe (cloud part of box 5's HOLD register; **not** box 4)

Method: `curl -sS -o /dev/null -w '%{http_code}' -I --max-time 20 https://<host>/` from this VM; the three KasiLink API routes with `GET`. Exit code 6 = this VM's resolver returned no address. Full table `/tmp/http_probe_122.tsv`.

| Result | Hosts | Class |
|---|---|---|
| **200** (13) | kopanolabs.com, www.kopanolabs.com, context.kopanolabs.com, starfallsalvage.kopanolabs.com, crisisconnect.kopanolabs.com, kasilink.com, www.kasilink.com, kasi-link.vercel.app, fivesarena.com, blog.fivesarena.com, lefa-core-live.vercel.app, kopano-context-studio.vercel.app, starfall-salvage-beryl.vercel.app | E2 |
| **404** (1) | kholofelorababalela.vercel.app | E2 |
| **did not resolve from this VM** (9) | www.context.kopanolabs.com, gsmb.kopanolabs.com, kopanocontext.kopanolabs.com, api.kopanocontext.kopanolabs.com, careers.kopanolabs.com, portfolio.kopanolabs.com, harvest-for-all.kopanolabs.com, bookit.fivesarena.com, capecampass.com | E2 for "no A/AAAA answer from this resolver at 01:40Z"; **E4** for whether a Vercel alias exists |
| **500** (3, GET) | kasilink.com/api/incidents, kasilink.com/api/water-alerts, kasilink.com/api/gigs | E2; consistent with the 09-07 "6/6 500" testimony. Per the hard exclusion, **no inference about KasiLink Atlas health** is drawn |
| **not probed here** | www.fivesarena.com, bookit-5s-arena.vercel.app (both named 200 in the 09-07 comment), Bookit `fra1` region ids, any Vercel deployment id or serving SHA | E4 |

`HTTP_200 != SERVING_SHA_PROVEN`: a 200 says a host answers; it does not say which commit it serves. Box 4 requires Vercel project reads (CLI or API with an owner token) that this VM does not have. `NXDOMAIN_FROM_ONE_RESOLVER != ALIAS_ABSENT`: the nine non-resolving hosts are recorded as observed, not as missing aliases.

## 4. What cannot be done from here (boxes 3 and 4) - UNKNOWN by construction

| Box | Requirement | Why UNKNOWN here | Who can close it |
|---|---|---|---|
| 3 | Local census: exact-clean / exact-dirty / cloud-ahead / diverged / missing for 22 clones | The owner's OneDrive and Playground trees are not mounted in this VM. The `/agent/repos/*` clones in this workspace are **the renter's** checkouts, not the owner's local GSMB, and prove nothing about the owner's machine. The ledger's `LOCAL_GSMB_CONTINUITY_AUDIT_2026-10-01.md` already records this boundary | Owner, on the owner's machine, with the output committed to the repository |
| 4 | Vercel alias vs source SHA re-proven | No Vercel token or CLI session in this VM; the 09-07 comment records the owner's own CLI was logged out. Serving revisions therefore stay `DATED_CANDIDATE` as the owner wrote | Owner with a Vercel login, or a provider-side read filed as a receipt |
| 1 | Isolated tree pinned to re-verified `master` SHA | **Cloud variant satisfied**: this worktree is pinned to `master@2b8a58da` (`git log -1`, `git status --short` clean before writing). The owner's local isolated tree at `c98dc235…` is E1 | Owner, if the local variant is required |
| 6 | Root `NOW.md` handoff only after receipts exist | Receipts now exist on this branch; `NOW.md` POST-SEED is Wave 3, after merge | Wave 3 |

## 5. Hard exclusions - compliance statement

- `Structure/discord_backup_codes.txt`, `Structure/07-Agents`, `.env*`: **not opened** (the only `Structure/` command run was `ls Structure/`, for the #110 receipt).
- Aya / hackathons: not touched.
- DIRISA attendance, Cars4Mars physical state, KasiLink Atlas health, Jennifer production recovery: **no statement made**. The Cars4Mars row is a CI conclusion, not a physical state. The KasiLink 500s are HTTP codes, not a database diagnosis.
- Nested `NOW.md`: none created.
- Alias change, cutover, merge to master, deployment: none. This PR is a Draft against `master` for the owner to merge.
- Stale GUI checkout (`codex/kc-sovereign-gui-full-dev`): not fetched, pulled, merged, reset or pushed (box 7 evidenced for this renter's actions; the owner's local checkout state is E1).
- Jennifer `2220172e…`, Website `beb37f85…`, Bookit fixtures `465d612…`: not promoted, not referenced beyond this line.

## 6. Box-by-box state after this receipt

| Box | Text (abridged) | State | Evidence |
|---|---|---|---|
| 1 | isolated tree pinned to re-verified `master` SHA | DONE (cloud worktree `master@2b8a58da`); local variant E1 | §4 |
| 2 | 22/22 identities, SHAs, open PRs, CI-at-head refreshed | **EVIDENCED** for 21/22 reads + 1 UNKNOWN (PKA 404); both owners probed | §2 |
| 3 | local census | UNKNOWN - owner-gated | §4 |
| 4 | Vercel alias vs source SHA | UNKNOWN - provider-gated | §3, §4 |
| 5 | HOLD register written; snapshots preserved first | **EVIDENCED (cloud)**: this receipt is append-only beside the 09-30 ledger; the 09-06/09-07 numbers are quoted, not overwritten (§1, §2.3). The local snapshots the owner mentioned remain E1 | §2.3, §3 |
| 6 | root `NOW.md` handoff only after receipts | OPEN until Wave 3 | §4 |
| 7 | no push/merge/deploy of the stale GUI checkout | **EVIDENCED** for this renter | §5 |

## 7. Close versus keep (owner decision)

Two admissible readings, offered without preference:

- **(a) Close as superseded.** This receipt plus the #110 and #94 receipts on the same branch replace the cloud half of the 09-07 testimony with repository evidence; boxes 3 and 4 are moved to a new, narrower owner-local issue ("local census + Vercel SHA proof") so that #122 stops carrying work only the owner can do. Ledger F-8's condition ("until an owner-local census exists") would then be satisfied by that new issue, not by #122.
- **(b) Keep as umbrella.** #122 stays open with boxes 2, 5-cloud and 7 checked by reference to this receipt and boxes 3, 4, 6 open, because eight issues name it as parent and a close would orphan those references until each is edited.

Either way the two 09-07 receipt files should either be committed from the owner's isolated tree (preferred: they are the primary record) or be declared local-only in a one-line issue comment so the next renter stops searching `master` for them.

## 8. C.L.E.A.R.

| Axis | Assessment |
|---|---|
| **Complete** | All 22 names probed under both owners (44 reads); every readable row carries SHA, date, PR count and **all** runs at head, not only the latest; every host from the 09-07 comment that was probed is listed, and the two that were not are named; all 7 boxes restated. |
| **Logical** | Totals are stated with their method (runs at head SHA) so the change from "14/3/5" is explained by method and by drift, not blended. Failures are qualified by kind (first-party gate, scheduled audit, Dependabot updater) because they carry different weight. |
| **Evidence** | GitHub reads, run ids, SHAs and HTTP codes are E2 and timestamped to the second. Redirect-versus-mirror and "scheduled" are E3 and labelled. Local census, Vercel SHAs, alias existence behind NXDOMAIN, PKA repository state and the owner's local files are E4 and written as UNKNOWN. |
| **Audience** | Owner (close/keep, Bookit canonical repository, the two un-committed receipts, the new Kopano-Labs Bookit and classroom50 failures); downstream issue owners (#94, #102, #103, #107, #110, #115, #116, #121) who cite #122 as parent; Wave 3 (C-122-1 move). |
| **Relevant** | Bounded to #122. No remediation of any failing workflow is proposed here; those belong to their repositories. |

`CLEAR_PASS != POC_VALIDATED`. This receipt validates that a dated cloud census exists in the repository. It does not validate estate health.

## 9. What this receipt does not claim

- No claim that any of the 22 repositories is healthy, deployed, or serving a particular commit.
- No claim that Partial-Knowable-Algebra does not exist; it is unreadable with this token under both owners.
- No claim about the owner's local clones, the isolated tree at `c98dc235…`, or the two 09-07 receipt files beyond "not on `master`".
- No claim that the nine non-resolving hosts lack Vercel aliases.
- No claim about KasiLink Atlas, Cars4Mars physical state, DIRISA, Jennifer production, or Seat 10.
- No claim about which Bookit repository is canonical.
- No claim that `Kopano-Labs/<name>` 404s mean those repositories were not transferred; only that this token cannot read them.
- No claim that #122 can or should close; §7 gives the owner both readings.

## 10. Decisions requested (owner)

- [ ] Choose §7 (a) close-as-superseded with a new owner-local issue for boxes 3-4, or (b) keep-as-umbrella with boxes 2, 5-cloud, 7 checked by reference to this receipt.
- [ ] Commit the two 2026-09-07 receipt files from the isolated tree to `master`, or state in a #122 comment that they are local-only.
- [ ] Name which Bookit-5s-Arena repository (`RobynAwesome` or `Kopano-Labs`) the 22-list means, so the `APWA Proof Gate` failure at `ae40d1df` is routed to the right lane.
- [ ] Decide whether the `Kopano-Labs/classroom50` scheduled `Collect Scores` failures (20/20) and the lefa-ai scheduled `Dependency Audit` failure are to be tracked in their own repositories or ignored as scheduled noise.
- [ ] Confirm the cloud count method (runs **at head SHA**) is the method future censuses should use, so totals stay comparable.

On merge of this PR, Wave 3 appends: `#122 -> cloud census receipt filed <sha>; 21/22 read, 1 UNKNOWN; boxes 2, 5-cloud, 7 evidenced; 3, 4 owner/provider gated; C-122-1 POC_VALIDATED (cloud subset), C-122-2 UNKNOWN unchanged`. #122 remains open pending the owner's §7 choice.

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
