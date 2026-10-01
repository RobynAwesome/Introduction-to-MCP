# KMEC OBSERVATION ENGINE #107 ADMISSION PACKET - 2026-09-30 (WAVE 2, ISSUE #107)

**Status:** OBSERVATION PACKET -> **HOLD** on PR1 implementation in this repository. No schema, fixture, or runtime code is added by this PR. Issue #107 stays OPEN.
**Scope:** Overlap audit of #107 "PR1 - contracts + fixtures" against (a) what already exists on `master`, (b) what the owner redirected to downstream repositories on 2026-09-02, and (c) what is readable in those repositories today. Output: the decisions a Design Review must take before any renter may write PR1 code anywhere.
**Ledger:** `ILR-2026-09-30` (`docs/swarm-ops/receipts/ISSUE_RECONCILIATION_LEDGER_2026-09-30.{md,json}`). Inputs: claims C-107-1 (engine unbuilt on master, POC_PENDING), C-107-2 (PR1 is a proposed, not admitted, slice), C-107-3 (cross-repo lanes unreadable, UNKNOWN) and the Wave 2 slice row `#107 PR1 | Design Review (cross-repo contract ownership) | UNRECORDED -> HOLD`. This packet is the Design Review input that row asked for. The ledger itself is updated in Wave 3, not here.
**Base:** `master@34ead442` · **Branch:** `cursor/kmec-107-admission-packet-4e71` · **Live read time:** 2026-10-01T00:41Z (all GitHub reads below).
**Actor:** Cursor cloud agent, stateless renter, operational rank Chief Facilitator. Authority: Robyn's approval of the Wave 0-3 plan (2026-09-30 22:14 UTC). No authority to decide contract ownership; that is the point of this packet.
**GSMB tier:** Cloud (this branch). Local and Google Drive: UNKNOWN.
**Doctrine:** `I_AM_STATELESS_RENTER_NOT_LANDLORD` · `WRITTEN_INSTRUCTION != RUNTIME_ENFORCEMENT` · `CLEAR_PASS != POC_VALIDATED` · `UNREADABLE != ABSENT` · `ADJACENT != DUPLICATE_LICENSE`

---

## 0. Decision in one paragraph

The issue body proposes PR1 as six contract surfaces plus DNS/backend fixtures. On 2026-09-02 the owner wrote that implementation is "decomposed into bounded owning repositories rather than duplicated inside Introduction-to-MCP" and named three lanes (KMEC#15, PKA#18, Jennifer#78). On 2026-09-07 the owner wrote that the issue is "still architectural capture only" and that "PR1-PR7 observation-engine work is unbuilt". Today, none of the six PR1 surfaces exists as a contract in this repository, but five of them have **adjacent Python shapes** here and in the KMEC clone, and the Jennifer lane has **closed with a receipt**. Writing PR1 schemas in this repository now would either duplicate a downstream owner's shape or pre-empt a shape that has not been assigned an owner. Both outcomes violate the 2026-09-02 instruction. The admissible action for a renter is therefore to surface the overlap and the unresolved ownership, and to stop. **HOLD.**

## 1. Governing record (verified live)

| Source | Id | Date (UTC) | What it says | Class |
|---|---|---|---|---|
| Issue #107 | state `open`, `updated_at 2026-09-07T00:42:56Z`, 2 comments, 0 labels | - | Title: "KMEC Data-Science Observation Engine - Parser + Smart Ledger + PKA for governed DNS/backend swarm operations" | E2 |
| Issue #107 body, "Proposed implementation sequence / PR1" | - | - | observation/event schemas; relationship-evidence schema; distribution-evidence schema; PKA status/lifecycle contract; Smart Ledger receipt contract; representative DNS/backend fixtures; no provider mutation | E2 |
| Issue #107 body, "Acceptance / POC gates" | - | - | 13 boxes, 0 checked (`rg -c "^- \[ \]"` = 13, `"^- \[x\]"` = 0) | E2 |
| Issue #107 body, "Explicit non-claims" | - | - | "Opening this issue validates **architectural capture only**." | E2 |
| Comment by `RobynAwesome` | `IC_kwDORtp9sc8AAAABSFQcmw` | 2026-09-02T10:54:44Z | "This governing issue remains the **KPGS orchestration/source-of-truth contract**. Implementation is now decomposed into bounded owning repositories rather than duplicated inside Introduction-to-MCP:" KMEC Parser Fabric -> `kpgs-morning-engine-core--kmec-#15`; PKA admission + Smart Ledger proof contract -> `Partial-Knowable-Algebra#18`; Jennifer mobile/offline persistence -> `Project-Jennifer#78`. Governing end-to-end proof: "Jennifer receipt -> PKA receipt -> KMEC observation -> original evidence". | E2 |
| Comment by `RobynAwesome` | `IC_kwDORtp9sc8AAAABS5uqkA` | 2026-09-07T00:42:56Z | "This issue is still architectural capture only. PR1-PR7 observation-engine work is unbuilt. A dated KMEC test pass (67 passed / 7 skipped) is not this engine. #122 observes KMEC repo identity/CI only. It does not implement this issue." | E2 |
| Charter `docs/governance/KPGS_4_ORGAN_CROSS_ESTATE_SMART_LEDGER_CONVERGENCE.md` | tag `KPGS-4-ORGAN-CONVERGENCE-2026-09-02` | 2026-09-02 | Names this repository as `ORCHESTRATION (#107)` above KMEC `PARSER FABRIC (Apple + Android + D_t, G_t, R_t)`; NOW.md line 464 marks it `SEALED` | E2 |

**Teach-back:** the owner kept #107 as the place where the whole is described and governed, moved the building of parts to three other repositories, and then stated that nothing in the sequence is built. A renter in this repository may describe, map and gate; a renter may not build a part here unless the owner names this repository as the part's owner.

## 2. PR1 surface-by-surface overlap audit (this repository, `master@34ead442`)

Search method: `rg` over the tree for JSON Schema files (`"$schema"`) whose names or contents match the surface; for the issue's named fields (`x_entity_id`, lifecycle words `seeded`/`correlated`/`challenged`); and for the adjacent Python modules the ledger already identified (C-107-1). Line counts are `wc -l` at this base.

| # | PR1 surface (issue body) | As a contract here | Nearest adjacent asset here | Status | Class |
|---|---|---|---|---|---|
| S1 | observation/event schemas | none (no JSON Schema file names or ids match; `evidence-bundle.schema.json` is a KPGS evidence bundle, not an observation envelope) | `kopano-core/kopano/kmec_trace_adapter.py` (381) turns `GovernanceTrace` objects into a DataFrame (`to_dataframe`, `trace_to_dict`); `governance/kpgs-vnext/evidence/evidence-bundle.schema.json` (306, `$id .../kpgs/evidence/evidence-bundle.schema.json`) | ABSENT as contract; PARTIAL as code | E2 |
| S2 | relationship-evidence schema (fields `x_entity_id`, `y_entity_id`, X/Y state, context, window, provenance ref, confidence, runtime version, PKA status) | none; `x_entity_id` appears in no JSON file | `TraceRelationshipMetrics` dataclass in the adapter: `x_variable`, `y_variable`, `sample_size`, `correlation_coefficient`, `direction`, `association_not_causation=True`, `unmeasured_confounders_may_exist=True`, `governance_action_permitted=False`; produced by `compute_relationship_metrics(df, x_col, y_col)` | ABSENT as contract; PARTIAL as code (no entity ids, no context/window, no PKA status field) | E2 |
| S3 | distribution-evidence schema | none | `TraceBoxPlotMetrics` dataclass: `variable`, `sample_size`, `minimum`, quartiles, `median`, `maximum`, `iqr`, `lower_fence`, `upper_fence`, `outlier_count`, `outlier_trace_ids`; produced by `compute_distribution_metrics(df, column)` | ABSENT as contract; PARTIAL as code | E2 |
| S4 | PKA status/lifecycle contract (`seeded -> observed -> correlated -> challenged -> validated -> adaptively/actionably admitted`) | none; none of `seeded`/`correlated`/`challenged` appears in any `.py` or `.json` here | `kopano-core/kopano/governance_trace.py` (494) `EpistemicState` = `PROVEN / SUPPORTED / INFERRED / UNKNOWN`; `kopano-core/kopano/pka_kmec_jennifer_bridge.py` (817) `pka_verdict` strings `ALLOW / HOLD / BLOCK` plus `POC_CANDIDATE / FOC_CANDIDATE`, `PkaTrustVector GREEN/YELLOW/RED`, `PkaConvergenceBand` | ABSENT as contract; three competing vocabularies in code (see 4.3) | E2 |
| S5 | Smart Ledger receipt contract | none as JSON Schema | `SmartLedgerReceipt` dataclass in the bridge: `receipt_id`, `sequence_number`, `previous_receipt_hash`, `content_hash`, `receipt_hash`, `idempotency_key`, `actor_seat`, `embodiment`, `pka_verdict`, `claim_type`, `admission_state` (`SmartLedgerAdmissionState`: `OFFLINE_CANDIDATE / PKA_REVALIDATING / POSTGRESQL_ADMITTED / CONFLICT_REJECTED / SUPERSEDED`), `device_signature`, `public_key_fingerprint`, `evidence_refs`, `supersedes_receipt_id`, `superseded_by_receipt_id`; also `skills/pka/watch-what-you-call/schemas/wyc-01-receipt.schema.json` (115, a different receipt family) and the hash-chained ledger entry shape in draft PR #245 (`kpgs.mzansi.data-engine.ledger-entry.v1`, not on master) | ABSENT as contract; PARTIAL as code, and the bridge shape is already Jennifer-flavoured (device signature, embodiment) | E2 |
| S6 | representative DNS/backend fixtures | none under any `fixtures/` path | `governance/kpgs-vnext/estate-registry/estate.json` and `evidence/live-provider-witness-2026-08-24.json` carry real apex/`www` observations (e.g. `www.kasilink.com`, "single canonical Vercel project owning both apex and www") - these are **witness records of live providers**, not fixtures, and would need a redaction decision before reuse | ABSENT as fixtures; raw material exists | E2 |
| S7 | no provider mutation | constraint, not an artifact | honoured: this packet performs no provider action | N/A | E2 |

Tests adjacent to the code column: `tests/test_kmec_trace_adapter.py` (230 lines, 5 `def test_`) and `tests/test_pka_kmec_jennifer_bridge.py` (333 lines, 8 `def test_`). They differ in dependency class:

- The adapter module imports `numpy` and `pandas` (`kmec_trace_adapter.py` lines 28-29), neither installed in the proving VM; the adapter test's pass state is therefore **E4 here**. NOW.md line 456 records a dated pass (`5 passed in 7.05s`) as testimony (E1 for this packet).
- The bridge module is stdlib-only (`hashlib`, `hmac`, `json`, `logging`, `os`, `sqlite3`, `time`, `uuid`, `dataclasses`, `datetime`, `enum`); `rg -n "pandas|numpy|kmec_trace_adapter|governance_trace" kopano-core/kopano/pka_kmec_jennifer_bridge.py` returns nothing. Its test was run in this worktree: `cd kopano-core && python3 -m pytest ../tests/test_pka_kmec_jennifer_bridge.py -q -p no:cacheprovider` -> `8 passed in 0.28s`, `git status --short` unchanged afterwards (**E2**).

Neither pass is this engine. A green adapter or bridge suite is exactly the class of evidence the owner's 2026-09-07 comment declines to count toward #107: it proves the existing shadow vocabulary works, not that PR1 contracts exist.

## 3. Downstream lane state (live, 2026-10-01T00:41Z)

| Lane | Owner's 2026-09-02 assignment | GitHub read with this token | Local clone evidence | Interpretation | Class |
|---|---|---|---|---|---|
| **KMEC** `RobynAwesome/kpgs-morning-engine-core--kmec-#15` | Parser Fabric: observations -> normalized parser envelope -> Pandas/NumPy/Dask evidence -> PKA -> Smart Ledger; preserve Apple Deployment Parser; add Android parser contract | issue 15 -> **HTTP 403** "Resource not accessible by integration"; repo metadata readable: `private: true`, default `main`, `pushed_at 2026-09-02T01:35:38Z`; `commits/main` -> `bf9988ab5ace6d1a9795e9c38242550a704e3069` at `2026-09-02T01:35:34Z` | `/agent/repos/kpgs-morning-engine-core--kmec-` HEAD `bf9988a` = remote `main` tip (exact match). Contains `src/kmec/observation_engine.py` (265; dataclasses `ObservationProvenance`, `DistributionEvidence`, `FrequencyEvidence`, `GroupedEvidence`, `RelationshipEvidence`; `ObservationEngine.describe / value_counts / distribution(iqr_multiplier) / groupby / relationship / evidence_packet`), `src/kmec/distributed_observation.py` (150; `DistributedObservationEngine`, `DistributedExecutionReceipt`, `DistributedObservationUnavailable`), `parser_protocols.py` (402), `providers/apple_xcode.py` (329), `providers/google_cloud_run.py`, `gsmb_markdown_observation.py` (856); 15 test files incl. `test_observation_engine.py` (6) and `test_distributed_observation.py` (7); **no `*.schema.json`**; **no Android provider file**; **no `seeded/correlated/challenged` vocabulary**; `.pka/README.md` line 3: "KMEC is the first controlled **private-repository** consumer candidate for `RobynAwesome/Partial-Knowable-Algebra` runtime v0.1" | Code that matches the issue's **PR2** (single-node Pandas/NumPy primitives over fixtures) and **PR4** (distributed engine with a single-node reference) descriptions exists at the KMEC tip, dated the same day as the owner's lane assignment. The issue's **PR1** contracts (JSON Schema) do not exist there either. Issue state and acceptance checkboxes on KMEC#15 are UNKNOWN. | repo/commit reads E2; clone contents E2; issue state E4 |
| **PKA** `RobynAwesome/Partial-Knowable-Algebra#18` | claim-type-aware admission; UNKNOWN/HOLD preserved; append-only hash-linked receipts; idempotency; supersede/revert; offline candidate -> reconnect revalidation | repo -> **HTTP 404** under `RobynAwesome` and under `Kopano-Labs` | no clone in this workspace; KMEC's `.pka/README.md` and `.github/workflows/pka-external-consumer.yml` reference it as a live dependency | A 404 from an integration token on what KMEC documents as a private repository is **not** evidence of non-existence. Lane state UNKNOWN. This is the lane the owner assigned the "Smart Ledger proof contract" to, which is PR1 surface S5. | E4 |
| **Jennifer** `RobynAwesome/Project-Jennifer#78` | encrypted/signed local Smart Ledger receipt envelope; Keychain/Keystore boundaries; reconnect -> PKA revalidation -> PostgreSQL admission/conflict -> Mongo projection refresh | **CLOSED** `2026-09-13T14:46:16Z`; title "FEP-POC-003: Encrypted offline Smart Ledger edge + PostgreSQL/MongoDB reconciliation for Apple and Android"; close comment 2026-09-13T14:46:15Z: "Required POC proved on CI platform-key doubles for Apple + Android semantics (not live Secure Enclave / Keystore)" | `/agent/repos/Project-Jennifer` HEAD `cc74b56` (2026-09-14): `packages/shared/src/smart-ledger-edge.ts` (89), `packages/runtime/src/smart-ledger-edge.ts` (265) | The Jennifer lane produced a receipted edge implementation of the Smart Ledger envelope. That receipt lives in Jennifer; nothing in this repository cross-references it, so #107 box 7 ("Smart Ledger records provenance and lifecycle transitions") is not yet evidenced **here**. | E2 |

`UNREADABLE != ABSENT`: two of three downstream lanes cannot be read at the issue level with this token. The Wave 2 ledger row anticipated this ("unreadable PKA/KMEC lanes").

## 4. Contradictions the Design Review must resolve (not the renter)

4.1 **Where do PR1 contracts live?** The issue body lists PR1 under #107 (this repository). The 2026-09-02 comment forbids duplication here and assigns parser work to KMEC and ledger/PKA work to PKA. The charter names this repository `ORCHESTRATION`. If contracts are orchestration artifacts, they belong here and KMEC/PKA/Jennifer must conform to them; if they are parts, they belong with their part. No surface in section 2 has a named contract owner. **This is the blocking gap.** Writing S1-S6 here resolves it by renter fiat, which is overstepping.

4.2 **"Unbuilt" versus the KMEC tip.** The owner's 2026-09-07 statement that PR1-PR7 are unbuilt and that "a dated KMEC test pass ... is not this engine" coexists with `observation_engine.py` and `distributed_observation.py` at the KMEC tip dated 2026-09-02. Two readings are possible: (a) KMEC's engine *is* this engine's PR2/PR4 and the owner's statement scopes to #107's own receipts (nothing is receipted back into #107); or (b) KMEC's engine is a different engine and #107's PR2/PR4 remain to be built against PR1 contracts that do not yet exist. Reading (a) means PR1 should be derived from KMEC's dataclasses and pinned to `bf9988ab`; reading (b) means PR1 is prior and KMEC must adapt. The renter cannot choose.

4.3 **Three lifecycle vocabularies.** #107 body: six stages `seeded -> observed -> correlated -> challenged -> validated -> adaptively/actionably admitted`. This repository's `governance_trace.EpistemicState`: `PROVEN / SUPPORTED / INFERRED / UNKNOWN`. This repository's bridge: PKA verdicts `ALLOW / HOLD / BLOCK` with `POC_CANDIDATE / FOC_CANDIDATE`, plus `SmartLedgerAdmissionState` (five states). A PR1 "PKA status/lifecycle contract" must either adopt one, define a mapping, or be issued by the PKA repository (where the owner placed "claim-type-aware evidence admission"). Writing a fourth vocabulary here would be the exact fork the issue's PR7+ section prohibits ("must not fork incompatible copies of the epistemic logic").

4.4 **Android parser.** The 2026-09-02 comment and the charter both state KMEC "adds Android deployment/parser contract". The KMEC tip readable today has `providers/apple_xcode.py` and `providers/google_cloud_run.py` only (`rg -il android src/kmec` returns nothing), while this repository's bridge already defines `AndroidDeploymentStage`. Not a PR1 item, but a charter claim without a readable artifact, relevant to S1 ownership.

4.5 **Fixture provenance.** The only DNS/backend material in this repository is live-provider witness data (S6). The issue's security box ("secrets/tokens/credentials are never written into ... fixtures") means a redaction rule must exist before witness data becomes fixtures, or fixtures must be synthetic by construction (the #103 PR2 pattern: `non_canonical: true`, placeholder values). The owner has not said which.

## 5. Acceptance box map (13 boxes, issue body)

| # | Box | Evidence in this repository at `master@34ead442` | Readable downstream evidence | State |
|---|---|---|---|---|
| 1 | NOW.md pre/post-seed receipts for every material PR lane | NOW.md lines 100, 135 keep #107 open; no PR lane for #107 has started here | - | NOT STARTED |
| 2 | Schemas reject malformed/under-specified evidence | no schemas (S1-S5) | KMEC: no schemas | ABSENT |
| 3 | Parser computes deterministic descriptive summaries and counts from fixtures | adapter `group_summary_*`, `pivot_*` over `GovernanceTrace`, not over DNS/backend fixtures | KMEC `describe`, `value_counts`, `groupby` with 6 tests (pass state E4) | PARTIAL downstream, UNRECEIPTED here |
| 4 | Box/distribution path detects fixture anomalies without claiming causation | `compute_distribution_metrics` (IQR fences, `outlier_trace_ids`) | KMEC `distribution(iqr_multiplier)` | PARTIAL both, UNRECEIPTED against #107 fixtures |
| 5 | Scatter/relationship path detects fixture relationships, records uncertainty/context | `compute_relationship_metrics` with `association_not_causation=True`, no context/window fields | KMEC `relationship` | PARTIAL both; context/window absent here |
| 6 | PKA returns UNKNOWN/HOLD and prevents unsupported promotion | `EpistemicState.UNKNOWN`; bridge `HOLD` verdict; `governance_action_permitted=False` default | PKA repo unreadable | PARTIAL here; owner-assigned lane UNKNOWN |
| 7 | Smart Ledger records provenance and lifecycle transitions | bridge `SmartLedgerReceipt` + `SmartLedgerEngine` (stdlib-only; 8 bridge tests `passed` locally, E2) | Jennifer#78 CLOSED with CI-double receipt; `smart-ledger-edge.ts` x2 | RECEIPTED downstream (Jennifer) and as shadow code here; UNRECEIPTED as a #107 contract anywhere |
| 8 | MongoDB and PostgreSQL responsibilities contractually separated, interoperable via evidence IDs | bridge enums `JenniferDatabaseLayer`, `SmartLedgerAdmissionState.POSTGRESQL_ADMITTED`; no adapters | Jennifer#78 "postgres-shaped admission -> mongo-shaped rebuild" on doubles | PARTIAL downstream on doubles; no adapter anywhere readable |
| 9 | Dask aggregation validated against single-node reference | none | KMEC `DistributedObservationEngine` with `_reference_engine`, 7 tests (pass state E4; KMEC tip commit message: "graceful skip for optional dask dependency") | PARTIAL downstream, tolerance proof UNKNOWN |
| 10 | TypeScript orchestration uses supported toolchain and passes canonical CI | none for #107 | Jennifer TS edge files exist; not #107 orchestration | ABSENT |
| 11 | DNS/backend POC observation-first, cannot mutate providers | no POC; estate witness data exists | - | ABSENT |
| 12 | Security: no secrets in telemetry/fixtures/logs/ledger | no #107 artifacts to scan; repo-wide GitGuardian runs on PRs (PR #245 check SUCCESS) | - | NOT APPLICABLE YET |
| 13 | Downstream adoption pattern documented, >=1 consumer proven | charter + FEP-POC-003 docs describe the pattern; no consumer proof receipted here | Jennifer#78 close is the closest; not cross-receipted | PARTIAL (documented), UNPROVEN |

No box can be checked by this packet. Boxes 3, 4, 5, 7, 9 have downstream or adjacent evidence that a cross-repo receipt could later bring into #107; none of that is this packet's claim.

## 6. Admission conditions for a future PR1 slice (any repository)

A renter may start PR1 only when a Design Review entry (or an owner comment on #107 with the same content) records:

1. **Contract owner per surface** S1-S6: this repository, KMEC, PKA, or Jennifer. One owner per surface; shared ownership is a HOLD.
2. **Shape precedence** (resolves 4.2): either "schemas derive from KMEC `observation_engine.py` dataclasses at a pinned SHA" or "schemas are prior and KMEC adapts". If derived, the pin is `bf9988ab5ace6d1a9795e9c38242550a704e3069` or later, stated explicitly.
3. **Lifecycle vocabulary** (resolves 4.3): adopt the six-stage #107 lifecycle, adopt `EpistemicState`, adopt PKA verdicts, or publish the mapping table between them. Where the PKA repository is the owner, this repository consumes and does not define.
4. **Fixture source** (resolves 4.5): synthetic-by-construction (recommended; matches #103 PR2 and avoids any redaction question) or redacted witness data with a written redaction rule and a secret-scan step.
5. **Gate placement**: if any surface lands here, it enters `.github/workflows/kpgs-vnext-phase0-gate.yml` as a `KPGS-<NAME> PASS|FAIL` validator plus unittest step, exactly as #103 PR1 (`b9942724`) and PR2 (draft #245) did; strict Draft 2020-12 with `additionalProperties: false` and a versioned `schema` constant.
6. **Receipt route**: how a downstream receipt (for example Jennifer#78's close receipt) is brought into #107 without copying code - a dated cross-repo receipt file under `docs/swarm-ops/receipts/` citing issue, SHA, and CI run.
7. **Tooling boundary**: the proving environment for pandas/numpy/dask tests, since this repository's hosted gate for #103 ran without them and the local VM lacks them.

Until 1-3 are recorded, a renter writing S1-S5 is guessing the owner's intent. Until 4 is recorded, a renter writing S6 risks the security box.

## 7. Reusable, already-receipted patterns (for the reviewer; nothing is implemented here)

| Pattern | Where | Status | Fit for PR1 |
|---|---|---|---|
| Strict kpgs-vnext schema + `validate.py` gate + unittest + CI step | `governance/kpgs-vnext/mzansi-language/` (PR1 `b9942724` on master) | MERGED | Template for S1-S5 wherever they land |
| Hash-chained append-only JSONL ledger with idempotent replay, conflict receipts, tamper detection, one-way transitions | `governance/kpgs-vnext/mzansi-language/data_engine.py` (draft PR #245, hosted checks all SUCCESS on `106604f9`) | UNMERGED | Candidate shape for S5 **only if** the owner names this repository as the receipt-contract owner; otherwise a reference for PKA |
| `SmartLedgerReceipt` / `SmartLedgerAdmissionState` dataclasses | `kopano-core/kopano/pka_kmec_jennifer_bridge.py` | ON MASTER (stdlib-only; 8 tests pass locally) | Existing S5 vocabulary; must be reconciled with whatever PKA#18 defines, not re-declared |
| `TraceBoxPlotMetrics` / `TraceRelationshipMetrics` | `kopano-core/kopano/kmec_trace_adapter.py` | ON MASTER | Existing S2/S3 field lists; lack entity ids, context, window, PKA status |
| KMEC `DistributionEvidence` / `RelationshipEvidence` / `ObservationProvenance` | KMEC `src/kmec/observation_engine.py@bf9988ab` | DOWNSTREAM | The other candidate S1-S3 shape; precedence undecided (4.2) |
| Evidence bundle schema | `governance/kpgs-vnext/evidence/evidence-bundle.schema.json` | ON MASTER | Wrapper for receipts, not an observation envelope |

## 8. C.L.E.A.R.

| Axis | Assessment |
|---|---|
| **Complete** | All six PR1 surfaces plus the mutation constraint are audited (section 2); all three downstream lanes are read to the limit of the token (section 3); all 13 acceptance boxes are mapped (section 5). |
| **Logical** | The HOLD follows from two owner statements that together leave no admitted builder for PR1 in this repository, and from the presence of adjacent shapes whose precedence is undecided. |
| **Evidence** | Issue and comment reads, repository metadata, commit SHAs, file line counts, grep results and clone heads are E2 and timestamped. KMEC#15 issue state and PKA#18 are E4 and labelled. The adapter test (pandas-bound) is E4 locally and E1 via NOW.md; the bridge test (stdlib-only) was run here, `8 passed`, E2. No E3 inference is presented as a fact; the two readings in 4.2 are offered as alternatives. |
| **Audience** | Forge CA / RTC Design Review (decisions 6.1-6.7); owner (whether this repository owns any PR1 surface); future renters (what exists, where, and why not to re-declare it). |
| **Relevant** | Bounded to #107 PR1 admission. Does not touch #103, #110 or #122 code paths; the only #103 reference is the reusable gate pattern. |

`CLEAR_PASS != POC_VALIDATED`. This packet validates nothing about the engine. It validates that the PR1 question is not yet answerable by a renter.

## 9. What this packet does not claim

- No claim that any PR1 surface exists, anywhere, as a contract.
- No claim that KMEC's `observation_engine.py` is or is not #107's PR2; both readings are recorded for the owner.
- No claim about KMEC#15 or PKA#18 state beyond "unreadable with this token".
- No claim that Jennifer#78's close satisfies any #107 box; it is downstream evidence awaiting a cross-repo receipt.
- No claim that this repository's adapter tests pass here; they were not run (pandas absent). The bridge tests did pass here (`8 passed`), and that pass is explicitly **not** offered as evidence for any #107 acceptance box.
- No claim that #107 can close or that any acceptance box can be checked.
- No DNS, provider, or runtime action was performed or recommended.

## 10. Decisions requested (owner / Design Review)

- [ ] Name the contract owner for each of S1-S6 (6.1).
- [ ] State shape precedence between #107 schemas and KMEC `observation_engine.py@bf9988ab` (6.2).
- [ ] Choose or map the lifecycle vocabulary (6.3).
- [ ] Choose synthetic fixtures or a redaction rule for S6 (6.4).
- [ ] Confirm or correct reading (a)/(b) in 4.2 so that the ledger claim C-107-1 can move from `POC_PENDING` to either `PARTIAL_DOWNSTREAM` or stay `POC_PENDING` with a reason.
- [ ] Decide whether a cross-repo receipt for Jennifer#78 should be filed here now (box 7 route, 6.6) or wait for the first PR1 landing.
- [ ] Record the decision as an RTC/Design Review entry or as an owner comment on #107, so the next renter has an admission basis rather than this HOLD.

On merge of this PR, Wave 3 appends a ledger entry: `#107 PR1 -> HOLD packet filed <sha>; admission conditions 6.1-6.7 open`. #107 remains open.

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
