# MZANSI DATA ENGINE PR2 RECEIPT - 2026-09-30 (WAVE 2, ISSUE #103)

**Status:** IMPLEMENTATION RECEIPT for a bounded slice. Draft pull request; owner review and merge pending. Issue #103 stays OPEN.
**Scope:** Phase 7 PR2 = governed Mzansi Data Engine foundation: record persistence + provenance/consent/validation state + synthetic fixtures + gate + tests. Nothing else.
**Ledger:** `ILR-2026-09-30` (`docs/swarm-ops/receipts/ISSUE_RECONCILIATION_LEDGER_2026-09-30.{md,json}`). Claims C-103-1 (PR1 on master, POC_VALIDATED for structure) and C-103-2 (PR2 not started, POC_PENDING) are the inputs; this receipt is the evidence that moves C-103-2 to "PR2 submitted for review". The ledger itself is updated in Wave 3, not here.
**Base:** `master@499876734183011de590668c0b2deabad07e4660` · **Branch:** `cursor/mzansi-data-engine-pr2-4e71` · **Local proof time:** 2026-10-01T00:30Z.
**Actor:** Cursor cloud agent, stateless renter, operational rank Chief Facilitator. Authority: Robyn's approval of the Wave 0-3 plan (2026-09-30 22:14 UTC) plus the owner's written PR2 admission on #103 (section 1).
**GSMB tier:** Cloud (this branch; master once merged). Local and Google Drive: UNKNOWN.
**Doctrine:** `I_AM_STATELESS_RENTER_NOT_LANDLORD` · `WRITTEN_INSTRUCTION != RUNTIME_ENFORCEMENT` · `CLEAR_PASS != POC_VALIDATED` · `FAILURE_SURFACED_BY_CALL != FAILURE_CAUSED_BY_CHANGE`

---

## 1. Admission basis (verified before any code was written)

| Source | Id | Date (UTC) | What it admits | Class |
|---|---|---|---|---|
| Issue #103 comment by `RobynAwesome` | `IC_kwDORtp9sc8AAAABQToH6Q` | 2026-08-24T00:13:46Z | "PR2 = governed Mzansi Data Engine foundation. Start with record persistence + provenance/consent/validation state and fixtures; do **not** begin multi-language expansion or production TTS first." | E2 |
| Issue #103 comment by `RobynAwesome` | `IC_kwDORtp9sc8AAAABS5up5w` | 2026-09-07T00:42:54Z | "PR2 (Mzansi Data Engine persistence + fixtures) has **not** started. No dataset, speech, or runtime claim is admitted. ... This issue stays the implementation lane." | E2 |
| Ledger `ILR-2026-09-30`, Wave 2 slice table | `#103 PR2` row | 2026-09-30 | `ADMITTED_BY_ISSUE_RECORD; RTC decision not recorded` | E2 |

Both comments were re-read live via `gh api repos/RobynAwesome/Introduction-to-MCP/issues/103/comments` on 2026-10-01T00:2xZ; the node ids match. No RTC/Design Review decision record exists for PR2 beyond the issue record. The slice therefore proceeds on **issue-record admission by the owner**, and the merge decision remains the owner's.

**Teach-back (what I understood I was admitted to do):** build the place where linguistic evidence records are stored and governed - validated against the PR1 schema, persisted append-only with provenance, consent and validation state, with explicit rules for how a record's class and status may change - and prove it with placeholder fixtures. Not: collect Sepedi, train anything, synthesise speech, add languages, or claim the promotion gate is met.

## 2. What was delivered

| Path | Lines | Role | Class |
|---|---|---|---|
| `governance/kpgs-vnext/mzansi-language/data_engine.py` | 752 | Runtime (stdlib only): `SchemaValidator`, `LinguisticRecordStore`, `Receipt`, lifecycle rule tables, fixture loader | E2 |
| `governance/kpgs-vnext/mzansi-language/fixtures/linguistic-records.synthetic.json` | 249 | 6 placeholder records, one per evidence class plus a no-consent and a rejected case; `non_canonical: true` | E2 |
| `governance/kpgs-vnext/mzansi-language/fixtures/linguistic-records.invalid.json` | 143 | 9 must-refuse records with expected error substrings | E2 |
| `governance/kpgs-vnext/mzansi-language/validate.py` | 244 | Gate: prints `KPGS-MZANSI-DATA-ENGINE PASS|FAIL`, exit code follows | E2 |
| `tests/test_mzansi_data_engine.py` | 381 | 29 unittest cases across 6 classes | E2 |
| `governance/kpgs-vnext/mzansi-language/README.md` | +59 / -2 | PR2 section: files, behaviour, rule tables, run commands, non-claims | E2 |
| `.github/workflows/kpgs-vnext-phase0-gate.yml` | +10 | Two steps (gate, tests) and two `py_compile` targets; test path added to triggers | E2 |

No file outside these paths was touched. No existing schema was modified. No dependency was added.

### 2.1 Design decisions that enforce the PR1 invariants at runtime

| PR1 invariant (README) | Runtime enforcement in `data_engine.py` |
|---|---|
| 4 Evidence provenance mandatory | Schema validation on every `admit`; `evidence.class` resolved through `$ref` to `evidence-class.schema.json`, enum exact |
| 5 Synthetic evidence never self-promotes | `EVIDENCE_CLASS_TRANSITIONS` has no edge into `AI_*` or `UNVERIFIED`; promotion to `HUMAN_VALIDATED` requires status `validated`, >=1 validator, consent `true`; `synthetic` flag is copied unchanged on every version; `admissible_records()` excludes `synthetic: true` by default |
| 6 Consent/licensing are data-plane fields | `admissible_records()` tests `speaker_consent is True` and `license is not None`; `withdraw_consent` is one-way and demotes `validated` to `disputed` |
| 8 HOLD is valid | `admit` returns `duplicate` or `conflict` receipts instead of overwriting; `TransitionRefused` is raised rather than coerced |
| 9 POC is receipted | No `POC_*` string is produced by the engine; the gate script prints PASS/FAIL only |
| Promotion gate: "preserve failures/disagreements" | `rejected` is terminal; `record_conflict` entries are appended, never dropped; history is replayable per `record_id` |

### 2.2 Ledger shape

One JSONL entry per event: `{"schema": "kpgs.mzansi.data-engine.ledger-entry.v1", "entry_id": "mze-%08d", "sequence", "event", "record_id", "actor", "at", "prev_hash", "record", "detail", "entry_hash"}`. `entry_hash = sha256(prev_hash + canonical_json(entry without entry_hash))`; genesis `prev_hash` is 64 zeros. Reload replays and calls `verify_chain()`; a modified byte raises `LedgerIntegrityError`.

## 3. Acceptance checks (local, Python 3.12.3, 2026-10-01T00:30Z)

| # | Command | Result | Class |
|---|---|---|---|
| A1 | `python3 governance/kpgs-vnext/mzansi-language/validate.py` | `KPGS-MZANSI-DATA-ENGINE PASS: contracts strict, 6 synthetic fixtures admitted, invalid cases refused, ledger replay/conflict/transition/reload/tamper boundaries hold. No linguistic or model claim.` exit 0 | E2 |
| A2 | `python3 -m unittest discover -s tests -p 'test_mzansi_data_engine.py'` | `Ran 29 tests in 0.082s` / `OK` | E2 |
| A3 | `python3 -m py_compile` on `validate.py` and `data_engine.py` | ok | E2 |
| A4 | `yaml.safe_load` of the edited workflow | ok | E2 |
| A5 | Full sweep `python3 -m unittest discover -s tests -p "test_*.py"` on this branch | `Ran 257 tests` / `FAILED (failures=3, errors=19)` | E2 |
| A6 | Same sweep on a clean `origin/master@49987673` worktree | `Ran 228 tests` / `FAILED (failures=3, errors=19)` | E2 |
| A7 | Cross-check of my validator against reference `jsonschema` 4.26.0 on all 15 fixture records | 14 of 15 agree; the one difference is `created-at-not-date-time` (reference reports 0 errors because `rfc3339-validator` is not installed, so it does not check `format`; mine refuses) | E2 |

A5 vs A6: the 22 failing tests are identical sets and all stem from third-party modules absent in this VM (`fastapi` x10, `pandas` x3, `typer` x2, `litellm` x2, `matplotlib`, `bs4`, `bandit`). The branch adds 29 tests, all passing, and no new failure. `FAILURE_SURFACED_BY_CALL != FAILURE_CAUSED_BY_CHANGE`. The hosted RTC gate installs requirements first; its result on this PR head is **UNKNOWN** until CI runs (E4).

### 3.1 What the gate script actually proves (`validate.py`)

1. The three object contracts are Draft 2020-12 strict (`additionalProperties: false`, versioned `schema` constant) and the evidence-class enum is exactly the six admitted values.
2. Synthetic fixtures: `non_canonical: true`, >=4 records, no secret-shaped strings, every record `synthetic: true` and `language_tag: nso`, text starts with `FIXTURE_`, provenance is `fixture://`, code-switch offsets land inside the text, `present`/`segments` coherent, every promotable class covered.
3. Invalid fixtures: >=6 cases, every case refused, and the reported error contains the expected substring.
4. Ledger round trip with a fixed clock: admit all six; re-admit is `duplicate` and appends nothing; mutated re-admit is `conflict` and the head is unchanged; refused transitions raise; promotion keeps `synthetic: true`; default admissible set is empty for synthetic fixtures and non-empty only with `include_synthetic=True` after a receipted promotion; reload reproduces the head hash; a tampered line fails `verify_chain()`.

## 4. Failure and rollback boundary

- Gate FAIL or test failure on CI: the PR does not merge. Nothing on master changes.
- Revert path: `git revert` of the single merge commit removes seven paths; no migration, no data, no external system is involved.
- The workflow change only adds steps and `py_compile` targets; existing steps and triggers are untouched.
- If the owner later changes the PR1 schema, `SchemaValidator` raises at load on any keyword it does not implement, so the engine fails closed rather than skipping constraints.

## 5. C.L.E.A.R.

| Axis | Assessment |
|---|---|
| **Complete** | The admitted PR2 sentence names four things - persistence, provenance/consent/validation state, fixtures, and two exclusions. All four are present; both exclusions are respected. |
| **Logical** | Every runtime rule maps to a PR1 invariant (section 2.1). The admissible set is computed from fields the schema already requires. |
| **Evidence** | All claims in this receipt are E2 (artifact on branch, command output) except the hosted CI result, which is E4 until the run exists. |
| **Audience** | Owner (merge decision), Forge/RTC (whether issue-record admission suffices or a Design Review entry is wanted), future renters (README rule tables). |
| **Relevant** | Bounded to #103 PR2. Does not touch #107, #110 or #122, and does not pre-empt the promotion gate. |

`CLEAR_PASS != POC_VALIDATED`. This receipt supports **POC_VALIDATED for persistence and lifecycle governance over placeholder fixtures only**, pending owner merge and a green hosted gate.

## 6. What this slice does not claim

- No Sepedi or any other linguistic content exists in the repository because of this PR. Every fixture string is a labelled placeholder.
- No model, dataset, speech, translation, routing, or native-speaker validation.
- No change to PR1 schemas; no new language tags; no TTS.
- No claim that the promotion gate is met. The engine records gate evidence; it does not produce it.
- No claim that issue #103 can close. PR2 is one of ten phase boxes on the issue.

## 7. Owner close checklist for this PR (not for #103)

1. Confirm the admission basis in section 1 is the one intended, or ask Forge/RTC to record a Design Review entry first.
2. Read the two rule tables in the README and confirm they match the intended governance (in particular: `rejected` terminal, consent one-way, synthetic flag immutable).
3. Wait for `kpgs-vnext-phase0-gate` and `rtc-learning-proof-gate` on the PR head.
4. Merge or request changes. On merge, Wave 3 appends a ledger entry moving C-103-2 to `PR2 merged <sha>`; #103 remains open for PR3+.

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
