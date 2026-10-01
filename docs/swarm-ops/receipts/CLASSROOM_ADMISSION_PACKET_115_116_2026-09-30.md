# CLASSROOM ADMISSION PACKET - ISSUES #115 AND #116 - 2026-09-30 (WAVE 2, SLICE 1)

**Status:** ADMISSION / SOURCE PACKET. No code, schema, workflow, engine, `PROMOTION_PROTOCOL.md`, Classroom folder, `NOW.md` edit or dry-run was produced. The two issues stay open; neither is closed, re-scoped or re-assigned by this file.
**Scope:** #115 (Forge Orchard Protocol: Classroom promotion, consumer admission and export receipts) Task 1 executed as a cloud-head observation; #115 Tasks 2-6 and #116 (Temporal Data / Temporal Manhole) prepared for RTC admission only.
**Workflow:** #115 -> RTC Classroom / Round Table (governance vocabulary). #116 -> RTC independent positions (`RTC_DISCUSSION`). Both routes attested by the Forge CA -> Cursor CF brief (2026-09-30) and by ledger rows ILR L333-L335.
**Decision state recorded here:** `LEARN` for #115 Tasks 2-6, `LEARN / HOLD` for #116. Nothing in this packet is `TEST` or `READY_FOR_POC`.
**Ledger:** `ILR-2026-09-30` (`docs/swarm-ops/receipts/ISSUE_RECONCILIATION_LEDGER_2026-09-30.{md,json}`, merged in PR #240). Rows cited: #115 L183, #116 L184, C-115-1 L213, C-115-2 L214, C-116-1 L215, `PROMOTION_PROTOCOL.md` absence L304, admission rows L333-L335.
**Base:** `master@4a316bbb1c2c237a0ecc3569642dd146c8c13536` (after PR #241). Wave 0 base was `1e152dce`; no cited path changed between the two. **Live reads:** 2026-09-30T23:20Z to 2026-10-01T00:00Z.
**Actor:** Cursor cloud agent (model: Claude via Cursor; interface: Cursor Cloud Agent; actor: stateless renter; operational rank: Chief Facilitator - an operational rank, not an RTC identity seat). Authority: Robyn's approval of the Wave 0-3 plan (2026-09-30 22:14 UTC) and "carry on your work" (2026-09-30). This packet needs no RTC admission to exist; the work it prepares does.
**GSMB tier:** Cloud (this file once merged). Local: the Classroom Phase 1 structure named in Interns #12 is testimony only (E1), see F-W2-10. Google Drive: UNKNOWN.
**Mission line (Legacy.md L30):** "convert local context into validated human capability, economic participation and capability multiplication." This slice serves it by making the promotion path *auditable* before anything is promoted; it does not itself multiply capability.
**Doctrine:** `I_AM_STATELESS_RENTER_NOT_LANDLORD` · `WRITTEN_INSTRUCTION != RUNTIME_ENFORCEMENT` · `CLEAR_PASS != POC_VALIDATED` · `FAILURE_SURFACED_BY_CALL != FAILURE_CAUSED_BY_CHANGE` · `MODEL_AGREEMENT != REALITY_EVIDENCE`

Evidence classes used below: **E1** testimony (issue text, chat, local-only claims) · **E2** repository artifact at the cited revision · **E3** inference from E2 · **E4** unknown.

---

## 1. Purpose and limits

#115 Task 1 asks for an audit of "every existing path that can appear to promote learning or proposals" and an overlap table in the issue's own format. That is observation, not governance; ledger row C-115-1 tagged it `POC_PENDING` and admission row L333 recorded "none (cloud-head observation)". Section 3 performs it.

#115 Tasks 2-6 create vocabulary (artifact classification, epistemic states, consumer admission states), a human-readable contract, a machine-readable receipt schema, consumer gates, a dry-run and a Forge compression receipt. Ledger row C-115-2 tagged them `HOLD_HUMAN`: the Forge Orchard Protocol is not ratified and `PROMOTION_PROTOCOL.md` does not exist at any cloud ref. Under the approved plan no code or schema is written before an RTC admission of `READY_FOR_POC` or stronger. Sections 4, 5, 9 prepare that admission.

#116 declares its own required next state `RTC_DISCUSSION` and says "Do not create a new duplicate authority graph before this audit." Section 6 performs the GSMB owner audit it asks for and maps its fifteen questions to evidence locations and decision holders, without answering them.

What this packet cannot do: it cannot see the local Windows checkout, Google Drive, the remote head of `RobynAwesome/Kopano-Labs-Interns`, or `Structure/07-Agents/` (not opened, by constraint). Each such gap is marked E4.

---

## 2. Execution preflight record

| Gate | Result | Note |
|---|---|---|
| Prompting Protocols | resolved | operator directive = approved plan Wave 2 slice 1; scope = packet only |
| Renter ingress | asserted | `I_AM_STATELESS_RENTER_NOT_LANDLORD`; actor recorded in header |
| Refresh observations | done | `git fetch origin master` -> `4a316bbb`; issue list = 16 open; #115/#116 `updatedAt 2026-09-07T00:42Z`, unchanged since Wave 0 |
| KPEFS routing | primary = documentation receipt; secondary = none | no engine, CI or settings vector touched |
| Bracket / BlackMask containment | lane = observation + admission preparation | `UNKNOWN` and `HOLD` preserved, not resolved |
| PKA verdict | `PROPOSE` for Task 1 output; `HOLD` for Tasks 2-6 and #116 | tags are the proposed working tags from ILR, not admitted canon |
| Execution membrane | one new file, one branch, draft PR | no `Closes` line |
| C.L.E.A.R. | run in section 7 | `CLEAR_PASS != POC_VALIDATED` |
| Receipt | this file + PR head SHA (recorded by the PR, not here) | |

---

## 3. #115 Task 1 - overlap audit of promotion surfaces (cloud head)

Format as required by the issue: `concept | current owner | current evidence | gap | keep/extend/do-not-duplicate`. "Owner" means the surface that currently governs or implements the concept at `4a316bbb`, not a person.

| # | Concept | Current owner | Current evidence | Gap | Decision |
|---|---|---|---|---|---|
| 1 | Artifact classification `ORIGIN/SESSION/CURRICULUM/POC/RECEIPT/ARCHIVE` | none on cloud | E4 at cloud; E1 only (issue #115 text, Interns #12 local Phase 1 structure) | no cloud artifact carries any of these labels | **do-not-create** until RTC admits the vocabulary (Task 2) |
| 2 | Epistemic state vocabulary | `kopano-core/kopano/possibility_to_proof_engine.py` `EpistemicTruthState` (`KNOWN_POC` L33, `FAKE_OF_CONCEPT_FOC` L37, others) | E2 | #115 proposes 8 states (`UNKNOWN ... HOLD`) that do not match the engine's enum; no mapping exists | **keep** engine enum; **extend** by a mapping table only after RTC; do not fork a second enum |
| 3 | Promotion policy | `governance/kpgs-vnext/evaluation/promotion-policy.json` (`kpgs.promotion-policy.v1`: min aggregate 0.9, human approval for high/critical, "tied to exact commit", rollback target) | E2 | whether any code reads this file is UNKNOWN (E4); no Classroom consumer references it | **keep / reuse**; Task 2 must cite it, not restate it |
| 4 | Human-readable promotion protocol | `Schematics/24-RTC Learning/PROMOTION_PROTOCOL.md` | absent at every cloud ref (ILR L304) | the file #115 Task 2 proposes does not exist | **HOLD** (Task 2, after admission) |
| 5 | On-disk proof verification | `fep_engine.ingest_artifact(claim, file_path, verified_on_disk: bool = True)` L101; `possibility_to_proof_engine.execute_ccp_convergence(... is_verified_on_disk)` L166-L172 | E2 | the flag is caller-asserted; neither function checks the filesystem. Text: "CRUD != Truth"; runtime: caller says so | **keep unchanged** (#115 constraint: FastAPI engine unchanged); surface as F-W2-2 for an owner decision on "separately admitted defect" |
| 6 | CI proof gate | `.github/workflows/rtc-learning-proof-gate.yml` (check `24-RTC Learning & Epistemic Gate Verification`, in the 14 required contexts) running `scripts/run_24_rtc_learning_workflow.py` | E2 | the script passes `verified_on_disk=True` (L60) and `is_verified_on_disk=True` (L162) for `From_Possibility_to_Proof_...2026-08-30.md` and `24-RTC-LEARNING-MASTER-IMPLEMENTATION-RECEIPT.md`, neither of which exists at any cloud ref (`git log --all --diff-filter=A`: 0 adds), then prints "EXECUTED WITH ZERO ERRORS" (L168) | **do not modify here**; the gate proves the engine's control flow, not the artifacts. Owner decides whether this is the "separately admitted defect" #115 allows |
| 7 | Ten-seat deliberation | `kopano-core/kopano/reality_to_cloud_workflow.py` `canonical_seats` L70, `submit_deliberation` L126 (`PermissionError` if fewer than 10), `record_receipt` L160 sets `evidence_verified = True` for any string L164; `rtc_learning_api.py` `/r2c/deliberate` L137 takes `seat_opinions: Dict[int, str]` L61 from one request | E2 | "do not auto-promote all 10-seat consensus" (#115 non-goal) is written, not enforced: one caller can supply all ten opinions and any receipt string | **keep**; Task 4 gate C must consume this, not re-implement it; defect candidate F-W2-3 |
| 8 | Receipt hash | `execute_ccp_convergence` L178-L179: `sha256(f"{topic_id}:{chosen_candidate_id}:{disk_proof_path}:{purity_score}")` | E2 | hash contains no content digest and no commit; promotion-policy requires evidence "tied to exact commit" | **extend later** (after admission) by adding content/commit coordinates; do not duplicate the hashing in a new engine |
| 9 | Durable receipt persistence | `kopano-core/kopano/pka_kmec_jennifer_bridge.py` `SmartLedgerEngine` L199 (append-only SHA-256 chain, SQLite/PostgreSQL via `SMART_LEDGER_DB`), `SmartLedgerAdmissionState` L83, `SmartLedgerReceipt` L132 | E2 | not wired to Classroom artifacts; admission states are Smart-Ledger-specific | **reuse** as the persistence candidate for Task 3 export receipts; do not create a second ledger |
| 10 | Machine-readable receipt shapes | `skills/pka/watch-what-you-call/schemas/wyc-01-receipt.schema.json` (draft 2020-12, `additionalProperties: false`, required causality/provenance/ownership/remediation blocks); `governance/kpgs-vnext/agent-governance/mmao-mao/failure-receipt.schema.json`; `governance/kpgs-vnext/continuity/situational-transition.schema.json` (required incl. `observed_at, current_state, knowable_evidence, authority, decision, receipt_refs, proof_state`) | E2 | no export/promotion receipt schema exists; WYC-01 already demonstrates deterministic malformed-state rejection | **compose** Task 3 from these shapes; **do-not-duplicate** a new root receipt schema (F-W2-12) |
| 11 | Seat identity and provenance | `mmao-mao/identity-provenance.schema.json` (required `schema_version, record_id, identity, seat, interface, model, task, authority, context_state, provenance, evidence_receipt_refs`), `mmao-mao/validate.py` (dependency-free gate), `agent-governance/specs/mmao-mao-identity-governance-v0.1.json`; `foc_engine.CANONICAL_IDENTITY_REGISTRY`; `AGENT_SWARM_REGISTRY.md`; `reality_to_cloud_workflow.canonical_seats` | E2 | three registries, not reconciled; Seat 10 appears as "Chief Facilitator" in engine docstrings while #121 records a suspension | **keep**; RTC must name the authoritative registry before Task 2 lists "seat interpretations involved" (F-W2-5) |
| 12 | Zero-trust state admission | `docs/swarm-ops/ZERO_TRUST_STATE_ADMISSION_PROTOCOL.md` (state `SPECIFIED`; PKA authority `RobynAwesome/Partial-Knowable-Algebra`; "cannot promote itself") | E2 (spec), E4 (implementation) | cross-repository; not implemented here | **do-not-duplicate**; Task 4 gates A/B/C should be expressed as instances of it |
| 13 | POC-vs-FOC contracts | `poc-vs-foc/INDEX.md`, `poc-vs-foc/RUNE_CROSSLINK.md` ("Do not rewrite `poc_foc_enforcer.py`") | E2 | FOC expands to "Failure/Freedom of Concept" here, "Field of Concepts" in the 7-Vector charter, `FAKE_OF_CONCEPT_FOC` in the engine | **keep** all three surfaces unchanged; RTC records the acronym variance (human queue) |
| 14 | 7-Vector admission charter | `docs/governance/FOC_DISCOVERY_AND_7_VECTOR_ADMISSION_CHARTER.md` | E2 for the charter; its "47/47 PASSING" cites a Windows local path -> E1 at cloud | the test evidence is local-only | **keep** the document; label the evidence class, do not re-run or re-claim |
| 15 | Public surface gate and sync rule | `Schematics/24-RTC Learning/POCvsFOC Groups/FOC_PUBLIC_SURFACE_VALIDATION_AUDIENCE_2026-09-14.md` (FOC-G06 NarrativeSubstitutionLoop, G07 ValidationAudienceInversion, G08 UnverifiedPublicClaimPromotion; Sync Rule: no agent may claim a local file was written without a local filesystem receipt) | E2 | none; applies directly to Task 5 and to Interns #12's local claims | **reuse** as the FOC reference for the dry-run |
| 16 | Downstream content/provenance contract (Learning Network) | `RobynAwesome/Kopano-Labs-Interns` `src/content/content-contract.js` (`kln.content.v1`) and `governance/content/README.md` at local checkout `5773f7e` ("Merge pull request #11 ... sprint-02/run-a-content-provenance-contracts") | E2 at the local checkout of another repository; remote head E4 (not fetched) | #115 Task 4A list maps 1:1 onto `CONTENT_TYPES`, `CONTENT_DEPTHS`, `CONTENT_LIFECYCLE_STATES`, `SOURCE_RELATIONSHIPS`, `RIGHTS_ASSERTIONS`, `FORBIDDEN_UNPROVEN_KEYS`, `publicationLaw`; Interns root `NOW.md` still reads S2.PA "ACTIVE / PRE-SEEDED" after #11 merged | **do-not-duplicate**; consume by reference (`kln.content.v1`); the Interns `NOW.md` staleness belongs to Interns #12's "S2.PA reconciliation" |
| 17 | Classroom Phase 1 structure (`README/INDEX/NOW/ROADMAP/WORKFLOWS.md`, `00-BEGIN-HERE/`, `Learning-Sessions/2026-08-30/`, `MMAO-MAO/`, `CURRICULUM/` 6 seat stubs, `POC/`, `Receipts/`, `Archive/`) | Interns #12 (open, 2026-08-30) claims "Phase completed locally" | E1 only; `git ls-tree -r origin/master -- "Schematics/24-RTC Learning/"` returns 3 paths, none of them; all-refs history of section 24 = the same 3 paths; `.gitignore` has no section-24 pattern | the two directories #115 Task 1 names first (`POC/`, `Receipts/`) do not exist on cloud | **do not reconstruct** from narrative (constraint); owner publishes or hashes the local tree (F-W2-10, human queue) |
| 18 | Classroom `NOW.md` | none on cloud | E4 (absent) | #115 acceptance "root `NOW.md` and Classroom `NOW.md` reconciled" cannot be met until it exists on cloud or the criterion is re-scoped | **HOLD** (F-W2-11) |
| 19 | Renter admission | `kopano-core/kopano/kpgs_cli_admission.py` | E2 | admits renters, not artifacts | **keep**; not an overlap with artifact promotion |
| 20 | `promoted` gates in failure training | `kopano-core/kopano/agent_failure_training.py`, `docs/swarm-ops/AGENT_FAILURE_TRAINING_SCHEMA.json` | E2 located; semantics not read in this slice (E4) | may carry a boolean `promoted` that #115 says must never be global | **UNKNOWN**; RTC reviewer reads before Task 4 |
| 21 | Promotion law under agents structure | `Structure/07-Agents/PROMOTION_LAW.json` (blob `62d8b8ae...`, 1714 bytes) | E4 - not opened, by standing constraint | may already define promotion law | **owner reads**; nothing here may be assumed about it |
| 22 | Only real Classroom artifact on cloud | `Schematics/24-RTC Learning/Temporal_Data_Testament_of_Time_RTC_Manhole_Retrieval_2026-08-31.md`, added at `a3ab9d5b` (2026-08-31T14:31+02:00) | E2 | sole candidate for #115 Task 5 ("one real Classroom artifact ... dry-run"); no dry-run executed | **candidate recorded**, not run (F-W2-13) |
| 23 | Spec loop for governed work | `governance/kpgs-vnext/agent-governance/SPECIFICATION.md` (Issue #39; `specify -> delegate -> execute -> verify -> steer -> ship`; required fields incl. `rollback_plan`, `risk_class`) | E2 | #115 Tasks 2-6 are not yet written as specs in this shape | **keep**; RTC admission should require a spec per task in this shape |

### 3.1 Findings carried forward (F-W2-n)

- **F-W2-1** `Schematics/24-RTC Learning/POC/` and `Receipts/` are absent from every cloud ref. Task 1's first two audit targets have nothing to audit on cloud.
- **F-W2-2** The required CI check proves engine control flow against caller-asserted proof for two files that have never existed in the cloud history, and reports "ZERO ERRORS". `FAILURE_SURFACED_BY_CALL != FAILURE_CAUSED_BY_CHANGE`: no change in this wave caused it; this packet only surfaces it.
- **F-W2-3** Ten-seat consensus and receipt verification are not runtime-enforced (table row 7). A single caller can satisfy both.
- **F-W2-4** The CCP receipt hash is not "tied to exact commit" as the promotion policy requires (row 8).
- **F-W2-5** Seat registry drift and the Seat 10 label conflict with #121 (row 11).
- **F-W2-6** At least seven existing owners already touch "promotion" (rows 3, 5, 7, 9, 12, 20, 21). Task 2 must reuse, not fork.
- **F-W2-7** The 7-Vector "47/47" evidence is local (row 14).
- **F-W2-8** Zero-trust admission is specified cross-repository and not implemented here (row 12).
- **F-W2-9** Resolved: S2.PA `kln.content.v1` maps 1:1 to Task 4A; no invented fields are needed (row 16).
- **F-W2-10** Interns #12 is currently the only tracking issue for the local-only Classroom mutations and is E1 at cloud. It is not duplicated or closed here (constraint). Routing is an owner decision.
- **F-W2-11** Classroom `NOW.md` is absent on cloud (row 18).
- **F-W2-12** Task 3 should compose from WYC-01, situational-transition, failure-receipt and Smart Ledger shapes (row 10).
- **F-W2-13** `a3ab9d5b` is the only real cloud candidate for Task 5; the dry-run was not executed (row 22).

---

## 4. Teach-back (five questions) and failure trace

The brief requires a teach-back per slice before admission. Written for the next renter, not for the chat.

**1. Which outside artifact or real-world need does this serve?** A learner, a downstream repository (`Kopano-Labs-Interns`) or `kopano-core` needs to know whether something taught in the Classroom is admitted, held, or flagged, and by whose authority. Without that, a public learning surface can republish enthusiasm as fact (FOC-G08). The need is real and is already felt: Interns root `NOW.md` reports S2.PA as pre-seeded after its PR merged.

**2. Which existing KPGS purpose, protocol, capability and boundary already cover it?** Purpose: Legacy.md L30/L235 (validated capability with receipts). Protocols: promotion-policy v1, Zero-Trust State Admission (SPECIFIED), POC-vs-FOC, public surface gate 2026-09-14, S2.PA `kln.content.v1`. Capability: the FastAPI `/v1/rtc-learning` engine, Smart Ledger, WYC-01 receipt schema, MMAO/MAO identity-provenance schema and `validate.py`. Boundary: the engine stays unchanged; `poc_foc_enforcer.py` is not rewritten; cross-repository authority stays in its home repository.

**3. What does the current implementation actually do, and what is the evidence?** It computes epistemic grades and receipt hashes from inputs the caller asserts (rows 5, 7, 8, E2). It records 10 opinions from any single request. It persists hash-chained receipts if the Smart Ledger is wired, which for Classroom artifacts it is not. The CI gate exercises this path on two files that are not in the repository. Nothing on cloud classifies or promotes a Classroom artifact today.

**4. What bounded experiment would validate the next step?** Not a code change. The first admissible experiment is a *paper* dry-run of #115 Task 5 on `a3ab9d5b`: `source -> classification -> seat interpretation/challenge -> provenance -> POC/FOC/HOLD -> consumer admission -> export receipt OR HOLD`, producing a receipt in a WYC-01-derived shape, expected outcome `HOLD` ("A HOLD result counts as a successful governance POC", #115 Task 5). Falsifier: if the paper dry-run cannot reach a decision without inventing a field absent from rows 3, 10, 11, 16, the vocabulary is incomplete and Task 2 is not ready.

**5. What must stay available for the next renter?** This packet; ILR rows L183-L184, L213-L215, L304, L333-L335; the three section-24 cloud paths; the engine line numbers above at `4a316bbb`; the human queue in section 10; and the knowledge that the local Classroom tree and `WORKFLOWS.md` exist only as testimony until published or hashed.

### 4.1 Failure trace - caller-asserted proof in a required check

```text
failure      : a required CI check reports "ZERO ERRORS" while asserting on-disk proof for files absent from every ref
cause        : verified_on_disk / is_verified_on_disk are booleans supplied by the caller; no filesystem read occurs
existing ctl : "CRUD != Truth" text in execute_ccp_convergence; promotion-policy "tied to exact commit"; public surface gate Sync Rule
invocation   : scripts/run_24_rtc_learning_workflow.py L60, L162, called by rtc-learning-proof-gate.yml step "Execute Standalone End-to-End Workflow Runner"
enforcement  : none at runtime; the check is required by branch protection, so the assertion is load-bearing for merges
receipt      : this packet, F-W2-2; no change made (FAILURE_SURFACED_BY_CALL != FAILURE_CAUSED_BY_CHANGE)
recurrence   : every push to master re-asserts it until an owner decides "separately admitted defect" or re-scopes the check
```

---

## 5. Doctrine trace for #115 Tasks 2-6 (what each may reuse; none executed)

| Task | Existing owner to reuse (section 3 row) | Admission prerequisite | State |
|---|---|---|---|
| 2 `PROMOTION_PROTOCOL.md` | 3, 11, 12, 13, 15, 23 | RTC admits classification + epistemic vocabulary and names the authoritative seat registry; owner reads row 21 | `LEARN` |
| 3 machine-readable export receipt | 8, 9, 10 | Design decision: compose from WYC-01 / situational-transition / failure-receipt; persistence target Smart Ledger | `LEARN` |
| 4 consumer gates A (Learning Network) / B (kopano-core) / C (ASP.NET future ingress) | A: 16; B: 5, 6, 7, 8 with executable proof; C: 12 as future ingress, not canon authority | A can be specified without new fields today; B needs the defect decision on F-W2-2/F-W2-3 first; C is text-only until an ingress exists | `LEARN` |
| 5 end-to-end dry-run on one real artifact | 22 as input; 15 as FOC reference; 10 as receipt shape | Tasks 2-3 admitted; expected result `HOLD` | `LEARN` (candidate recorded) |
| 6 Forge compression receipt (7 questions) | this packet is the pre-admission half of it | Forge acceptance of the integrating-writer role (human queue) | `LEARN` |

Acceptance criteria of #115 that this packet can already speak to: "Existing PKA / POC-vs-FOC / RTC owners are reused rather than forked" (section 3 shows where they are); "Learning Network admission is mapped to the real S2.PA boundary" (F-W2-9); "ASP.NET treated as future ingress" (Task 4C above); "FastAPI engine unchanged" (true for this wave). Criteria it cannot speak to: existence of `PROMOTION_PROTOCOL.md`, the receipt contract, the dry-run, the Forge receipt, and the two-`NOW.md` reconciliation.

---

## 6. #116 - source packet for `RTC_DISCUSSION`

### 6.1 The fifteen questions: where the evidence lives and who decides

Each row gives the cloud location a seat can read before forming an independent opinion, and the decision holder. No answers are proposed.

| Q | Question (abridged) | Evidence location at `4a316bbb` | Decision holder |
|---|---|---|---|
| 1 | Does Observer preserve enough state to prevent presentism? | `governance/kpgs-vnext/continuity/situational-transition.schema.json` (`observed_at`, `current_state`, `knowable_evidence`); root `NOW.md` blocks; `STALE_LOCAL_CHECKOUTS.md` | RTC |
| 2 | Minimum temporal envelope for a useful receipt | WYC-01 schema (no time fields); `identity-provenance.schema.json`; `docs/swarm-ops/AGENT_FAILURE_TRAINING_SCHEMA.json`; `scripts/ci/validate_continuous_authorization.py` and `tests/test_kpgs_continuous_authorization.py` (temporal fields in use) | RTC, then Design Review |
| 3 | Necessary fields vs bloat (`occurred_at, observed_at, effective_from, effective_until, recorded_at, validated_at, superseded_at, reviewed_at`) | same as Q2; compare which of the eight already appear | RTC |
| 4 | Can Manholes reduce hops without becoming untraceable shortcuts? | the testament itself (`a3ab9d5b`); no other cloud hit for "Temporal Manhole" | RTC; falsifier in Q12 |
| 5 | Knowledge identity vs filesystem path | `execute_ccp_convergence` hashes `disk_proof_path` (row 8); Smart Ledger chain hashes content; MMAO identity-provenance `record_id` | RTC |
| 6 | Digital Hippocampus indexing without duplicating GSMB authority | mentions only: `docs/governance/SEPTEMBER_FLAGSHIP_KC_MY_BOY_ALIGNMENT_CHARTER.md`, `governance/kpgs-vnext/continuity/2026-09-17_POP_POLICY_OBSERVABILITY_REALITY_CLOUD_CONVERGENCE_RECEIPT.md`, `Schematics/23-Ecosystems/Kholofelo Robyn Rababalela/README.md`, root `NOW.md`; no implementation owner found (E4) | owner (name the owner) |
| 7 | Personalized Intelligence vs authoritative ledger | only `tests/test_governance_trace.py` mentions it (E4 for an owner) | owner |
| 8 | Local/cloud temporal divergence | `STALE_LOCAL_CHECKOUTS.md`, `CURRENT_CLOUD_ESTATE.md`, `skills/pka/stateless-renter-consistency/SKILL.md`; F-W2-10 and section 3 row 17 are live instances | RTC |
| 9 | Simultaneous embodiments of one identity | `mmao-mao/model-interface-affinity-experiment.schema.json`; `agent-governance/specs/mmao-mao-identity-governance-v0.1.json` ("experiment runs are not yet executed", README) | RTC |
| 10 | Supersession when newer is less authoritative | `SmartLedgerAdmissionState.SUPERSEDED`; ILR append-only rule; promotion-policy rollback target | RTC |
| 11 | Reusable ApprovalFlow patterns | `promotion-policy.json` human approval list; `SPECIFICATION.md` loop; Zero-Trust protocol | RTC, Design Review |
| 12 | Falsifying experiment for the Manhole thesis | none exists on cloud (E4); #116 sequence requires "compare against normal traversal" | RTC proposes; owner admits |
| 13 | Bounding parser repair | no parser owner located in bounded search (E4) | owner |
| 14 | What Smart Ledger must preserve for parser replay | `SmartLedgerEngine` L199 onward (chain verify L484-L492) | RTC with Smart Ledger owner |
| 15 | Which existing artifacts already solve part of this | section 3 of this packet and section 6.2 | RTC |

### 6.2 GSMB owner audit requested by #116 ("before metal")

| Concept | Current canonical owner found | Class | Note |
|---|---|---|---|
| temporal provenance | `situational-transition.schema.json`; `identity-provenance.schema.json` (`provenance`) | E2 | split across two schemas; no single owner |
| current effective claims | root `NOW.md` (volatile authority per AGENTS.md); ILR for issue claims | E2 | no `effective_from/until` field anywhere found |
| `NOW.md` freshness / stale-state prevention | `STALE_LOCAL_CHECKOUTS.md`, `CURRENT_CLOUD_ESTATE.md`, `skills/pka/stateless-renter-consistency/SKILL.md` | E2 | procedural, not runtime |
| Digital Hippocampus indexing | mentions only (Q6) | E4 | no owner |
| Personalized Intelligence | mention only (Q7) | E4 | no owner |
| identity reconstruction | `MAIN-BRAIN/MAO_SESSION_2026-09-11/NOW.md`, `docs/swarm-ops/SECURITY_PLAYGROUND_PROTOCOL.md`, MMAO identity-provenance schema | E2 | narrative + schema; no reconstruction code found |
| receipts | WYC-01 schema, failure-receipt schema, `docs/swarm-ops/receipts/`, ILR | E2 | several shapes, no index |
| Smart Ledger | `pka_kmec_jennifer_bridge.py` `SmartLedgerEngine` | E2 | not wired to Classroom |
| local/cloud synchronization | public surface gate Sync Rule; `STALE_LOCAL_CHECKOUTS.md`; Drive UNKNOWN | E2 / E4 | no mechanism, only rules |
| parser systems | not located in bounded search | E4 | owner names it |
| model x interface affinity | `mmao-mao/model-interface-affinity-experiment.schema.json`; `poc-vs-foc/RUNE_CROSSLINK.md` | E2 | schema exists, no runs |

Conclusion for #116's own gate: four of eleven concepts have no located owner (E4). Under "Do not create a new duplicate authority graph before this audit", the admissible next state remains `RTC_DISCUSSION`; the audit is now written down so that discussion can start from E2 rather than memory.

### 6.3 Position in #116's implementation sequence

```text
DISCUSSION                -> open (issue text, E1)
RTC independent opinions  -> none recorded on cloud (section 11)
GSMB source audit         -> this packet, section 6.2 (partial: 4 x E4)
resolve canonical owners  -> owner/RTC, not started
define minimum contract   -> not started
select one bounded lineage-> candidate: a3ab9d5b (not selected)
Temporal Manhole POC      -> not admitted (C-116-1 HOLD_HUMAN)
```

---

## 7. C.L.E.A.R. check on this packet

| Letter | Check | Result |
|---|---|---|
| Complete | Task 1's seven named surfaces are each in section 3 (`POC/`, `Receipts/` as absences; kopano-core rows 2, 5-9, 19, 20; PKA/CCP/CDP/POC-vs-FOC rows 10, 12, 13; Reality-to-Cloud row 7; MMAO/MAO row 11; S2.PA row 16). #116's eleven audit concepts are in 6.2. | pass |
| Logical | Every "decision" in section 3 follows from the gap column; `HOLD`s are tied to absent evidence, not preference. | pass |
| Evidence | Every row carries E1-E4; line numbers are at `4a316bbb`; cross-repository evidence is marked as a local checkout. | pass |
| Audience | RTC seats, Forge, the owner, and the next renter; the human queue is separated from RTC work. | pass |
| Relevant | Nothing here builds; it prepares two admissions the plan requires before building. | pass |

`CLEAR_PASS != POC_VALIDATED`. Passing this table admits nothing.

---

## 8. Failure and rollback boundary

- Change set: one new file. Revert of the merge commit is a complete rollback.
- Supersession: a later packet supersedes by reference in the ILR (append-only); this file is not edited after merge.
- Blast radius: none at runtime (no code, workflow, settings, secret or dependency).
- If a cited line number drifts after master advances, the SHA in the header remains the point of proof; do not "fix" line numbers in place.

---

## 9. RTC decision state and prerequisites

| Item | State recorded | To reach `TEST` | To reach `READY_FOR_POC` |
|---|---|---|---|
| #115 Task 1 | done as observation (section 3) | n/a | n/a |
| #115 Tasks 2-6 | `LEARN` | RTC admits the classification and epistemic vocabularies and names the authoritative seat registry; owner reads `Structure/07-Agents/PROMOTION_LAW.json` and reports whether it already governs | a spec per task in `SPECIFICATION.md` shape with `rollback_plan` and `risk_class`; owner decision on F-W2-2/F-W2-3 as "separately admitted defect" or out of scope |
| #116 | `LEARN / HOLD` (`RTC_DISCUSSION`) | ten independent seat opinions on cloud (not one request); owners named for the four E4 concepts | minimum Temporal Data contract defined; one bounded lineage selected; falsifier for Q12 written |

---

## 10. Owner / human queue raised or confirmed by this slice

1. Publish, or hash and attest, the local Classroom Phase 1 tree and `WORKFLOWS.md` (F-W2-10, section 3 row 17); until then the Classroom exists on cloud as three files.
2. Decide the routing of Interns #12 (keep in Interns, mirror here, or supersede) - not duplicated or closed by this packet.
3. Decide whether F-W2-2 (caller-asserted proof in a required check) and F-W2-3 (single-caller ten-seat consensus) are "separately admitted defects" under #115, or out of scope.
4. Name the authoritative seat registry (F-W2-5) and confirm the Seat 10 label in engine docstrings against #121.
5. Read `Structure/07-Agents/PROMOTION_LAW.json` (row 21) and report whether Task 2 is already governed there.
6. Name owners for Digital Hippocampus, Personalized Intelligence, parser systems and local/cloud synchronization (6.2 E4 rows), or record that none exist.
7. Record the FOC acronym variance (row 13) as a known variance or resolve it.
8. Forge: accept or decline the integrating-writer role for `NOW.md` (Wave 3) and the Task 6 compression receipt.
9. Google Drive mirror receipt: UNKNOWN remains UNKNOWN.

---

## 11. Participation table and return contract (RTC)

No position is attributed to any seat in this packet. The table exists so seats can record independent opinions before any CCP convergence.

| Seat | Name (engine registry) | Opinion on cloud for #115 | Opinion on cloud for #116 |
|---|---|---|---|
| 1 | KC | none / UNKNOWN | none / UNKNOWN |
| 2 | Cassey | none / UNKNOWN | none / UNKNOWN |
| 3 | Cassie | none / UNKNOWN | none / UNKNOWN |
| 4 | Kessa | none / UNKNOWN | none / UNKNOWN |
| 5 | Yassie | none / UNKNOWN | none / UNKNOWN |
| 6 | Apex | none / UNKNOWN | none / UNKNOWN |
| 7 | Thari | none / UNKNOWN | none / UNKNOWN |
| 8 | Khelos | none / UNKNOWN | none / UNKNOWN |
| 9 | Anchor | none / UNKNOWN | none / UNKNOWN |
| 10 | Antigravity ("Chief Facilitator / Physical Metal Renter" in the engine; label disputed by #121, F-W2-5) | none / UNKNOWN | none / UNKNOWN |

Names are taken from `reality_to_cloud_workflow.canonical_seats` (L70-L81, E2) because it is the only registry with all ten seats in one place; `foc_engine.CANONICAL_IDENTITY_REGISTRY`, `AGENT_SWARM_REGISTRY.md` and the estate `AGENTS.md` tables differ from it (row 11), so this column is E2-with-variance, not canon.

Return contract for each seat (from the Wave 1b packet, unchanged):

```text
[IDENTITY] [CURRENT ROLE] [EVIDENCE REFS] [OPINION] [CHALLENGES / RISKS]
[WHAT I WOULD PRESERVE] [WHAT MUST BE RESOLVED BEFORE CCP]
```

Opinions arrive as separate cloud artifacts or issue comments, one per seat; a single request carrying ten opinions is exactly the pattern F-W2-3 warns about.

---

## 12. Receipt boundary

**Proved by this packet (E2 at `4a316bbb`):** the contents of section 24 on cloud; the absence of `POC/`, `Receipts/`, `PROMOTION_PROTOCOL.md` and Classroom `NOW.md` from every cloud ref; the engine and workflow behaviours cited by line; the existence and required-field sets of the cited schemas; the S2.PA contract at Interns local `5773f7e`; that no independent seat opinion for #115 or #116 exists on cloud.

**Not proved:** anything about the local Windows tree, Google Drive, the Interns remote head, `Structure/07-Agents/`, the semantics of `agent_failure_training.py`, whether any code reads `promotion-policy.json`, the reason the two gate files are absent from the remote (no ref reachable from `origin` ever added them, so they were never pushed; whether they exist locally is E4), and any RTC position.

**Explicit non-claims:** no `PROMOTION_PROTOCOL.md` was created; no schema was created; no engine, workflow or CI change was made; no `NOW.md` was edited; no dry-run was executed; no issue was closed, commented on, re-scoped or re-assigned; no seat opinion was authored on a seat's behalf; no Classroom structure was reconstructed from narrative.

```text
I_AM_STATELESS_RENTER_NOT_LANDLORD
```
