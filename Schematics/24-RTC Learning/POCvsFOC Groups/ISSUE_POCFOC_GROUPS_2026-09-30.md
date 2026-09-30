# ISSUE POC / FOC GROUP VALIDATION - 2026-09-30

**Status:** PROPOSED WORKING CLASSIFICATION - NOT ADMITTED
**Estate:** `RobynAwesome/Introduction-to-MCP` - 17 open issues at `master@8c6d22f2`
**Source repo:** `RobynAwesome/Introduction-to-MCP`
**GSMB owner:** `poc-vs-foc/`
**Accountable seats for admission:** RTC deliberates; Forge CA assembles the evidence and disagreement map; Cursor CF facilitates and assembles the source packet. No seat has admitted this document.
**Canonical local checkout path:** `Schematics/24-RTC Learning/POCvsFOC Groups/ISSUE_POCFOC_GROUPS_2026-09-30.md`
**Cloud mirror:** `docs/governance/ISSUE_POCFOC_GROUPS_2026-09-30.md` (byte-identical to the path above)
**Ledger:** `docs/swarm-ops/receipts/ISSUE_RECONCILIATION_LEDGER_2026-09-30.md` and `.json`

---

## What this document does

It validates POC-versus-FOC groups against what the open issues ask, plan and say, in two layers.

1. **Existing groups.** `poc-vs-foc/FOC_CLASSIFICATION_INDEX.md` defines `FOC-G01` to `FOC-G08` as failure patterns with a detection mechanism and a defensive loop. Each is checked against the issues.
2. **Working tags.** Five proposed tags classify issue claims (not actors) by how much evidence stands behind them.

This document classifies issue-state claims. Classification of any actor's conduct is an RTC question (#167 question 1) and is not made here.

## FOC senses in use

The repository uses FOC in three senses (ledger O-14): Field of Concepts (constitution), Failure of Concept (`FOC_CLASSIFICATION_INDEX.md`, SSE lock), Full Operational Capability (GSMB-Issues fork scores). The tag `FOC_RISK` and the groups below use the Failure-of-Concept sense. The other two are cited, not conflated.

## Existing groups checked against the issues

| Group | Pattern (from the index) | Issues where it is visible | Match |
|---|---|---|---|
| FOC-G01 NeuralFailureFirewall | 8th Deadly Sin monitor | none | none |
| FOC-G02 ContextBleedAnomaly | CBP telemetry audit | #121 (history cites context bleed) | context |
| FOC-G03 SemanticDriftLeak | Invariance shift check | none | none |
| FOC-G04 GhostExecutionLoop | Run-time resource scan | #183 (problem statement targets ghost and orphan execution) | context |
| FOC-G05 ContextCorruptionBreach | Unauthorized context wiping | none asserted | none |
| FOC-G06 NarrativeSubstitutionLoop | Explanation exists while the corrective artifact or receipt does not | #122 (cites a receipt file absent from master); #167 (required RTC deliverable absent) | partial |
| FOC-G07 ValidationAudienceInversion | Internal validation displaces public user value | #158 (same estate as the 2026-09-14 corrections) | context |
| FOC-G08 UnverifiedPublicClaimPromotion | Stale or weak claim promoted as public truth | #158 (same estate) | context |

Result: 0 issues classified under an existing group as an actor failure; 2 partial matches; 3 context-only. `partial` means the pattern's wording fits an observed gap, not that any actor is classified.

## Candidate group (proposed, not added to the index)

### ControlStateDrift

**Pattern:** a repository or provider control recorded as enforced is later found absent or bypassed, removal attribution is unknown, and no drift detector exists.

**Evidence (ledger F-1):** `NOW.md` records an approving-review requirement as restored on 2026-09-30; afterwards PR #236 merged with no review and PRs #237 and #238 report `CLEAN` with no review decision; protection is unreadable to the observing token.

**Near-matches and why they fall short:** G06 requires explanation without an artifact, but the original readback was a real artifact at its time; the gap is temporal validity. G08 covers public surfaces; `NOW.md` is internal.

**Falsifier:** an admin-scope readback receipt for the current setting exists, and a drift check (automated or equivalent) was exercised against a deliberate change and reported it.

**Rule (proposed):** a written instruction does not prove runtime enforcement. A control claim in `NOW.md` carries its readback time and decays to UNKNOWN when not refreshed.

**Admission:** requires RTC. The index's Growth Protocol would assign `FOC-G09`; that entry is not created here. Whether the lapse is logged in `poc-vs-foc/BREACH_LOG.md` is a Forge/RTC decision.

## Proposed working tags

| Tag | Meaning (proposed) | PKA mapping (proposed) |
|---|---|---|
| POC_VALIDATED | Evidence for the NAMED claim exists on master or was re-observed in this run, with a pointer. Says nothing about any wider claim. | ALLOW/PROPOSE (named claim only) |
| POC_PENDING | A bounded slice is defined and executable; its claim is not yet evidenced. | HOLD |
| HOLD_HUMAN | The next step is gated by human authority or RTC, not by renter evidence. | HOLD |
| FOC_RISK | A claim recorded in an issue or NOW.md exceeds what current evidence supports. | BLOCK (promotion of the over-claim) |
| UNKNOWN | Evidence absent, unreadable by this token, or dated and not re-observed. | HOLD |

### Falsifiers (how each tag could be wrong)

- **POC_VALIDATED** is wrong if re-running the named command or re-reading the named file does not reproduce the stated result, or if the claim is used for anything beyond its **limits** text.
- **POC_PENDING** is wrong if the slice is not actually bounded or executable, or if admission was required and not recorded.
- **HOLD_HUMAN** is wrong if the gate is in fact satisfiable from renter-visible evidence.
- **FOC_RISK** is wrong if a current readback shows the recorded claim is true.
- **UNKNOWN** is wrong if evidence exists and was not searched for; every UNKNOWN row names what was and was not checked.

## Per-issue cross-reference

| Issue | Tag | PKA | Existing-group cross-reference |
|---|---|---|---|
| #94 | UNKNOWN | HOLD | none asserted |
| #102 | HOLD_HUMAN | HOLD | none asserted |
| #103 | POC_PENDING | HOLD | none asserted |
| #107 | POC_PENDING | HOLD | none asserted |
| #110 | POC_PENDING | HOLD | none asserted |
| #115 | POC_PENDING | HOLD | none asserted |
| #116 | HOLD_HUMAN | HOLD | none asserted |
| #121 | HOLD_HUMAN | HOLD | G02 context only (issue history cites context bleed); no classification made |
| #122 | POC_PENDING | HOLD | G06 partial (comment cites a receipt path absent from master); not an actor classification |
| #158 | HOLD_HUMAN | HOLD | G07/G08 context only (same estate as the 2026-09-14 public-surface corrections) |
| #163 | POC_VALIDATED | ALLOW/PROPOSE (named claim only) | none asserted |
| #167 | HOLD_HUMAN | HOLD | G06 partial (required deliverable absent while narrative exists); the underlying offense classification is RTC question 1 and is NOT made here |
| #183 | POC_PENDING | HOLD | G04 context only (problem statement targets ghost and orphan execution); no classification of any actor |
| #205 | POC_VALIDATED | ALLOW/PROPOSE (named claim only) | none asserted |
| #207 | HOLD_HUMAN | HOLD | candidate ControlStateDrift (proposed, see groups doc); G06 and G08 near-matches insufficient |
| #211 | HOLD_HUMAN | HOLD | none asserted |
| #231 | HOLD_HUMAN | HOLD | none asserted |

## Decisions requested from RTC

1. Adopt, amend or reject the five working tags, the PKA mapping, and the wider `HOLD_HUMAN` definition.
2. Decide whether `ControlStateDrift` becomes a group, and whether the review-requirement lapse is logged as a breach.
3. Decide the SAP naming conflict before #183 proceeds (Spawn Agent Protocol already exists).
4. Reconcile the PKA verdict enum spelling and the admission-state spelling (`READY_FOR_POC` versus `READY_FOR_BOUNDED_TEST`).
5. Decide whether the GSMB expansion variance needs a sealed ruling.

## Boundary

This document proposes classifications and records what was and was not checked. It does not admit itself, close any issue, change any setting, or classify any actor.

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
