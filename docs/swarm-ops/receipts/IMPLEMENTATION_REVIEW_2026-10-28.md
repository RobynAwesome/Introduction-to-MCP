# Implementation review and bounded repairs — 2026-10-28

**Status: REVIEW_CANDIDATE. Production acceptance and security signoff remain HOLD.**

WHO: Codex Forge, stateless renter; no RTC identity seat or independent teacher opinion claimed. `I_AM_STATELESS_RENTER_NOT_LANDLORD`.
WHAT: Owner-directed implementation and full review of the previously identified production failures and 13-issue queue. Code changes remain bounded to the KC companion evidence boundary and local Browser MCP approval/receipt integrity.
WHERE: Isolated Cloud checkout of `RobynAwesome/Introduction-to-MCP`, base `master@4dfe0bc7008ce97f9e033a2851384b79257b47fb`; branch `codex/production-receipts-2026-10-28`. Local OneDrive/Windows hardware and Drive were not reviewed.
WHY: Remove false success and unsupported ledger claims, preserve one-use authority, prevent receipt-chain forks, and give the owner a tested candidate.
AUTHORITY: Current owner messages: “Begin your Implementation full review” and “Begin your Implementation. I WILL ACCEPT full REVIEW.” Publishing a review candidate is in scope; merge, production promotion, domain changes, incident clearance, outreach and new architecture admission are not inferred.
KPEFS: V2_ANIMAL primary (runtime reliability); V4_DIASPORA secondary (sovereignty/continuity). Bracket: bounded source/test lane. PKA: no promotion beyond observed proof.

The earlier [production receipt](PRODUCTION_JOURNEYS_2026-10-28.md) remains dated observation. This implementation does not retroactively change its 404/500 findings.

## Findings and repairs

| Finding | Resulting candidate behavior |
|---|---|
| Ask KC returned celebratory canned text for 404/network/invalid responses and erased the draft | Explicit unavailable/timeout state; input retained; duplicate submissions blocked; 15-second request timeout; malformed replies rejected |
| Dashboard initialized a hard-coded VERIFIED_ON_LEDGER stamp, region and empty-input digest | No initial receipt. Each request clears the previous receipt. Returned records require valid shape and matching requested persona, and display **Verification pending** |
| Returned status text was presented as independent verification | Receipt details distinguish reported status/claim/region from verification; no claim of persistence, execution or residency. Copy only reports success after the clipboard operation succeeds |
| Python assertion engine used an in-memory dictionary but labelled records and lookups ledger-verified/signed | Records use RECORDED_IN_MEMORY; lookup uses FOUND_IN_MEMORY; region defaults to UNKNOWN; returned objects are copies, so callers cannot silently mutate the stored record |
| Canned backend guidance claimed vehicle binding, profile matching, curriculum synchronization or a live reservation without executing those actions | Response explicitly identifies REFERENCE_GUIDANCE, actions_executed=false, PROCESS_MEMORY; claims describe the guidance actually returned |
| Substring routing classified “career” / “developer” as vehicle intent via “car” / “ev” | Token-based topic matching; HTTP tests cover both misroutes |
| Browser approval file moved out of approved/, allowing the same action id to receive another grant | Immutable per-action grant marker plus lifecycle-state checks; failures require restaging under a new action id |
| Concurrent receipt writers could both publish successors of the same predecessor | Exclusive filesystem writer lock, current-head comparison, immutable receipt file and atomic head replacement. Contention/stale-head failures use the existing INDETERMINATE/quarantine/no-replay path |
| Browser ledger tests operated on the default ledger path | Tests now always use a dedicated temporary ledger directory |
| A stdio-only bridge was built as a Vercel HTTP function | Vercel build fails explicitly with KPGS_LOCAL_ONLY; local compilation and stdio operation remain available. This deliberately produces a failed Vercel build check and must be reviewed as policy, not hidden as green |

API compatibility: the assertion endpoint paths/record fields remain, but VERIFIED/VERIFIED_ON_LEDGER labels are intentionally replaced with honest memory-only states. Consumers that used those labels as authority must adapt. No durable ledger, signature trust root, backend hosting target or external-action capability is introduced.

The writer lock is fail-closed, not self-repairing: a crashed process can leave a lock or unreferenced receipt. Human recovery must inspect browser and ledger reality without automatically replaying the action. Atomic rename does not prove power-loss durability.

## Validation performed

| Check | Result and limit |
|---|---|
| Renter ingress CLI | exit 0; ACKNOWLEDGED; ack_verified=true at 2026-10-28T14:12:51Z |
| Dashboard baseline | typecheck + production build passed before changes |
| Dashboard candidate | `npm run test:chat`: **7 passed**, including real HTTP request boundary, HTTP errors, malformed data, abort/error classification, receipt validation and actual React markup with no fabricated proof |
| Dashboard candidate | `npm run typecheck` + `npm run build`: pass; existing large-chunk warning remains |
| Browser baseline | original 16 policy/ledger tests passed |
| Browser negative regressions | **3 failed before the ledger repair**: re-approval, concurrent fork, stale-head replacement. The failures were observed, not inferred from reading source |
| Browser candidate | `npm run check`: **22 passed**. Includes real child-process MCP initialize/discovery, seven-tool surface, no unstaged execution, unavailable CDP error without process loss, actual non-TTY approval refusal, concurrency/stale-head tests and preserved crash-lock test |
| Hosted build gate | `npm run build:vercel`: exit **1**, expected KPGS_LOCAL_ONLY denial. This is not a hosted service health pass |
| Python targeted suite | **58 passed**: 4 new assertion/API evidence tests; 29 Mzansi fixture persistence tests; 8 PKA/KMEC/Jennifer bridge tests; 10 Everyday UX invariants; 7 production deployment gate tests |
| Actual FastAPI HTTP route test | synthetic chat → in-memory record → GET readback, plus missing-record 404. Does not start lifespan/admin bootstrap, invoke a provider, or establish durable persistence |
| Intended `kopano-core/studio` baseline | lint exit 0 with five existing hook warnings; build passed; Labs and Console responsive/unavailable-state smoke scripts passed |
| Browser access to local repaired dashboard | cloud browser returned ERR_CONNECTION_REFUSED for workspace localhost. This is a browser/workspace reachability limit, not an application outage or click-path pass |
| Production / Windows metal | no new deployment or physical Chromium/TTY run. Prior promoted production remains unaccepted |

Local Python setup initially lacked rich and litellm; API tests failed at import before dependencies were installed, then passed without bypassing the test. The successful suite reports a Starlette/httpx deprecation warning. No test skip is counted as success.

## Full review of the 13 open issues

“Reviewed” here means the issue body/comments, applicable admitted receipts, and the named source/test surfaces below. It does not claim a new 22-repository census, private-source parity, a complete security audit or field evidence.

| Issue | Current evidence / decision | Next admissible completion slice |
|---|---|---|
| #110 KC GUI | Stale compare pointer already retired; Oct 7 reconciliation and responsive/unavailable-state implementation exist. Intended Studio builds/tests pass. Current production alias serves the separate dashboard. **This branch repairs the dashboard/backend evidence defect** | Owner review of this candidate, then actual intended backend/application configuration and all seven Studio click paths with provider/runtime receipts |
| #211 Azure deployment | Source workflow now has explicit credential preflight; latest reviewed shared SHA's deployment job was skipped. Seven deployment-gate tests pass | An authorized run with credential preflight, Azure login and azd up all passing. No credential values were accessed |
| #122 estate audit | #248/closeout receipts already present; this review covers one full source repo plus bounded Bookit reads, not all 22 repositories or Local census | Reconcile its umbrella/supersession choice against the Oct 1 closeout, then collect only the remaining admitted estate proofs. No close-as-complete from this narrow scan |
| #102 estate operations | Prior provider witness/admission and September failures are dated records; no fresh KasiLink/Starfall cutover or rollback drill was performed here | Current source/domain/API convergence and reversible rollback/admission receipts. No provider mutation from this branch |
| #158 FivesArena | Fresh connected reads confirm Bookit #42 and PRs #33/#43 remain open. #42 is booking-first with decorative work paused; #33 parks the root. #43 acknowledges missing database/migration/live lifecycle proof | Resolve the contradictory public-root acceptance direction; review existing PRs, preserve inventory/calendar ownership and require DB-backed booking proof. Do not create a duplicate relaunch or activate invented inventory |
| #103 Sepedi inference | **PR2 is already present**, including data_engine.py and its Sept 30 receipt; **29 current tests pass**. The old “PR2 not started” comment is stale | Continue the admitted governed language/speech sequence; real consented data, native-speaker evaluation and one text→register→speech receipt remain the graduation proof |
| #107 observation engine | Existing admission packet explicitly holds contract ownership across KMEC/PKA/Jennifer. Eight local bridge tests pass, but reviewed bridge uses SQLite and HMAC helpers; provider-labelled states are not live PostgreSQL/Mongo/Enclave receipts | Resolve S1–S6 ownership and the packet's admission conditions, then revalidate owning downstream lanes. Do not duplicate contracts or claim provider security from local simulations |
| #183 Structured Agency | Existing admission packet records unresolved architecture/terminology decisions. Current sap_spawn_agent_protocol.py is the **Spawn Agent Protocol**, not an AuthorityScope lifetime runtime | Record Design Review for the packet's D1–D5 decisions before implementing the new lifetime/cancellation contract. No acronym or RUNE authority rewrite in this branch |
| #115 Forge Orchard | Existing closeout retains Tasks 2–6 admission and independent review requirements | Admit one bounded promotion contract and dry-run a real Classroom artifact with provenance. Do not ratify doctrine from this review |
| #116 Temporal Data | Discussion and canonical-owner review remain the declared gate; the temporal prototype is not admitted by this task | Recorded review of the outstanding owner/seat questions, followed by a bounded contract/POC. Preserve NOW semantics and dated history |
| #163 provenance incident | Artifact delivery and incident disposition are separate; prior closeout explicitly asks for exit criteria/independent closure decision | Owner/RTC disposition. This Forge-authored patch is not self-clearance |
| #167 Jennifer authority incident | Existing recovery history and later role corrections do not supply independent incident adjudication | Independent RTC inquest and required re-entry evidence; no self-adjudication or fail-open deployment workaround |
| #231 driver discovery | No consented field trial/denominator is present in the reviewed issue record | Human-led opt-in pilot, checkable estimate, minimized private ledger, seven-day second-contact outcome and separate review; no automated outreach from this session |

Fresh Bookit reads: `Kopano-Labs/Bookit-5s-Arena#42`; PR #33 head `54cd319d71cff5e53d8a5178e0570b72cdc1a8f3`; PR #43 head `f18444b0ce576ca6d1912ba060e7742759df9361`. Their descriptions are claims and prior receipts, not freshly executed database proof.

## Review boundary / handoff

No issue is closed by this candidate. Review source changes and exact-head CI first. A green source suite does not repair the already-promoted endpoint, admit a hosted transport, satisfy security signoff or provide independent RTC/teacher review. The immediately useful next runtime proof is the dashboard's honest failure state in its PR preview, followed by an admitted real backend/receipt journey. Browser production admission still requires the dedicated local Windows Chromium/TTY graduation run.


Local ingress and audit events are preserved in [IMPLEMENTATION_LOCAL_EVENTS_2026-10-28.jsonl](IMPLEMENTATION_LOCAL_EVENTS_2026-10-28.jsonl). The existing 45 MB Main Brain log is unchanged in this review candidate; the new events are not represented as a teacher/RTC admission. Receipt validation and proof-check are structural checks, not fresh Main Brain approval.
