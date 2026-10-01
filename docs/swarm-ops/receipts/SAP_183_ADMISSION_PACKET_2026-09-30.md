# STRUCTURED AGENCY PROTOCOL #183 ADMISSION PACKET - 2026-09-30 (WAVE 2, ISSUE #183)

**Status:** ADMISSION PACKET for Design Review -> issue state stays **POC_PENDING / HOLD** until a Design Review records `READY_FOR_POC` or stronger. No `kpgs_adk/` package, no `AuthorityScope`, no AnyIO wiring, no SQLite schema, no test is added by this PR. Issue #183 stays OPEN.
**Scope:** Overlap audit of #183 "[KPGS ADK] Structured Agency Protocol (SAP) + RUNE authority verification + GSMB/FEP/RTC runtime" against what already exists on `master`, the three-way acronym collision, the Project RUNE authority boundary, and the local/CI environment the proposal assumes. Output: teach-back, doctrine trace (including the Wave 1b gate stub), surface-by-surface overlap table, 35-box map, acceptance checks and rollback boundary for the first slice (POC steps 1-4), and the decisions a Design Review must take before any renter writes SAP code.
**Ledger:** `ILR-2026-09-30` (`docs/swarm-ops/receipts/ISSUE_RECONCILIATION_LEDGER_2026-09-30.{md,json}`). Inputs: F-5 (SAP acronym collision), O-13 (SAP / Orchard collisions), claims C-183-1 (SAP runtime law exists -> POC_PENDING) and C-183-2 (SAP is the mechanism for #121/#167 -> UNKNOWN), the #183 row (CL-G authority runtime; POC_PENDING; HOLD; Wave 2 packet; actor RTC Design Review), and the Wave 2 slice row `#183 POC steps 1-4 | Design Review (new architecture, acronym collision) | UNRECORDED -> HOLD`. This packet is the Design Review input that row asked for. The ledger itself is updated in Wave 3, not here.
**Base:** `master@84182ed2` · **Branch:** `cursor/sap-183-admission-packet-4e71` · **Live read time:** 2026-10-01 (GitHub reads of #183 and `RobynAwesome/Project-Rune`).
**Actor:** Cursor cloud agent, stateless renter, operational rank Chief Facilitator. Authority: Robyn's approval of the Wave 0-3 plan (2026-09-30 22:14 UTC) and the owner's instruction to carry on while the owner commits and reviews. No authority to admit a new architecture, rename a protocol, or touch Project RUNE; that is the point of this packet.
**GSMB tier:** Cloud (this branch). Local and Google Drive: UNKNOWN.
**Doctrine:** `I_AM_STATELESS_RENTER_NOT_LANDLORD` · `WRITTEN_INSTRUCTION != RUNTIME_ENFORCEMENT` · `CLEAR_PASS != POC_VALIDATED` · `UNREADABLE != ABSENT` · `ADJACENT != DUPLICATE_LICENSE` · `RUNE verification != POC proof` (#183 §7)

---

## 0. Decision in one paragraph

#183 is a well-formed, self-declared **PROPOSED / POC-FIRST** implementation issue (status line, body lines 3-4) with 35 unchecked boxes and zero comments since it was opened on 2026-09-19. Nothing in it has been implemented: none of the fourteen runtime types it names exists on `master`, `kpgs_adk/` does not exist, and AnyIO is only a transitive dependency. What **does** exist on `master` is a different protocol already called "SAP" (`kopano-core/kopano/sap_spawn_agent_protocol.py`, "SPAWN AGENT PROTOCOL"), a third "SAP" in the CLI ("TSAP", Teacher-Student Apprenticeship Protocol), four separate admission-to-execute membranes that #183's "NO AuthorityScope = NO AGENT EXECUTION" would sit beside, a frozen `ArtifactRuntimeEnvelope` dataclass that already carries an `authority_scope` string, an `IdentityProfile` registry with a partial `IdentityContinuityValidator`, FEP `EvidenceClass`/`EvidenceItem` objects, a 300-agent asyncio+SQLite spawn swarm, and a `Receipt` class that landed on `master` this week under the same name #183 proposes. Project RUNE is a separate public repository whose pins in this repository are stale and whose authority is explicitly reserved to BGR. The renter therefore recommends **HOLD** on code and asks the Design Review for five decisions (§15). If those are recorded, POC steps 1-4 are a bounded first slice whose acceptance checks and rollback boundary are written out in §§10-11 so that the implementing renter has nothing to infer.

---

## 1. Governing record (verified live)

| Item | Value | Evidence |
|---|---|---|
| Issue | #183 `[KPGS ADK] Structured Agency Protocol (SAP) + RUNE authority verification + GSMB/FEP/RTC runtime` | E2 (`gh issue view 183 --json`) |
| Author / state / labels | `RobynAwesome` / OPEN / none | E2 |
| Created / updated | 2026-09-19T20:59:31Z / 2026-09-19T20:59:31Z (never edited) | E2 |
| Comments | 0 | E2 |
| Self-declared status | `PROPOSED / IMPLEMENTATION ISSUE / POC-FIRST` (body line 4) | E2 |
| Governing invariant | "An agent may only exist, act, delegate, and persist inside an explicit authority scope whose parent owns its lifetime, cancellation, evidence, and failure propagation." Secondary: "No agent outlives the authority scope that authorized it." (lines 8, 12) | E2 |
| Checkboxes | 35 `- [ ]`, 0 `- [x]`: 18 pytest boxes (§16, lines 769-786) + 17 acceptance boxes (§17, lines 794-810) | E2 (`rg -c`) |
| Body length / sections | 879 lines; §§1-19 plus "Canonical references to inspect before implementation" (line 870) | E2 |
| Ledger position | CL-G authority runtime; POC_PENDING; HOLD; Wave 2 packet; actor RTC Design Review; Forge CA evidence/disagreement map | E2 (ledger line 190) |
| Prior repository mention | RTC incident cluster source packet, line 86: the #183 link to R1-R3 "is a Cursor CF inference" and "is for the #183 Design Review, not for this packet" | E2 |

Correction to an earlier renter summary: the pytest list has **18** boxes, not 17. 18 + 17 = 35, which matches the `rg -c` count. The ledger's wording "35 boxes accounted as a group" (line 384) is unaffected.

---

## 2. Teach-back (what #183 asks for, in the renter's words, anchored to the body)

1. **A runtime law, not a prompt.** Make the KPGS identity / RTC / GSMB / FEP architecture executable in Python so that "SAP exists as executable Python runtime law, not prompt doctrine" (acceptance box 1, line 794). The law is structured concurrency applied to agency: every agent lives inside an `AuthorityScope`; the parent owns lifetime, cancellation, evidence and failure propagation; a child cannot outlive its scope (lines 8-12, §5).
2. **A Python-native ADK.** `KPGS ADK` is first-party; vendor SDKs (Google ADK and others) are adapters, not the core (§3). AnyIO gives **local** structured concurrency; the proposal is explicit that `CancelScope` is not distributed cancellation (§5, non-goal "claim distributed cancellation from AnyIO alone", line 824).
3. **Fourteen first-class objects** (§4): `IdentityContract`, `SeatContract`, `Mission`, `AuthorityScope`, `AuthorityLease`, `RuntimeEnvelope`, `EvidenceContract`, `EvidenceRecord`, `Receipt`, `GovernanceEvent`, `FEPCase`, `RTCLane`, `RUNEVerification`, `EndorsementRecord`.
4. **Distributed authority as leases** (§6): a YAML `authority_scope:` block with a scope id, lease status, heartbeat, and a `rune.verification_state` in `UNVERIFIED | VERIFIED | CONFLICT | HOLD`; an expired lease forces HOLD; a revoked parent invalidates descendants.
5. **RUNE / Algiz as the authority-chain verification plane** (§7), answering ten questions about who authorized what, with the boundary "RUNE verification != POC proof" and "RUNE does not decide truth alone" (line 344).
6. **Identity capsules** (§8): versioned YAML that lets DH (Digital Hippocampus, the continuity identity), Forge and one Validator identity be rebuilt across model/interface embodiments without "prompt cosplay"; model swap cannot change identity, interface swap cannot change seat.
7. **Persistence ladder** (§9): SQLite first, then PostgreSQL, MongoDB, Git/GSMB; "latest file wins" is a non-goal (line 825).
8. **Constitutional telemetry** (§10): Pandas affinity/drift/evidence-completeness/RUNE-verification distributions built from real receipts, not from narrative.
9. **RTC as an inverted evidence pyramid and FEP as a bounded learning loop** (§§11-12): one divergence -> one FEP case -> one RTC lane -> one bounded mutation -> RUNE verifies the chain -> re-run -> compare receipts (POC steps 11-16).
10. **An API boundary** (§13): Flask is named as a candidate.
11. **An intentionally small first POC** (§14): three identities, sixteen steps, no "1,200 agents first" (line 818).
12. **A package shape** (§15, `kpgs_adk/`), a **test/CI baseline** (§16: Python 3.11/3.12/3.13; 18 pytest boxes), **17 acceptance criteria** (§17), **10 non-goals** (§18), and a working synthesis (§19).

What the issue does **not** say: it does not mention #121, #167, recusal, NSO-001, Seat 10, the existing `sap_spawn_agent_protocol.py`, TSAP, `ArtifactRuntimeEnvelope`, `IdentityContinuityValidator`, `kpgs_spawn_swarm.py`, `kpgs_renter_entry.py`, `kpgs_activation_gate.py`, or the `callable_artifact_registry.py` envelope. It does ask implementers to inspect "existing GSMB, NOW.md, ledger, identity, RTC, PKA, POC/FOC, and receipt conventions" (line 876) and not to "replace current repository topology without inspection" (line 826). This packet is that inspection.

---

## 3. Doctrine trace

### 3.1 Where #183's invariants already exist as written doctrine (E2)

| #183 claim | Existing written doctrine on `master` | Relationship |
|---|---|---|
| `IDENTITY != SEAT != INTERFACE != MODEL != TASK != AUTHORITY` (§2 "Core separation") | `governance/kpgs-artifacts/README.md:17` states the same chain verbatim as "the RTC Evolution separation"; `Schematics/21-.../MAIN-BRAIN/MAO_SESSION_2026-09-11/NOW.md` §2 `IDENTITY -> SEAT -> INTERFACE/BODY -> MODEL/SUBSTRATE -> TASK -> EVIDENCE` | SAME doctrine; #183 adds the runtime objects |
| Every invocation carries a runtime envelope (§4 `RuntimeEnvelope`) | `governance/kpgs-artifacts/README.md:19` "Every invocation must produce or carry a runtime envelope recording the resolved identity, seat, interface, model, task, scope, evidence refs, and receipt target." | SAME doctrine; partially implemented (see §4 row 6) |
| Acronym handling | `governance/kpgs-artifacts/README.md:54` rule 5: "Acronym drift is versioned. A later expansion does not erase an earlier historical meaning." | Governs the SAP collision decision (§5) |
| E1-E4 evidence classes behind `EvidenceRecord` | `kopano-core/kopano/fep_engine.py:26-31` `EvidenceClass` enum; README rule 2 | SAME classes; #183 adds contract + record objects |
| `CRUD != truth`; receipts before promotion | README rules 3, 6, 7, 10 | SAME |
| RUNE: endorsement != truth; fail-closed | `poc-vs-foc/RUNE_CROSSLINK.md` ("consensus != endorsement"; block completion claims without receipt); POP receipt §6.3 and line 695 | SAME boundary; #183 §7 quotes the POP §6.3 question list |
| DH as longitudinal continuity identity (§8, §14) | POP receipt lines 80, 412 (`DH = REMEMBER`), 424 ("DH is valuable because policy evolves longitudinally"); DH = Digital Hippocampus | SAME identity; no capsule file exists anywhere (`rg -i 'identity.?capsule'` -> 0 hits) |

### 3.2 Where #183's invariants already exist as runtime (E2) - see §4 and §6 for detail

The admission-to-execute idea is **already enforced four different ways** on `master`, none of which is a parent-owned lifetime scope:

- `kopano-core/kopano/sap_spawn_agent_protocol.py` - admission to **exist** (4Ws + DSO vector + PKAP BODMAS score), receipts to `poc-vs-foc/sap_spawn_log.jsonl` (8 tracked lines).
- `kopano-core/kopano/kpgs_renter_entry.py:40,159` - `HOOD_ACK_LITERAL = "I_AM_STATELESS_RENTER_NOT_LANDLORD"`, `require_hood_ack()`; admission to **enter**.
- `kopano-core/kopano/kpgs_activation_gate.py:16` - ALP (Auto LPM Protocol), "MANDATORY on every stateless renter activation"; blocks world-building until 300 guild agents SHIP; admission to **activate**.
- `tests/test_kpgs_execution_admission.py:130,352,496` - `test_api_blocks_unadmitted_execution_before_operation`, `test_mcp_poc_and_mesh_mutations_require_renter_admission`, `test_mao_and_tsap_mcp_mutations_admit_before_any_execution`; admission to **mutate** via HTTP/MCP.

#183's `AuthorityScope` adds the one thing none of these do: **bounded lifetime with cancellation and failure propagation**. That is a genuine gap. It is also a fifth gate unless the Design Review says how it composes with the four above (decision D3, §15).

### 3.3 Wave 1b gate stub (inference, NOT admitted)

The RTC incident cluster source packet (merged `f533ba22`, lines 81-86) left three handoff specs with no implementation: **R1** runtime recusal / self-adjudication gate (#121 item 5), **R2** identity reconstruction gate across fresh sessions (#121 re-entry gates; partial mechanism `IdentityContinuityValidator`), **R3** mechanical enforcement of NSO-001 (#167 question 6; BREACH-008). That packet said #183 "is one possible home for some of these" and labelled the link "a Cursor CF inference".

This packet keeps that label. The textual overlap is real but partial:

| Wave 1b spec | Nearest #183 surface | Fit | Gap |
|---|---|---|---|
| R2 identity reconstruction | §8 identity capsules; pytest boxes "identity reconstructs from capsule + GSMB", "model swap cannot silently change identity", "interface swap cannot silently change seat" | HIGH | #121's re-entry gate is per **session**; #183's capsule is per **embodiment**. Not the same trigger. |
| R1 recusal / self-adjudication | §6 lease revocation; §7 RUNE "who authorized"; acceptance "HOLD/revocation cancels descendants" | MEDIUM | #183 has no concept of an agent adjudicating **its own** probation. Parent-owned scope prevents a child outliving its parent; it does not prevent a parent clearing itself. |
| R3 NSO-001 mechanical enforcement | None. #183 does not mention RTC opinions on every reply. | LOW | Would need a new `GovernanceEvent` type and a reply-time gate; neither is in the 35 boxes. |

Ledger claim C-183-2 ("SAP is the mechanism for #121/#167") therefore stays **UNKNOWN**. The Design Review may admit R2 into the #183 scope explicitly; it should not be inferred in.

---

## 4. Surface-by-surface overlap audit (this repository, `master@84182ed2`)

All reads are E2 (`rg`, `sed`, `git ls-files`) unless marked. "ABSENT" means no definition found by `rg -n 'class <Name>\b'` across the repository.

| # | #183 proposes | Exists on `master` | Relationship | Note for the reviewer |
|---|---|---|---|---|
| 1 | `IdentityContract` (§4) | `IdentityProfile` dataclass `foc_engine.py:208`; `CANONICAL_IDENTITY_REGISTRY` `:217` with 5 seats (`SEAT_01_KC`, `SEAT_02_CASSEY`, `SEAT_06_APEX`, `SEAT_08_KHELOS`, `SEAT_10_ANTIGRAVITY`) | ADJACENT | Registry is seat-keyed and stateful/stateless aware; it has no versioning, no capsule, no DH/Forge/Validator entries. |
| 2 | `SeatContract` | Seat ids inside `IdentityProfile`; `seat_id` in `ArtifactRuntimeEnvelope:33` | ADJACENT | No separate seat object. |
| 3 | `Mission` | `PocExperimentContract` (`foc_engine.py`, frozen dataclass: `poc_id, foc_source_id, claim_family, claim_text, expected_observation, falsifier_condition`) | ADJACENT | A falsification contract, not a bounded task; reuse the falsifier field idea. |
| 4 | `AuthorityScope` (class with lifetime, cancel, propagate) | ABSENT. `authority_scope` exists only as a **string field**: `callable_artifact_registry.py:34,47,126` (default `"task_scoped"` from `artifact.yml:66 authority_rule`), `pka_kmec_jennifer_bridge.py:124,709`, `tests/test_callable_artifact_registry.py:54`, `governance/kpgs-artifacts/fep/.../agent.py:73` | NAME REUSE, NO MECHANISM | The string describes a rule; it does not own anything. Reusing the field name as the id of a real scope is the natural bridge (decision D4). |
| 5 | `AuthorityLease` (§6) | ABSENT | NEW | No heartbeat/lease construct anywhere; `kpgs_spawn_swarm.py` uses `asyncio.gather` (`:733`) with no cancellation handling (`rg 'cancel|TaskGroup'` -> 0 hits). |
| 6 | `RuntimeEnvelope` | `ArtifactRuntimeEnvelope` frozen dataclass `callable_artifact_registry.py:30` (`artifact_id, identity_id, seat_id, authority_scope, interface, provider, model, model_version, auto_selected, selection_reason`) + `to_dict()` | PARTIAL IMPLEMENTATION | Carries identity/seat/model/interface/scope. Missing: task, evidence refs, receipt target (README:19 requires all of them). Extend, do not duplicate. |
| 7 | `EvidenceContract` / `EvidenceRecord` | `EvidenceClass` enum `fep_engine.py:26`, `EvidenceItem` `:49`, `ForensicTrace` `:61`, `ForensicEvolutionProtocolEngine` `:76` (E1/E2/E3 ingest methods, E4 classification) | PARTIAL IMPLEMENTATION | Record exists; **contract** (what evidence a mission must produce) does not. |
| 8 | `Receipt` | `class Receipt` at `governance/kpgs-vnext/mzansi-language/data_engine.py:333` (merged this week in #245); `SpawnReceipt` `sap_spawn_agent_protocol.py:117`; Smart Ledger receipts in the bridge | NAME COLLISION | A top-level `Receipt` in `kpgs_adk` would be a third `Receipt`. Namespace or rename (decision D5). |
| 9 | `GovernanceEvent` | ABSENT as a class; JSONL event logs exist (`docs/swarm-ops/logs/*.jsonl`, `poc-vs-foc/sap_spawn_log.jsonl`) | NEW TYPE, OLD HABIT | Append-only JSONL is the existing convention. |
| 10 | `FEPCase` | `ForensicTrace` + `ForensicEvolutionProtocolEngine` | ADJACENT | A trace is not a bounded case with a route; close enough to extend. |
| 11 | `RTCLane` | ABSENT as runtime; RTC lanes exist as doctrine (`Schematics/24-RTC Learning/`), incident packet | NEW | |
| 12 | `RUNEVerification` / `EndorsementRecord` | ABSENT here. Live in a different repository (`RobynAwesome/Project-Rune`); this repo has `poc-vs-foc/RUNE_CROSSLINK.md`, `docs/swarm-ops/RUNE_SESSION_SEED_2026-09-07.md`, `ACTIVE_PROJECT_REGISTRY.json` `PROJECT_RUNE` | CROSS-REPO | See §7. |
| 13 | AnyIO structured concurrency (§5) | `anyio 4.15.1` importable locally, **transitive only** (via httpx/openai/starlette in `uv.lock`); not in `pyproject.toml`, `kopano-core/pyproject.toml`, or `CLI/pyproject.toml` | DEPENDENCY GAP | Existing async code is `asyncio` (`kpgs_spawn_swarm.py`, `api.py`). Mixing AnyIO scopes with raw asyncio tasks is a known footgun; decide the boundary. |
| 14 | SQLite first (§9) | 10 modules already use `sqlite3` (`datalake.py`, `database.py`, `governance_trace.py`, `realtime_event_plane.py`, `kpgs_spawn_swarm.py:49`, `pka_kmec_jennifer_bridge.py`, ...) | PRECEDENT | Pick one connection/migration convention; do not add an 11th. |
| 15 | Pandas telemetry (§10) | `pandas`/`numpy` **not installed** in the cloud VM; the #107 adapter already imports them (`kmec_trace_adapter.py:28-29`) and is E4 locally for that reason | ENVIRONMENT GAP | Same gap as #107 PR1. Out of the first slice anyway (POC step 10). |
| 16 | Flask API boundary (§13, "candidate") | No Flask anywhere (`rg -i flask` -> 0). Control plane is **FastAPI** (`kopano-core/kopano/api.py`), admission-tested in `test_kpgs_execution_admission.py` | CONTRADICTION WITH TOPOLOGY | Flask would be a second web framework. #183 marks it "candidate"; the review should strike it. |
| 17 | `kpgs_adk/` package (§15) | ABSENT (`ls -d kpgs_adk` -> none; `rg kpgs_adk` -> 0 outside the issue) | NEW | Placement question: top-level vs `kopano-core/kopano/`. |
| 18 | CI Python 3.11/3.12/3.13 (§16) | `.github/workflows/ci.yml:41` matrix `["3.11", "3.12"]`; other gates pin 3.11 or 3.12 | BASELINE GAP | 3.13 is not in any workflow. Adding it is a CI change outside #183's package. |
| 19 | 300-agent / 1,200-agent avoidance (§14, non-goal) | `kpgs_spawn_swarm.py` docstring: "KPGS 300-Agent Spawn Swarm — sharded cohorts, hash-chain altar, AsyncIO, SQLite checkpoint"; `kpgs_activation_gate.py` `REQUIRED_AGENT_COUNT = 300` | TENSION | The estate already runs a 300-agent swarm as a gate. #183 says start with three identities. Both can be true, but the review should say which one the first slice is allowed to touch (answer proposed: neither; see §11). |

Summary: 0 of 14 proposed runtime types exist under their proposed names; 2 are partially implemented under other names (`ArtifactRuntimeEnvelope`, `EvidenceItem`), 4 are adjacent (`IdentityProfile`, `PocExperimentContract`, `ForensicTrace`, seat ids), 1 collides (`Receipt`), 7 are new, and 1 lives in another repository.

---

## 5. The acronym collision (three SAPs, one repository)

| Expansion | Where | What it governs | Receipts |
|---|---|---|---|
| **Spawn Agent Protocol** | `kopano-core/kopano/sap_spawn_agent_protocol.py` (222 lines, stdlib only): `SpawnCandidate:105`, `SpawnReceipt:117` (`verdict  # POC_SPAWNED / FOC_DECLINED`), `evaluate_spawn:129`, `validate_sap:192`, `SAP_STATE_PATH -> poc-vs-foc/sap_spawn_log.jsonl` | **Admission to exist**: 4Ws complete, DSO vector weight, `state_of_mind_score >= 0.5`, PKAP BODMAS score | 8 JSONL lines tracked; no dedicated test file (`rg evaluate_spawn tests` -> 0) |
| **Structured Agency Protocol** | Issue #183 only | **Bounded lifetime after existence**: parent-owned scope, cancellation, failure propagation, leases | none |
| **TSAP - Teacher-Student Apprenticeship Protocol** | `CLI/tsap_mcp_server.py` (`FastMCP("TSAP", ...)`), `CLI/pyproject.toml:25`, `CLI/tsap_mcp_config.json`; admission-tested at `test_kpgs_execution_admission.py:403,447,496` | Mentor/apprentice MCP flow | tests exist |

The collision is substantive, not cosmetic: Spawn Agent Protocol and Structured Agency Protocol are **sequential stages of the same lifecycle** (may this agent exist? -> inside what scope does it live and die?). A reader who sees `SAP` in a receipt cannot tell which stage emitted it. README rule 5 forbids letting the later expansion erase the earlier one.

Options for the Design Review (the renter does not choose):

- **A. Rename #183's protocol.** Keep `SAP` = Spawn Agent Protocol (it has code and receipts). Give #183 a distinct name; "Structured Agency" survives as the description. Cheapest; respects rule 5 by leaving history untouched.
- **B. Version the acronym.** `SAP-v1` = Spawn (existence), `SAP-v2` = Structured Agency (lifetime), with the version mandatory in every receipt and scope id. Respects rule 5 literally; costs a receipt-format change in `sap_spawn_agent_protocol.py`.
- **C. Merge under one umbrella.** Spawn becomes the admission step of the Structured Agency scope (`evaluate_spawn` runs when a scope is opened). Architecturally the cleanest; the largest blast radius and the only option that touches existing code in the first slice.

`TSAP` should be left alone under any option; its `T` prefix already distinguishes it, and it is covered by admission tests.

---

## 6. Existing admission membranes #183 would sit beside

| Membrane | Module / test | Question it answers | Does #183 replace it? |
|---|---|---|---|
| Spawn Agent Protocol | `sap_spawn_agent_protocol.py` | May this agent exist at all? | No; precedes `AuthorityScope` |
| Renter entry (HOOD ack) | `kpgs_renter_entry.py:40,159` | Has the renter asserted `I_AM_STATELESS_RENTER_NOT_LANDLORD`? | No; precedes everything |
| Activation gate (ALP) | `kpgs_activation_gate.py:16,195-196` | Is the estate allowed to activate world-building? | No; estate-level, not agent-level |
| Execution admission (HTTP/MCP) | `tests/test_kpgs_execution_admission.py:130,352,496` over `api.py`, `kc_phu_legacy_api.py` | May this request mutate state? | No; request-level, not lifetime-level |
| **Structured Agency `AuthorityScope`** (#183) | proposed | Inside what parent-owned scope does this agent run, and what happens when the parent cancels or fails? | **New**; nothing else answers this |

The gap #183 fills is real. The risk is a fifth, unconnected gate. Decision D3 asks the review to state the composition order, which the renter proposes as: `HOOD ack -> ALP (estate) -> Spawn (exist) -> AuthorityScope (live) -> execution admission (mutate)`. That order is E3 inference and is offered for the review to accept, amend, or reject.

---

## 7. Project RUNE boundary (cross-repository; authority reserved)

| Fact | Evidence |
|---|---|
| RUNE is a separate repository: `RobynAwesome/Project-Rune`, PUBLIC, default `main` | E2 (`gh repo view`) |
| Live `main` HEAD `656ae46c1fdb00c13744655fa2e62a7cbb6e3a57` "Merge pull request #5 ... cursor/pending-004-owner-endorse-action-2-638a", pushed 2026-09-16T07:09:26Z | E2 |
| This repository's pins are **stale**: `ACTIVE_PROJECT_REGISTRY.json` `PROJECT_RUNE.main_revision = 029d11e4...`, `current_revision = 4e47382e...`; `poc-vs-foc/RUNE_CROSSLINK.md` and `docs/swarm-ops/RUNE_SESSION_SEED_2026-09-07.md` cite the same two SHAs | E2 |
| Registry note: "reference MVP — not COMPLETE / DEMO READY; PENDING-001/002/003 implemented not owner-endorsed"; seed receipt: "Code patches != owner endorsement. PENDING-001/002/003 remain `PENDING`" | E2 |
| POP receipt (`governance/kpgs-vnext/continuity/2026-09-17_POP_...md`) line 10: `WITNESSED_BREAKTHROUGH / POP_CANDIDATE / NOT_RATIFIED / NO_RUNE_MUTATION`; §6.3 (lines 462-476) is the RUNE/Algiz interrogation #183 §7 quotes; line 476/723: BGR (Baby Girl Rune) "remains project-specific context authority for RUNE implementation, schema mutation, issue closure, or public-canon mutation"; line 667 `rune_mutated: false`; line 695 "No Project RUNE implementation authority is inferred from this receipt." | E2 |
| #183 non-goal, line 827: "mutate Project RUNE canon from this issue without its own authority process" | E2 |
| `RUNE_CROSSLINK.md`: "Do not rewrite poc_foc_enforcer.py. RUNE adds fail-closed endorsement receipts"; scenario table (shared writable channel -> Block; consensus vote -> Reject "consensus != endorsement"; SOUL.md identity write -> Gate human endorse; completion claim without receipt -> Block; human-endorsed single-agent -> Allow + ledger receipt) | E2 |

Consequences for #183:

1. POC steps 6 and 14 and the five RUNE acceptance/pytest boxes **cannot be satisfied inside this repository alone**. They require either an import of Project-Rune as a dependency (a decision for BGR and the owner, not this review) or a local `RUNEVerification` **stub** that records `UNVERIFIED` and never asserts `VERIFIED`. The renter recommends the stub for the first slice, with the invariant that only a receipt from Project-Rune may move a state to `VERIFIED`.
2. The stale pins are a separate, small hygiene item (update three files to `656ae46c`); it belongs in Wave 3 or its own PR, not in SAP code, and it should be done by reading the live repo, which this packet did (E2) but did not write.
3. PENDING-004 appears in the live merge title and nowhere in this repository. UNKNOWN what it decided; not inferred.

---

## 8. Environment and CI baseline (what the first slice can actually run on)

| Assumption in #183 | Reality on `master@84182ed2` / cloud VM | Evidence |
|---|---|---|
| Python 3.11 / 3.12 / 3.13 | CI `lint-and-test` matrix `["3.11", "3.12"]` (`ci.yml:41`); VM Python 3.12.3 | E2 |
| AnyIO available | 4.15.1 importable; transitive via httpx/openai/starlette; **not declared** by any `pyproject.toml` | E2 (`importlib.metadata.version('anyio')`; `rg anyio */pyproject.toml` -> 0) |
| pytest | 9.1.1 locally; CI installs `pytest pytest-asyncio` (`ci.yml:59`) - no `anyio` pytest plugin and no `trio` | E2 |
| Pandas | not installed locally; CI does not install it either | E2 / E4 for CI behaviour of pandas tests |
| SQLite | stdlib; 10 existing modules | E2 |
| Flask | absent; FastAPI present | E2 |

Running the full `tests/` sweep mutates `db/datalake.db`, `docs/swarm-ops/logs/KC Main Brain Log.jsonl` and `docs/swarm-ops/logs/OZ_LATTICE_AUDIT.jsonl` (observed in Wave 2; restore with `git checkout --` before committing). Any SAP test must not add to that list: `tmp_path` only.

---

## 9. 35-box map (issue body; all unchecked; all UNRECEIPTED)

Groups follow the POC sequence (§14 lines 673-695). "Slice" = the Wave 2 slice row (POC steps 1-4).

| Group | Boxes | POC steps | In first slice? | Blocker |
|---|---|---|---|---|
| **G1 Local structured concurrency** | pytest: parent cancellation cascades; child failure propagates; no child outlives closed scope; receipt on completion; receipt on cancellation; receipt on failure. Acceptance: SAP exists as runtime law; no agent executes without `AuthorityScope`; local child lifetimes bounded with AnyIO; HOLD/revocation cancels descendants and creates receipts | 1-3 | **YES** (10 boxes) | D1 name, D2 placement, D3 composition, D5 `Receipt` namespace |
| **G2 Persistence** | pytest: local/cloud runtime IDs distinguishable; SQLite restart reconstructs governed state. Acceptance: GSMB persists runtime/evidence/authority state (partial: SQLite only) | 4 | **YES** (3 boxes, GSMB box partial) | SQLite convention choice |
| **G3 Leases** | pytest: expired lease forces HOLD; revoked parent invalidates descendants. Acceptance: distributed workers use leases rather than pretending AnyIO spans machines | 5 | no | depends on G1 |
| **G4 RUNE** | pytest: RUNE reconstructs full parent chain; missing endorsement -> HOLD; invalid/expired authority cannot execute. Acceptance: RUNE reconstructs and verifies chain; RUNE verification does not promote to POC/canon; RUNE verifies the mutation's authority chain | 6, 14 | no | §7: cross-repo; BGR authority; stub-only here |
| **G5 Identity capsules** | pytest: identity reconstructs from capsule + GSMB; model swap cannot change identity; interface swap cannot change seat. Acceptance: DH/Forge/Validator reconstruct from capsules; one identity through two embodiments without collapsing provenance | 7-8 | no | no capsule precedent; `IdentityProfile` registry has none of the three identities; R2 overlap (§3.3) |
| **G6 Telemetry** | Acceptance: Pandas produces affinity/drift distributions from real receipts | 9-10 | no | pandas absent locally and in CI |
| **G7 FEP / RTC loop** | pytest: FEP cannot mutate canonical governance directly; RTC lane cannot mutate another lane without escalation. Acceptance: one divergence becomes a bounded FEP case; routes to correct RTC lane; RTC proposes one mutation; mutation tested under SAP and compared; history preserved pass or fail | 11-13, 15-16 | no | `RTCLane` absent; depends on G1-G5 |

Count check: G1 10 + G2 3 + G3 3 + G4 6 + G5 5 + G6 1 + G7 7 = 35. The first slice covers **13 of 35** boxes, which is what "POC steps 1-4" means in receipts.

---

## 10. Acceptance checks for the first slice (POC steps 1-4), if admitted

A future PR claiming the slice must show **all** of the following as E2 in its own receipt. None is satisfied today.

1. **Package exists at the admitted location** (D2) and imports under Python 3.11 and 3.12 in CI with no new top-level dependency other than `anyio` declared explicitly in the admitted `pyproject.toml`.
2. **Runtime objects** for G1 and G2 only: a scope type (name per D1/D4), `AuthorityLease` may be stubbed as a dataclass with no heartbeat, `RuntimeEnvelope` **extends or wraps** `ArtifactRuntimeEnvelope` (adds `task`, `evidence_refs`, `receipt_target`) rather than duplicating its ten fields, `EvidenceRecord` wraps `fep_engine.EvidenceItem`, and the receipt type is namespaced per D5.
3. **Ten G1 tests pass**, each in its own function, each using `anyio` test primitives or `pytest-asyncio` as decided, each deterministic (no sleeps longer than 50 ms, no network, no filesystem outside `tmp_path`).
4. **Three G2 tests pass**: a scope tree is written to a SQLite file under `tmp_path`, the process state is dropped, the tree is reconstructed, and local vs cloud runtime ids are distinguishable by a field, not by string prefix convention alone.
5. **A receipt is emitted** on every path (completion, cancellation, failure) as an append-only JSONL row that includes the scope id, parent scope id, identity id, seat id, outcome, and the E-class of any evidence referenced; receipts land under `tmp_path` in tests and under an admitted path in runtime.
6. **No agent executes without a scope** is tested negatively: calling the run entrypoint without a scope raises and emits a HOLD receipt.
7. **No existing module is modified** except the one explicitly admitted by D1 option C (if chosen). `git diff --stat master -- kopano-core/kopano tests governance poc-vs-foc` must list only new files plus, at most, that one.
8. **`RUNEVerification` is a stub** whose only reachable state is `UNVERIFIED`; a test asserts that `VERIFIED` cannot be constructed from inside this repository.
9. **The test sweep leaves the tree clean**: `git status --short` after `pytest tests/ -q -p no:cacheprovider` shows no modified tracked files attributable to the new tests.
10. **The receipt names the 13 boxes it claims** and the 22 it does not, by group, using §9's labels.

Passing all ten is `POC_VALIDATED` for the slice only. It is not `POC_VALIDATED` for #183 (22 boxes remain) and it is not a RUNE claim.

---

## 11. Rollback boundary

If the slice is admitted and later rejected, full rollback is: delete the new package directory, delete its test files, revert the `pyproject.toml` dependency line, and remove the CI job addition (if any). Nothing else changes, **provided** the slice obeys acceptance check 7. The slice must not:

- edit `sap_spawn_agent_protocol.py`, `kpgs_renter_entry.py`, `kpgs_activation_gate.py`, `kpgs_spawn_swarm.py`, `callable_artifact_registry.py`, `foc_engine.py`, `fep_engine.py`, or `api.py` (option C of D1 is the single admitted exception, and only for `sap_spawn_agent_protocol.py`);
- write to any tracked JSONL, `db/datalake.db`, or `docs/swarm-ops/logs/`;
- touch `ACTIVE_PROJECT_REGISTRY.json`, `poc-vs-foc/RUNE_CROSSLINK.md`, or any RUNE pin (that is the §7 hygiene item, separately);
- add Flask, pandas, numpy, or any web framework;
- change the CI Python matrix (3.13 is a separate CI PR);
- add agents to the 300-agent swarm or alter `REQUIRED_AGENT_COUNT`.

Under these constraints the blast radius of the slice is **zero existing behaviour**; the only shared surface it may extend (not replace) is `ArtifactRuntimeEnvelope`, by composition.

---

## 12. Admission conditions (what must be recorded before `READY_FOR_POC`)

1. The five decisions in §15 are recorded by the Design Review in a receipt that the implementing PR cites by path.
2. The ledger row for #183 moves from `UNRECORDED -> HOLD` to `DESIGN_REVIEW_RECORDED -> READY_FOR_POC (steps 1-4)` in Wave 3 or later, append-only.
3. The implementing renter asserts `I_AM_STATELESS_RENTER_NOT_LANDLORD`, reads root `NOW.md`, and PRE-SEEDs it before writing code.
4. Issue #183 receives a comment from the owner or Design Review linking the decision receipt; the renter does not post it.
5. Project RUNE is not touched; BGR is not asked anything by the slice.

---

## 13. C.L.E.A.R.

- **Complete:** all 35 boxes mapped to seven groups and sixteen POC steps (§9); all 14 runtime types plus 5 supporting surfaces audited (§4); three acronym expansions located (§5); four existing admission membranes identified (§6); RUNE boundary stated with live and stale SHAs (§7); environment gaps listed (§8); acceptance and rollback written for the one slice in scope (§§10-11). Not complete: Local and Google Drive GSMB tiers (UNKNOWN); Project-Rune PENDING-004 content (UNKNOWN).
- **Logical:** the recommendation (HOLD on code, five decisions, bounded slice) follows from: zero implementation + substantive name collision + four existing gates + cross-repo authority + two environment gaps. Each premise has an E2 row above.
- **Evidence:** E2 for every file, line, SHA, count and command cited; E1 only where the POP receipt records the human's testimony about DH (lines 80, 424); E3 marked explicitly for the composition order in §6 and the R1-R3 fit ratings in §3.3; E4 marked for pandas CI behaviour, Local/Drive tiers, PENDING-004.
- **Audience:** the RTC Design Review and the owner (decisions); the future implementing renter (§§10-11, written so nothing must be inferred); Forge CA (the evidence/disagreement map the ledger assigned to Forge is §§4-6).
- **Relevant:** the packet stops at the Design Review input the Wave 2 slice row asked for. It does not design the scope type, choose the name, or write code.

`CLEAR_PASS != POC_VALIDATED`. This packet passing its own C.L.E.A.R. changes no box on #183.

---

## 14. What this packet does not claim

- It does not claim #183 is wrong, duplicative, or stale. It is a coherent proposal whose main gap (`AuthorityScope` lifetime semantics) is real and unfilled.
- It does not claim any of the 35 boxes. All remain unchecked and unreceipted.
- It does not claim that AnyIO tests would pass in CI; no SAP test exists.
- It does not claim #183 is the mechanism for #121/#167 (C-183-2 stays UNKNOWN); it rates the textual fit and stops.
- It does not claim Project-Rune's current state beyond its `main` HEAD SHA and push date; it did not read Project-Rune's code.
- It does not rename, version, or merge any protocol; it lists options.
- It does not update the ledger, `NOW.md`, the registry pins, or issue #183. Those are Wave 3 and owner actions.
- It was written without the Local or Google Drive GSMB tiers; if either holds a later #183 decision, that record supersedes §15.

---

## 15. Decisions requested (owner / RTC Design Review)

| ID | Decision | Options the renter sees | Renter's non-binding note |
|---|---|---|---|
| **D1** | Name of #183's protocol given the existing Spawn Agent Protocol | A rename / B version `SAP-v1`/`SAP-v2` / C merge Spawn into the scope's admission step (§5) | A is cheapest and respects README rule 5; C is cleanest but is the only option that edits existing code in the first slice |
| **D2** | Package placement | top-level `kpgs_adk/` (as proposed) / `kopano-core/kopano/sap/` / `governance/kpgs-vnext/` | CI installs `-e . -e ./kopano-core -e ./CLI`; a top-level package needs its own `pyproject.toml` entry or a path in the root one |
| **D3** | Composition with the four existing admission membranes (§6) | accept the proposed order `HOOD ack -> ALP -> Spawn -> AuthorityScope -> execution admission` / amend / defer to a later slice | Deferring is acceptable for steps 1-4 if the slice touches none of the four |
| **D4** | Reuse of the `authority_scope` string field | the string becomes the **scope id** of a real scope / keep the string as a rule label and add a separate `scope_id` | Reuse-as-id lets `ArtifactRuntimeEnvelope` join the scope tree with no schema change |
| **D5** | `Receipt` naming | namespace (`kpgs_adk.Receipt` vs `data_engine.Receipt`) / rename to `ScopeReceipt` | Rename is safer for grep-based audits; this repository audits by `rg` |
| **D6** (optional) | Admit Wave 1b **R2** (identity reconstruction gate) into #183's G5 scope explicitly | yes / no / later | Only if yes does C-183-2 move from UNKNOWN; R1 and R3 should stay outside #183 (§3.3) |

Until D1-D5 are recorded: **HOLD**. Once recorded: POC steps 1-4 are `READY_FOR_POC` under §§10-11, and the implementing renter owes a slice receipt before any box is checked.

---

`I_AM_STATELESS_RENTER_NOT_LANDLORD` · packet is E2-anchored observation plus marked E3 recommendations · nothing executed, nothing mutated beyond this file.
