# ISSUE RECONCILIATION LEDGER - 2026-09-30 (WAVE 0 - CONTEXT ANCHOR)

**Status:** ACTIVE RECEIPT / OBSERVATION ONLY. This receipt changes no issue state, repository setting, dependency, or runtime.
**Receipt id:** `ILR-2026-09-30` · **Machine twin:** `ISSUE_RECONCILIATION_LEDGER_2026-09-30.json` (append-only, hash-chained)
**Authority:** Robyn, 2026-09-30 22:14 UTC: "YOU MAY BEGIN EXCTION OF YOUR PLAN I APPROVE" (E1). The Forge CA brief "GSMB continuity and admission brief", relayed in the same thread, is an attributed instruction.
**Actor:** Cursor cloud agent, stateless renter, operational rank Chief Facilitator (CF). **Model:** Claude Sonnet 5.5 as stated in this session's system prompt; Forge's brief names Fable. Both are recorded and not reconciled here (a model name in a receipt is attribution, not attestation). **Interface:** Cursor cloud agent, Linux VM, GitHub App token `cursor`.
**Base:** `master@8c6d22f22dbc600a38b52daf3b2887940b8841fb` (observation began at `65975a12`; master advanced when the owner merged PR #237 during the session, see O-01 and O-20) · **Observation window:** 2026-09-30T22:15Z to 2026-09-30T22:48Z · **Publishing worktree:** clean checkout of the base, branch `cursor/issue-ledger-context-anchor-4e71`.
**GSMB tier:** Cloud (this file, once merged). Local GSMB: UNKNOWN to this runtime. Google Drive GSMB: UNKNOWN until an owner receipt exists.
**Doctrine:** `I_AM_STATELESS_RENTER_NOT_LANDLORD` · `CLEAR_PASS != POC_VALIDATED` · `WRITTEN_INSTRUCTION != RUNTIME_ENFORCEMENT`

---

## 0. Read this first: where the evidence changed the plan

The approved plan was checked against live GitHub and master before any claim was written. These findings changed verdicts. Details are in section 5.

1. **F-1** The approving-review requirement is not observably in force (recurrence).
2. **F-2** Protected-material flag: tracked Structure/discord_backup_codes.txt in a public repository.
3. **F-3** #207 is not ready to close; owner-closeable set is #205 only.
4. **F-4** #163 artifact is delivered but its own status is OPEN with no exit criteria.
5. **F-5** #183's link to #121/#167 is an inference, and its acronym collides.
6. **F-6** #211 HOLD persists after the latest merge.
7. **F-7** #158's pull request is stale and its direction may be superseded.
8. **F-8** #122's cited receipt is absent and it is the declared parent audit of eight issues.
9. **F-9** #167 question 3 was open when PR #166 merged.
10. **F-10** Third-party and generated material dominates the tracked tree.

Consequence for the plan: the owner-closeable set shrinks from four issues (#205, #207, #163, #122) to one (#205). Each other issue stays open with a named next action and actor.

---

## 1. Working authority and role packet

```text
Robyn - final human authority
  -> RTC - governed deliberation and admission
    -> Forge / CA - architecture, integration, acceptance, evidence review
      -> Cursor / CF - facilitation, bounded delivery, continuity, handoffs
        -> admitted implementation and validation lanes
```

| Field | Recorded value |
|---|---|
| Actor | Cursor cloud agent, stateless renter |
| Assigned role | Chief Facilitator, operational rank |
| Model (attribution) | Claude Sonnet 5.5 per session system prompt; Forge brief names Fable |
| Interface | Cursor cloud agent (Linux VM) |
| Human authority | Robyn's approval message, 2026-09-30 22:14 UTC |
| Forge relationship | Forge CA precedes Cursor CF in the working order after RTC |

Operational rank is not an RTC identity seat. Incident, recusal, suspension and identity-admission gates stay attached to their subjects (#121, #167). Nothing here grants incident exit or a seat.

**Integrating writer (proposed, pending Forge CA acceptance):** Cursor CF for root `NOW.md`, this ledger, and the closeout records during Waves 0-3. Forge CA supplies blocks and acceptance as packets; Cursor appends them.

## 2. Mission line

`Legacy.md`: convert local context into validated human capability, economic participation and capability multiplication, with continuity that survives a change of founder, model, tool and institution. It is a mission target, not a completion claim (`GLOBAL_UNEMPLOYMENT_SOLVED_REQUIRES_PROOF`).

This ledger's contribution: it lets the next renter reconstruct the state of 17 open issues from receipts instead of memory (`LEGACY != FOUNDER_DEPENDENCE`). Each Wave 2 slice states its own contribution in its teach-back.

## 3. Source populations and observation rules

- **Cloud population:** a clean worktree at the base SHA. Every observation carries a command or API, a UTC window, an evidence class and its uncertainty.
- **Local OneDrive population:** dirty, separate, unreadable here. It enters only as `LOCAL_EVIDENCE_REPORTED_BY_<actor>`, never merged into cloud rows.
- **Evidence classes** (RTC council prompt, from `fep_engine.py`): E1 direct user testimony; E2 repository or artifact evidence; E3 working inference; E4 unknown, requires forensic audit.
- **Claim families** (FOC vs POC constitution): Declarative (testimony), Textual (source), Empirical (metal or reality). A claim is tagged per family, never by frequency or proximity.
- **Attributed** means stated in an issue, `NOW.md` or the brief, and not re-observed by this renter.

## 4. Observations

| ID | What | Result | Class | Uncertainty |
|---|---|---|---|---|
| O-01 | Cloud head of master | Observation began at 65975a125cad2954aa51cdf8b888ce6523839fd5 (merge of PR #236, 2026-09-30T21:05:03Z). During the session master advanced to 8c6d22f22dbc600a38b52daf3b2887940b8841fb (merge of Dependabot PR #237, 2026-09-30T22:32:09Z, merged by RobynAwesome; it changes only uv.lock). This receipt is based on 8c6d22f2. Root NOW.md and the studio lockfile have identical blobs at both heads. | E2 | Master can advance again before merge; the publishing branch is rebased and re-checked at merge time. |
| O-02 | Open issues | 17 open: #94 #102 #103 #107 #110 #115 #116 #121 #122 #158 #163 #167 #183 #205 #207 #211 #231. Latest updatedAt among them is 2026-09-28; none changed since the issue dump used here. | E2 | Comment bodies were read from a dump taken 2026-09-30T21:36Z; issue updatedAt values show no later activity. |
| O-03 | Open pull requests (new since last read) | #238 pyjwt 2.13.0->2.15.0 changes only uv.lock: mergeStateStatus=CLEAN, reviewDecision=''. #239 litellm 1.89.0->1.89.7 changes kopano-core/requirements.txt and uv.lock: mergeStateStatus=BLOCKED while reviewDecision='' (so whatever blocks it is not a review requirement). #237 urllib3 was open earlier and is now merged (O-20). | E2 | Outside the approved plan; not acted on. Dependency-firewall and scoped review belong to the Security backlog lane. |
| O-04 | Merge record of PR #236 (this renter's prior merge) | mergedAt 2026-09-30T21:05:03Z, mergedBy app/cursor, reviews=[], reviewDecision=''. | E2 | Shows GitHub permitted the merge with no recorded approving review. Does not show why. |
| O-05 | Protection and ruleset readability | GET /branches/master/protection -> 403 for this token. Rulesets: 24144685 (active, 'Block new high-severity CodeQL findings on master') and 19244487 (disabled, Copilot review). rules/branches/master returns one rule type: code_scanning. | E2 | Classic branch protection is unreadable here. The rules API lists ruleset rules only, so it neither confirms nor denies classic protection. |
| O-06 | Checks that ran on the PR #236 head | 18 entries. Inferred required set of 14 = 24-RTC Learning gate, Agent build PoC, Analyze (actions/javascript-typescript/python/rust), Dependency firewall, GitGuardian, Require PR provenance, zero-trust admission, cli-package-check, gui-check, lint-and-test (3.11/3.12). Vercel checks and the skipped CodeQL entry are excluded. | E3 | Inference: the required list itself is unreadable. NOW.md@8c6d22f2 says 14 named checks. |
| O-07 | Production deploy workflow on the latest master push | Run 36777088537 on 65975a12 (2026-09-30T21:05Z) and run 36786135007 on 8c6d22f2 (2026-09-30T22:32Z): 'Authorize production invocation' success; 'Deploy authorized production change' FAILED at step 'KPGS Azure credential preflight' both times. The step checks AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_SUBSCRIPTION_ID and emits the KPGS_DEPLOY_HOLD error path; in run 36777088537 its env block shows AZURE_CLIENT_ID and AZURE_TENANT_ID empty. Earlier: 2fae1480 success, d6126890 success, a469ebbe failure. | E2 | AZURE_SUBSCRIPTION_ID value state was not captured. The failure is upstream of any code deployment, so it is not caused by the #236 or #237 content (FAILURE_SURFACED_BY_CALL != FAILURE_CAUSED_BY_CHANGE). |
| O-08 | PR provenance gate behavior on the latest master push | Push runs for 65975a12 (2026-09-30T21:05Z) and 8c6d22f2 (2026-09-30T22:32Z) success; pull_request runs for c4ce3140, 46b04d40, c45e5bb0, 9827ae7b, ac45bd31 success. Workflow text states enforcement still requires protection or ruleset settings. | E2 | Proves detection behavior only. |
| O-09 | Cross-repository reads (read-only) | KMEC#15 -> 403 (not accessible). PKA#18 -> 404 (not accessible). Project-Jennifer#78 closed 2026-09-13T14:46:16Z. Project-Jennifer#82 merged 2026-09-11T20:48:35Z, merge commit 425710670f8f5c0242f8fc3879967b91f39bf6fc, and apps/api/src/server.ts at that commit has blob 3d341f26507219a8e76fb4f2bfcffd9fdff2f66e. Kopano-Labs-Interns#12 open. KasiLink#15 open. Bookit-5s-Arena#33 open draft, mergeable=CONFLICTING, mergeStateStatus=DIRTY, updated 2026-09-09; Bookit #39 #40 #41 #44 merged; #43 open draft. | E2 | 403/404 mean UNKNOWN, not absent. |
| O-10 | Repository visibility and tracked-file inventory | Repository visibility PUBLIC. 5,660 tracked files. .CLI_Project/ holds 3,419 (60.4%) and contains a tracked Python virtual environment (site-packages). Schematics/.smart-env (437) and Schematics/.obsidian (84) are tool-generated. Reviewable doctrine and implementation population is about 1,720 files. | E2 | Classification by path pattern; the generated directories were not opened. |
| O-11 | Protected-material flag: tracked file named like credential backups (metadata only) | Structure/discord_backup_codes.txt is tracked on master (221 bytes), added in commit a44d3fb8 on 2026-08-30 by RobynAwesome, in a PUBLIC repository. Content NOT opened (issue #122 hard exclusion). No open issue tracks it. | E2 | Content unknown; the name and size are consistent with a set of account backup codes. If real, they have been public since 2026-08-30. Owner action recommended below; no renter action taken. |
| O-12 | Content-blind credential-pattern scan of tracked non-generated files | 3 files matched: Schematics/.obsidian/plugins/obsidian-excalidraw-plugin/main.js (third-party bundle, 3 matches of one Google-key-shaped pattern), docs/swarm-ops/logs/OZ_LATTICE_AUDIT.jsonl (32 matches of one sk- shaped pattern), tests/test_oz_lattice_protocol.py (2 matches of the same pattern; the test file defines test_api_key_exposure_detected). | E3 | Pattern hits are not proof of a live credential; the test-name evidence suggests synthetic fixtures but that is unverified. GitHub reported zero open secret-scanning alerts (NOW.md@8c6d22f2), which does not cover non-provider patterns or history. |
| O-13 | Acronym and term collisions with issue proposals | 'SAP' already means Spawn Agent Protocol (kopano-core/kopano/sap_spawn_agent_protocol.py, poc-vs-foc/sap_spawn_log.jsonl, poc-vs-foc/alp_protocol/KPCB_OVERRIDE_LOG_RTCP.md, docs/BPSP_GSPMB_ARCHITECTURE.md); issue #183 defines SAP as Structured Agency Protocol. 'Orchard' already appears as MMAO = Mobile Multi-Agent Orchard (KPGS_THESIS_MMAO.md), 'MMAO Orchard' and KHELOS 'Orchard witness'; issue #115 proposes a Forge Orchard Protocol that no file defines. | E2 | Collision means the name needs RTC resolution before adoption; it does not show either usage is wrong (LEARNING_SPEC: protocol-name conflicts are resolved from GSMB). |
| O-14 | Vocabulary variances inside canon | PKA verdict enum appears as ALLOW/HOLD/BLOCK (pka_kmec_jennifer_bridge.py, 4-organ charter, flagship charter) and PROPOSE/HOLD/BLOCK (constitution, 7-vector charter). Admission state appears as READY_FOR_POC (Temporal Data testament) and READY_FOR_BOUNDED_TEST (issue #231). GSMB expands to 'Governance System Main Brain' (SSE lock, KPGS_CHEAT_SHEET, JIRO retrospective) and to 'Governance Smart Model Brain' (GSMB-Issues/index.md line 2). FOC has three senses in use: Field of Concepts (constitution), Failure of Concept (FOC_CLASSIFICATION_INDEX and SSE lock), Full Operational Capability (GSMB-Issues fork scores). | E2 | No sealed file reconciles these; this ledger cites them and does not choose. |
| O-15 | Seat 10 / Chief Facilitator records, in date order | 2026-06-23 BREACH-008 (FOC_CRITICAL, FOC_UNANIMOUS_10_OF_10): AntiGravity demoted CF -> DEV, seat_10_status OPEN_VACANT. 2026-09-05 issue #121: Seat 10 CF authority suspended/quarantined, no self-reinstatement. 2026-09-11 learning spec: orchestration chain Forge CA, Cursor CF, AntiGravity Lead Developer. 2026-09-15 PR #166 merged ('promote Cursor to CF'). Issue #167 question 3 asked whether #166 should be blocked; no RTC answer artifact exists on master. | E2 | Records conflict on Seat 10 state. No adjudication is made here. Current human direction (Forge CA brief relayed 2026-09-30) places Forge CA and Cursor CF as operational ranks, not RTC identity seats. |
| O-16 | Artifacts named by issues or sources that are absent from master | Absent: docs/governance/CA_ESTATE_AUDIT_2026-09-07_VERCEL_HTTP.md (cited by #122); RTC_INQUEST_2026-09-11_FORGE_PROJECT_JENNIFER (required by #167); Schematics/24-RTC Learning/PROMOTION_PROTOCOL.md (#115); Forge Orchard Protocol definition (#115). Present: poc-vs-foc/RTC_BREACH008_AG_DEMOTION.json, docs/swarm-ops/incidents/FORGE_LEAD_NODE_TRUTH_FAILURE_2026-09-11.{md,json}, governance/kpgs-vnext/mzansi-language/ (4 schemas + README). | E2 | Search-bound negatives; absence from this checkout is not absence everywhere. |
| O-17 | Mzansi PR1 schemas re-validated | All four schemas pass Draft 2020-12 check_schema. | E2 | Structure only; no dataset, model, or runtime claim. |
| O-18 | Who closed the ESLint-adjacent Dependabot PRs | #198, #201 and #204 were each closed by dependabot[bot] on 2026-09-28 (18:16:24Z, 18:16:27Z, 18:16:31Z). #199 #200 #202 #203 merged 2026-09-29T06:19:15Z with the integration PR #213. | E2 | Dependabot's reason for closing is not recorded in the issue. |
| O-19 | Who authors agent pull requests | PRs #233, #234, #235 and #236 show author RobynAwesome; Dependabot PRs show app/dependabot. | E2 | Used only for hypothesis H1 in finding F-1. |
| O-20 | Owner merge of Dependabot PR #237 with no approving review | Merged 2026-09-30T22:32:09Z by RobynAwesome (the human owner), merge commit 8c6d22f2. reviews=[], reviewDecision=''. Events: labeled, two Vercel deployments, merged, closed, head ref deleted by dependabot[bot]. No approval event. | E2 | Does not show whether the owner used a bypass right or whether no review rule applied. Together with O-04 it means two different actors merged without a review within 90 minutes. |

## 5. Findings (detail)

### F-1 The approving-review requirement is not observably in force (recurrence)

NOW.md@8c6d22f2:L56 records that at recovery required_pull_request_reviews was null, that Forge restored one approving review on 2026-09-30, and that removal attribution is UNKNOWN. Afterwards two different actors merged with no review: this renter's PR #236 at 21:05:03Z (O-04) and the owner's own merge of PR #237 at 22:32:09Z (O-20). Open PR #238 reports CLEAN with no review decision, and open PR #239 is BLOCKED while its review decision is also empty, so what blocks it is not a review requirement (O-03). Protection is unreadable here (O-05), so the current setting is UNKNOWN; the PR metadata says no approving review is gating merges. Two instructions now point different ways: NOW.md tells every agent to preserve the review requirement, and the owner, who is final authority, merged without one. This ledger records both and resolves neither. Hypothesis H1 (E3): PRs #233-#236 are authored as RobynAwesome (O-19) and GitHub does not let an author approve their own PR, so a one-approval rule may be unsatisfiable in this repo without a second approver identity, which would explain why it keeps lapsing.

**Next action:** Forge/Robyn: read protection with an admin-scope token now; state whether the requirement is intended and, if so, who can satisfy it (second approver identity, bot approver, or a PR-required rule with zero approvals plus required checks); decide whether to log the lapse in poc-vs-foc/BREACH_LOG.md; update the NOW.md instruction to match the decision. Renter made no setting change.

### F-2 Protected-material flag: tracked Structure/discord_backup_codes.txt in a public repository

Observed by metadata only (O-11). Content was not opened. No issue tracks it and GitHub secret scanning would not recognise this kind of value.

**Next action:** Robyn: regenerate the account's backup codes now, treating the old set as exposed if the file is what its name suggests. Then decide on removal from HEAD and on history remediation (a force-push to protected master is outside renter authority).

### F-3 #207 is not ready to close; owner-closeable set is #205 only

Detection behavior is validated (O-08). Settings-level prevention is HOLD: the recorded direct-push rejection (NOW.md@8c6d22f2:L74) is consistent with ruleset 24144685's code_scanning rule, and GH013 is the repository-rule-violation family, so it does not by itself show PR-required or review-required enforcement (O-05). The plan listed #205, #207, #163 and #122 as closeable; evidence supports #205 only.

**Next action:** Owner decision per issue; see register.

### F-4 #163 artifact is delivered but its own status is OPEN with no exit criteria

Commit 1219c994 (#164) put the .md and .json on master. Both say status OPEN / OPEN INCIDENT; a search of the artifact for exit, closure, or re-entry terms found none.

**Next action:** RTC/owner: define incident exit criteria or decide that the tracker issue may close while the artifact stays OPEN.

### F-5 #183's link to #121/#167 is an inference, and its acronym collides

#183's text contains no reference to #121, #167, recusal, NSO-001, Seat 10, quarantine, or suspension. #167 question 6 asks RTC how NSO-001 should be enforced mechanically and is unanswered. Separately SAP already means Spawn Agent Protocol in this repo (O-13); existing authority_scope string fields exist in callable_artifact_registry.py and pka_kmec_jennifer_bridge.py and should be reused or extended, not duplicated.

**Next action:** RTC Design Review: decide the name, whether SAP is a candidate mechanism for #167 question 6, and reuse of authority_scope.

### F-6 #211 HOLD persists after the latest merge

Runs 36777088537 (65975a12) and 36786135007 (8c6d22f2) both failed at the Azure credential preflight (O-07). Same boundary as the 2026-09-15 and 2026-09-19 failures in the issue. Every production-affecting merge, including the owner's own #237, now produces a red deploy run until the secrets exist.

**Next action:** Robyn: provide AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_SUBSCRIPTION_ID to GitHub Actions secrets and verify the federated identity (issue #211 steps 1-4).

### F-7 #158's pull request is stale and its direction may be superseded

Bookit PR #33 is open draft, CONFLICTING/DIRTY (O-09). Customer-first public-surface work merged after it (Bookit #39 and #40 and #41 on 2026-09-14, #44 on 2026-09-28).

**Next action:** Robyn: decide whether the epoch relaunch is still intended; if yes, rebase is required before inspection.

### F-8 #122's cited receipt is absent and it is the declared parent audit of eight issues

docs/governance/CA_ESTATE_AUDIT_2026-09-07_VERCEL_HTTP.md is not on master (O-16). #94, #102, #103, #107, #110, #115, #116 and #121 each carry a 2026-09-07 comment 'Parent audit: #122'. Its 22-repo list includes cars4mars-landingpage, which the Kopano-Labs-Website AGENTS.md calls retired (as supplied in the session instructions; that file was not re-read from disk).

**Next action:** Owner: keep #122 open as umbrella until an owner-local census exists; the cloud-subset observation in Wave 2 is additive.

### F-9 #167 question 3 was open when PR #166 merged

PR #166 merged 2026-09-15T01:41:25Z. No RTC answer artifact exists on master (O-15, O-16). Current CF assignment therefore rests on Robyn's current direction and #166, as an operational rank only.

**Next action:** RTC/Robyn: record disposition of #167 questions 1-7. This ledger does not adjudicate them.

### F-10 Third-party and generated material dominates the tracked tree

69.6% of tracked files (3,940 of 5,660) are a committed virtual environment or tool-generated (O-10). They are classified third_party_generated in the coverage CSV and are not counted as reviewed doctrine.

**Next action:** Owner decision on untracking; not attempted.

### F-1 failure trace

`failure -> cause -> existing control -> invocation -> enforcement -> receipt -> recurrence`

| Step | Record |
|---|---|
| Failure | Master accepted merges with no recorded approving review. |
| Cause | UNKNOWN. `NOW.md@8c6d22f2:L56` says removal attribution is UNKNOWN; protection is unreadable to this token (O-05). Hypothesis H1 (E3): one-approval rule is unsatisfiable when agent PRs are authored as the sole owner (O-19). |
| Existing control | Classic branch protection with one required approving review (Forge readback, attributed). Ruleset `24144685` gates new high CodeQL findings only (O-05). |
| Invocation | PR merge by `app/cursor` at 2026-09-30T21:05:03Z (O-04) and by the owner `RobynAwesome` at 22:32:09Z (O-20). |
| Enforcement | Both merges permitted with no review. Open PR #238 reports `CLEAN` and open PR #239 is `BLOCKED`, both with an empty review decision (O-03). |
| Receipt | O-03, O-04, O-05, O-20 here; Forge's before/after readbacks are local and UNAVAILABLE (section 10). |
| Recurrence | At least two episodes: the null state found at recovery (PRs #232 and #233 merged with empty review lists), and the state observed after Forge's restoration (two merges by two actors). |

## 6. Issue register

Tag vocabulary is a proposed working classification (section 9). PKA verdicts use the `ALLOW/PROPOSE` spelling to cover the canon variance (O-14).

| Issue | Clusters | Baseline (2026-09-07) | Tag | PKA | Owner-closeable | Next admissible action (actor) |
|---|---|---|---|---|---|---|
| [#94](https://github.com/RobynAwesome/Introduction-to-MCP/issues/94) | CL-C child of #122; CL-E owner-gated | MAYBE / OPEN; own triage: not closable | UNKNOWN | HOLD | No (issue says it is not closable) | Robyn supplies the second registry name or URL; otherwise Wave 2 records what a bounded search of RobynAwesome/Skills finds. A miss is not negative proof. Actor: Robyn (names the registry) or renter (Wave 2 bounded repo-scoped re-search). |
| [#102](https://github.com/RobynAwesome/Introduction-to-MCP/issues/102) | CL-C child of #122; related KasiLink#15 | Witness slice POC_VALIDATED; remainder HOLD | HOLD_HUMAN | HOLD | No | Wave 2 re-observes public HTTP read-only. KasiLink#15 runtime repair, apex/www convergence, and the Starfall rollback drill remain human or provider gated. No domain mutation. Actor: Robyn / provider-domain owner; renter for read-only re-observation. |
| [#103](https://github.com/RobynAwesome/Introduction-to-MCP/issues/103) | CL-F implementation; child of #122 | PR1 merged; PR2 not started | POC_PENDING | HOLD | No | Wave 2: confirm admission basis, then PR2 = record persistence plus provenance, consent and validation state plus synthetic fixtures. No real data, no TTS, no multi-language expansion. Actor: Renter (bounded PR2 slice after teach-back) ; Forge/RTC for admission confirmation. |
| [#107](https://github.com/RobynAwesome/Introduction-to-MCP/issues/107) | CL-F implementation; child of #122; cross-repo KMEC#15, PKA#18, Jennifer#78 | Architecture capture only; PR1-PR7 unbuilt | POC_PENDING | HOLD | No | Wave 2: Design Review packet with an overlap audit first, because PR1 (contracts and fixtures) overlaps existing assets and the unreadable PKA/KMEC lanes. No schema code before the contract owner is named. Actor: Forge CA / RTC Design Review; then renter. |
| [#110](https://github.com/RobynAwesome/Introduction-to-MCP/issues/110) | CL-F implementation; child of #122 | Pointer retired; branch dirty local; Studio QA open | POC_PENDING | HOLD | No | Wave 2: Studio-versus-plan audit document classifying each plan item implemented / stale / blocked / actionable. Browser QA and UX fixes stay separate runtime lanes. Actor: Renter (audit document) ; owner or browser-capable lane (QA). |
| [#115](https://github.com/RobynAwesome/Introduction-to-MCP/issues/115) | CL-B Classroom; child of #122; consumer boundary Interns#12 | LEARNING / not ratified; protocol undefined on cloud head | POC_PENDING | HOLD | No | Wave 2: Task 1 only (overlap table over cloud-head promotion surfaces) plus an admission packet for Tasks 2-5. Do not reconstruct section 24 from local narratives (issue triage rule). Actor: Renter (Task 1 audit) ; RTC (Tasks 2-5 admission). |
| [#116](https://github.com/RobynAwesome/Introduction-to-MCP/issues/116) | CL-B Classroom; child of #122 | LEARNING / not ratified; RTC discussion | HOLD_HUMAN | HOLD | No | Wave 2: Cursor CF assembles the RTC discussion source packet only. No seat opinion is written by the renter; unavailable seats stay recorded as unavailable. Actor: RTC seats (independent positions) ; Forge CA (disagreement map) ; Cursor CF (source packet). |
| [#121](https://github.com/RobynAwesome/Introduction-to-MCP/issues/121) | CL-A RTC incident; child of #122 | P0 OPEN; quarantined until independent re-entry or decommission | HOLD_HUMAN | HOLD | No | Gate A (independent re-entry receipts) or gate B (Tier-0 decommission). Renter records sources and dates only. Actor: RTC and Robyn (Tier 0). |
| [#122](https://github.com/RobynAwesome/Introduction-to-MCP/issues/122) | CL-C parent audit of #94 #102 #103 #107 #110 #115 #116 #121 | Dated umbrella audit; 0 of 7 acceptance boxes checked | POC_PENDING | HOLD | No (recommend keep open as umbrella) | Wave 2: fresh read-only cloud-subset receipt (GitHub identities, default-branch SHAs, open PRs, CI-at-head for the 22 repos, unreadable rows marked UNKNOWN). Boxes 3 and 4 remain human or provider gated. Owner decides close versus keep. Actor: Renter (cloud subset) ; Robyn (local census, Vercel alias). |
| [#158](https://github.com/RobynAwesome/Introduction-to-MCP/issues/158) | CL-E owner-gated; Bookit-5s-Arena | Not in the 09-07 table; receipt 2026-09-09 (draft PR #33) | HOLD_HUMAN | HOLD | No | Decide whether the epoch relaunch is still intended. If yes, rebase PR #33 before owner inspection. No merge or deploy by a renter. Actor: Robyn. |
| [#163](https://github.com/RobynAwesome/Introduction-to-MCP/issues/163) | CL-A RTC incident | Not in the 09-07 table (opened 2026-09-11) | POC_VALIDATED | ALLOW/PROPOSE (named claim only) | Owner/RTC decision; not recommended while the artifact says OPEN | Define incident exit criteria, or decide the tracker issue may close while the artifact stays OPEN. Renter does not adjudicate. Actor: RTC / Robyn. |
| [#167](https://github.com/RobynAwesome/Introduction-to-MCP/issues/167) | CL-A RTC incident; related PR #166 | Not in the 09-07 table (opened 2026-09-11) | HOLD_HUMAN | HOLD | No | RTC produces RTC_INQUEST_2026-09-11_FORGE_PROJECT_JENNIFER and answers questions 1-7. Forge may not self-adjudicate; Cursor may not either. Actor: RTC seats; Robyn (Tier 0). |
| [#183](https://github.com/RobynAwesome/Introduction-to-MCP/issues/183) | CL-G authority runtime; candidate link to CL-A (inference) | Status PROPOSED / POC-FIRST; 0 comments; 35 boxes unchecked | POC_PENDING | HOLD | No | Wave 2: Design Review admission packet (teach-back, doctrine trace, acronym-collision decision, authority_scope reuse, acceptance checks, rollback boundary). Code for POC steps 1-4 only after READY_FOR_POC or stronger. Actor: RTC Design Review; Forge CA (evidence and disagreement map); then renter. |
| [#205](https://github.com/RobynAwesome/Introduction-to-MCP/issues/205) | CL-D repository boundary / deploy | Not in the 09-07 table (opened 2026-09-23) | POC_VALIDATED | ALLOW/PROPOSE (named claim only) | Yes: owner may close after reading claims C-205-1 to C-205-3 | Owner may close. Limits to read first: #198 and #201 and #204 were closed by Dependabot without a recorded rationale; #202's upload/download and runner-fleet check was not performed. New Dependabot PRs #237 and #238 are outside this issue. Actor: Robyn (close). |
| [#207](https://github.com/RobynAwesome/Introduction-to-MCP/issues/207) | CL-D repository boundary / deploy | Not in the 09-07 table (opened 2026-09-24); DETECTION_GATE POC_VALIDATED_ON_MASTER; SETTINGS_LEVEL_PREVENTION HOLD | HOLD_HUMAN | HOLD | No | Read protection and all rulesets with an admin-scope token; decide whether the approving-review rule is intended and who can satisfy it; decide on a drift check (new governance mechanism: RTC admission). Renter changed no setting. Actor: Forge CA and Robyn (admin-scope readback and decision). |
| [#211](https://github.com/RobynAwesome/Introduction-to-MCP/issues/211) | CL-D repository boundary / deploy | Not in the 09-07 table (opened 2026-09-24) | HOLD_HUMAN | HOLD | No | Provide AZURE_CLIENT_ID, AZURE_TENANT_ID and AZURE_SUBSCRIPTION_ID to GitHub Actions secrets, verify the federated identity, re-run an authorized deploy, and require a run receipt with Azure login PASS and azd up PASS. Renter does not handle secret values. Actor: Robyn (secrets and federated identity). |
| [#231](https://github.com/RobynAwesome/Introduction-to-MCP/issues/231) | CL-E owner-gated | Not in the 09-07 table (opened 2026-09-28); state LEARN -> READY_FOR_BOUNDED_TEST | HOLD_HUMAN | HOLD | No | Run the bounded field lane only when authorized; preserve denominator, declines, corrections and seven-day second-contact outcomes. No agent contacts drivers. Actor: Robyn (consenting-driver field lane); Cassey (separate review). |

## 7. Claim register

Each row names one claim and the tag for that claim. `POC_VALIDATED` rows say exactly what was validated; the **limits** column says what was not.

| Claim | Issue | Claim (family, class) | Tag | Receipts | Limits |
|---|---|---|---|---|---|
| C-94-1 | #94 | A second external skill registry with fuller Project Jennifer / PKA presence exists. (Declarative, E1) | UNKNOWN | issue #94 body (testimony as recorded); issue #94 comment 2026-09-07: no second registry proven | Testimony proves the statement was made, not that the registry exists. |
| C-94-2 | #94 | RobynAwesome/Skills is not the second registry. (Empirical, E4) | UNKNOWN | issue #94 body: must not be assumed | Wave 2 re-search is bounded and cannot close the issue. |
| C-102-1 | #102 | Starfall Salvage public DNS, Vercel ownership, READY deployment and rollback candidates were witnessed on 2026-08-24. (Empirical, E2) | UNKNOWN | issue #102 body; issue #122 table classifies this slice POC_VALIDATED (2026-09-07); cited receipt file absent from master (O-16) | Attributed and dated; receipt not on master; not re-observed here. |
| C-102-2 | #102 | KasiLink apex/www remain split and its three data routes returned HTTP 500 (6 of 6 on 2026-09-07). (Empirical, E2) | HOLD_HUMAN | issue #102 comment 2026-09-07; KasiLink#15 open (O-09) | A public 500 does not prove the Atlas auth cause. |
| C-103-1 | #103 | PR1 contracts are on master: four JSON Schemas (Draft 2020-12) and a README under governance/kpgs-vnext/mzansi-language/. (Empirical, E2) | POC_VALIDATED | PR #105 merge b994272453d7... per issue #103 comment 2026-08-24; 5 tracked files (O-16); check_schema OK x4 re-run 2026-09-30 (O-17) | CLAIM VALIDATED: contract structure and persistence only. No dataset, model, speech, native-speaker, or runtime claim. |
| C-103-2 | #103 | PR2 (Mzansi Data Engine foundation) has not started. (Empirical, E2) | POC_PENDING | issue #103 comment 2026-09-07; no engine or persistence file under mzansi paths (O-16) | Search-bound negative. |
| C-107-1 | #107 | The observation engine itself (parser, box and scatter reasoning, Dask) is unbuilt on master. (Empirical, E2) | POC_PENDING | issue #107 comment 2026-09-07; name search finds kmec_trace_adapter.py, pka_kmec_jennifer_bridge.py and two test files, FEP_POC_003 and KMEC convergence docs, but no engine | Adjacent assets exist and must be reused, not duplicated. Search-bound. |
| C-107-2 | #107 | PR1 (contracts plus DNS/backend fixtures) is an admitted slice. (Declarative, E2) | POC_PENDING | issue #107 body 'Proposed implementation sequence' | Labeled proposed in the issue; not admitted. |
| C-107-3 | #107 | Cross-repo lanes KMEC#15 and PKA#18 are open and carry the parser and Smart Ledger contracts. (Empirical, E4) | UNKNOWN | KMEC#15 -> 403; PKA#18 -> 404 (O-09); Project-Jennifer#78 closed 2026-09-13 (O-09) | Unreadable is not absent. |
| C-110-1 | #110 | The stale codex/kc-sovereign-gui-full-dev open-PR pointer was removed from canonical navigation. (Textual, E2) | POC_VALIDATED | docs/swarm-ops/NAVIGATION.md line 22 (Issue #110 pointer) and line 43 (branch is historical testimony only) | CLAIM VALIDATED: documentation pointer repair only. The other seven boxes are open. |
| C-110-2 | #110 | Studio-versus-plan audit, browser QA and bounded UX fixes. (Empirical, E4) | POC_PENDING | issue #110 comment 2026-09-07: starts from master | Runtime QA needs a running Studio. |
| C-115-1 | #115 | Task 1 (audit of current promotion surfaces into an overlap table) can be done from cloud head without new vocabulary. (Empirical, E3) | POC_PENDING | issue #115 Task 1 text; issue #115 triage 2026-09-07: cloud-head section 24 must not be reconstructed from local narratives | Audit only; it must not create a second owner for governed concepts. |
| C-115-2 | #115 | Tasks 2-5 (PROMOTION_PROTOCOL.md, export receipt schema, consumer gates, promotion dry-run) are admissible now. (Declarative, E2) | HOLD_HUMAN | issue #115 triage: Forge Orchard Protocol is not ratified; PROMOTION_PROTOCOL.md absent (O-16) | Needs RTC admission; the dry-run must prove no writes through SQLite, JSONL, forensic, Main Brain and handoff paths. |
| C-116-1 | #116 | A Temporal Manhole POC is admitted. (Declarative, E2) | HOLD_HUMAN | issue #116 status: LEARNING / RTC DISCUSSION CANDIDATE - NOT RATIFIED; issue #116 triage 2026-09-07: no POC admitted | Discussion before metal. |
| C-121-1 | #121 | Seat 10 Chief Facilitator authority is suspended; exit is gate A or gate B; no self-clearing. (Declarative, E1) | HOLD_HUMAN | issue #121 comment 2026-09-07; issue #121 body status | Not adjudicated here. |
| C-122-1 | #122 | The cloud-verifiable subset of the 22-repo audit can be refreshed read-only. (Empirical, E3) | POC_PENDING | issue #122 body acceptance list; cross-repo reads partially 403/404 (O-09) | Local census and Vercel alias re-proof are not cloud-verifiable. |
| C-122-2 | #122 | The 2026-09-07 Vercel/HTTP receipt file exists. (Textual, E2) | UNKNOWN | issue #122 last comment cites docs/governance/CA_ESTATE_AUDIT_2026-09-07_VERCEL_HTTP.md; absent from master (O-16) | The 09-07 HTTP and Vercel statements are attributed only. |
| C-158-1 | #158 | PR #33 implements the neutral relaunch; 10/10 epoch tests, tsc clean and build pass (2026-09-09). (Empirical, E2) | UNKNOWN | issue #158 comment 2026-09-09; Bookit #33 open draft CONFLICTING/DIRTY (O-09) | Attributed; not re-run here; base has moved. |
| C-158-2 | #158 | The park-and-relaunch direction is still the intended public-surface direction. (Declarative, E2) | HOLD_HUMAN | Bookit #39 #40 #41 (2026-09-14) and #44 (2026-09-28) merged (O-09) | Owner decision. |
| C-163-1 | #163 | The incident artifacts (md and json) are on master and preserve history. (Empirical, E2) | POC_VALIDATED | commit 1219c994 (2026-09-15) 'incident: record Forge lead-node truth/provenance failure (#164)'; blob fd822648d9186a62c9f39fd816c2431c7453f5da (md); blob 80548ac7abd46514edc971bda5bc83040c7b076d (json); json: status OPEN, downstream_709_agent_propagation_confirmed false, repository_net_file_damage_after_cleanup none_known | CLAIM VALIDATED: artifact delivery only. It does not validate incident closure, corrected behavior, or propagation extent. |
| C-163-2 | #163 | Incident exit criteria are defined. (Textual, E2) | HOLD_HUMAN | search of the .md for exit/closure/re-entry terms found none (F-4) | Search-bound negative. |
| C-167-1 | #167 | The required RTC inquest deliverable exists. (Textual, E2) | HOLD_HUMAN | name search over tracked files returns nothing (O-16) | Search-bound negative. |
| C-167-2 | #167 | Project Jennifer recovery PR #82 restored the pre-Arena server.ts. (Empirical, E2) | POC_VALIDATED | Project-Jennifer PR #82 merged 2026-09-11T20:48:35Z, merge commit 425710670f8f5c0242f8fc3879967b91f39bf6fc; apps/api/src/server.ts blob 3d341f26507219a8e76fb4f2bfcffd9fdff2f66e at that commit (O-09) | CLAIM VALIDATED: recovery merge and file blob only. It does not clear the offense or assert Jennifer production state. |
| C-167-3 | #167 | Question 3 (should #166 be blocked, amended or superseded) was answered before #166 merged. (Textual, E2) | UNKNOWN | PR #166 merged 2026-09-15T01:41:25Z; no answer artifact on master (O-15, O-16) | Absence from master is not absence of an RTC answer elsewhere. |
| C-183-1 | #183 | SAP runtime law (AuthorityScope over AnyIO) exists. (Empirical, E2) | POC_PENDING | no AuthorityScope class found; authority_scope is a string field in callable_artifact_registry.py and pka_kmec_jennifer_bridge.py; anyio appears only inside the tracked third-party virtual environment (O-10); SAP already means Spawn Agent Protocol (O-13) | Search-bound negative. |
| C-183-2 | #183 | SAP is the mechanism for #121/#167 recusal and NSO-001 enforcement. (Declarative, E3) | UNKNOWN | #183 text contains no reference to #121, #167, recusal, NSO-001 or Seat 10 (F-5); #167 question 6 unanswered | Candidate link by Cursor CF inference. Not an admitted dependency. |
| C-205-1 | #205 | The ESLint 10 pair migration landed with a regenerated studio lockfile. (Empirical, E2) | POC_VALIDATED | kopano-core/studio/package-lock.json at 8c6d22f2 (blob ad46697a9e20..., same at 65975a12): eslint 10.11.0, @eslint/js 10.0.1; PR #200 merged 2026-09-29T06:19:15Z; NOW.md 2026-09-29 block: local studio proof and hosted gui-check | CLAIM VALIDATED: dependency repair in the studio lockfile. Root and apps/kc-dashboard locks carry no eslint entries. |
| C-205-2 | #205 | Dispositions of #198-#204: merged #199 #200 #202 #203; closed unmerged #198 #201 #204. (Empirical, E2) | POC_VALIDATED | gh pr view 198..204 (O-18); #198 #201 #204 closed by dependabot[bot] 2026-09-28 | CLAIM VALIDATED: PR disposition record. Rationale for the three Dependabot closures is not recorded. |
| C-205-3 | #205 | #202's actions/upload-artifact 4 -> 7 was verified by an actual artifact upload/download and runner-fleet check. (Empirical, E2) | UNKNOWN | NOW.md@8c6d22f2 2026-09-29 block: a separate manual artifact download was not performed; required checks that run upload-artifact@v7 passed | Upload paths exercised in CI; download and runner-fleet compatibility not exercised. |
| C-207-1 | #207 | The Require PR provenance gate behaves as designed. (Empirical, E2) | POC_VALIDATED | .github/workflows/kpgs-branch-proof-gate.yml; issue #207 production receipt 2026-09-24; push runs on 65975a12 and 8c6d22f2 success (O-08); check 'Require PR provenance' pass on PR #236 (O-06) | CLAIM VALIDATED: detection behavior. It detects; it does not prevent. |
| C-207-2 | #207 | Direct pushes to master are prevented at the settings boundary. (Empirical, E2) | HOLD_HUMAN | NOW.md@8c6d22f2:L74: a direct push was rejected until CodeQL and the 14 required checks existed; ruleset 24144685 active with a code_scanning rule (O-05); branch protection unreadable (403) | GH013 is the repository-rule-violation family; the rejection is consistent with the code_scanning rule and does not alone show PR-required enforcement. Rejection text not preserved in the cloud record. |
| C-207-3 | #207 | Master requires one approving review before merge (restored by Forge on 2026-09-30). (Empirical, E2) | FOC_RISK | NOW.md@8c6d22f2:L56 and L235 (attributed to Forge readback); contradicting observations: O-04 (#236 merged with no review), O-20 (#237 merged by the owner with no review), O-03 (#238 CLEAN and #239 BLOCKED, both with no review decision) | Protection is unreadable here; inference from PR metadata only; includes this renter's own merge of #236. The owner's merge shows the requirement is not binding in practice, not that it was removed on purpose. |
| C-211-1 | #211 | The production deploy still fails at the Azure credential contract. (Empirical, E2) | POC_VALIDATED | run 36777088537 on 65975a12 and run 36786135007 on 8c6d22f2: 'Deploy authorized production change' failed at 'KPGS Azure credential preflight' (O-07) | CLAIM VALIDATED: failure persistence only. It is the HOLD condition, not a fix. Not caused by the #236 or #237 content. |
| C-211-2 | #211 | Required closure (secrets restored, identity verified, authorized deploy run, azd up PASS). (Declarative, E1) | HOLD_HUMAN | issue #211 'Required closure' steps 1-4 | Owner-held. |
| C-231-1 | #231 | The operator field kit is on master. (Empirical, E2) | POC_VALIDATED | docs/product-discovery/issue-231/: FIELD-KIT.md, PEER-REVIEW.md, PREPARATION-RECEIPT.md, README.md, TEACHER-REVIEW.md, private-ledger/; PR #232 merged per NOW.md@8c6d22f2 | CLAIM VALIDATED: artifact delivery only. No driver outcome, consent, or field completion is asserted. |
| C-231-2 | #231 | A driver-owned WhatsApp shift receipt test was run. (Empirical, E1) | HOLD_HUMAN | issue #231 boxes 0 of 5 checked | Human field lane; needs consent. |

## 8. Clusters and connections

```mermaid
flowchart TD
  subgraph A [CL-A RTC incident]
    i163["#163 artifact"] --- i167["#167 inquest"]
    i121["#121 Seat 10"] --- i167
  end
  subgraph G [CL-G authority runtime]
    i183["#183 SAP proposal"]
  end
  i167 -.->|"inference only"| i183
  subgraph B [CL-B Classroom]
    i115["#115 promotion"] --- i116["#116 temporal"]
  end
  subgraph C [CL-C umbrella]
    i122["#122 parent audit"]
  end
  i122 --- i94["#94"]
  i122 --- i102["#102"]
  i122 --- i110["#110"]
  i122 --- i121
  subgraph D [CL-D boundary and deploy]
    i205["#205"] --- i207["#207"]
    i207 --- i211["#211"]
  end
```

Link strength: `textual` (an issue cites the other), `artifact` (shared file or SHA), `thematic` (same control surface or gate holder), `inference` (Cursor CF proposal, not admitted).

| ID | Cluster | Members | Link strength | Evidence of the link |
|---|---|---|---|---|
| CL-A | RTC incident | #163 #167 #121 | textual | #167 cites #163/#164 and #121 in its body; #121 names #122 as parent audit. |
| CL-B | Classroom / 24-RTC Learning | #115 #116 Interns#12 | artifact | Both issues live in Schematics/24-RTC Learning; #115 names Kopano-Labs-Interns as a consumer; candidate dry-run artifact for #115 Task 5 is the Temporal Data testament that #116 discusses (inference, RTC to choose). |
| CL-C | Estate observation umbrella | #122 (parent) of #94 #102 #103 #107 #110 #115 #116 #121 | textual | Each of the eight carries 'Parent audit: #122' in a 2026-09-07 comment; #122's body table also classifies #94 #102 #103 #107 #110 #115 #116 #121. |
| CL-D | Repository boundary / deploy | #205 #207 #211 | thematic | #205 and #207 share base SHA 617092ce and the stale-NOW reconcile item (textual); #211 is the same control surface one step later (a merge triggers the deploy workflow). |
| CL-E | Owner-gated external lanes | #158 #231 #94 | thematic | Each next step is held by the owner, a provider, or a consenting human; none is renter evidence. |
| CL-F | Implementation lanes | #103 #107 #110 | textual | Each issue defines its own bounded next slice; #107 is tied to KMEC#15, PKA#18, Jennifer#78. |
| CL-G | Authority runtime | #183 (candidate link to CL-A) | inference | #183 text has no reference to #121/#167. Only hook: #167 question 6 (mechanical NSO-001 enforcement), unanswered. |

## 9. POC/FOC groups

The groups document `ISSUE_POCFOC_GROUPS_2026-09-30.md` (path and mirror in its header) cross-references the existing `FOC-G01` to `FOC-G08` groups against the issues and keeps the five working tags visible as **proposed**:

| Tag | Meaning (proposed) | PKA mapping (proposed) |
|---|---|---|
| POC_VALIDATED | Evidence for the NAMED claim exists on master or was re-observed in this run, with a pointer. Says nothing about any wider claim. | ALLOW/PROPOSE (named claim only) |
| POC_PENDING | A bounded slice is defined and executable; its claim is not yet evidenced. | HOLD |
| HOLD_HUMAN | The next step is gated by human authority or RTC, not by renter evidence. | HOLD |
| FOC_RISK | A claim recorded in an issue or NOW.md exceeds what current evidence supports. | BLOCK (promotion of the over-claim) |
| UNKNOWN | Evidence absent, unreadable by this token, or dated and not re-observed. | HOLD |

Result: no issue is classified under an existing FOC group as an actor failure. Two partial matches (G06 on a missing artifact: #122, #167), three context-only mentions (G02 #121, G04 #183, G07/G08 #158). A candidate group, `ControlStateDrift`, is proposed from F-1 and is not added to `poc-vs-foc/FOC_CLASSIFICATION_INDEX.md`.

## 10. Local-source recovery (brief-attested; cloud presence verified on the base)

| Source | Cloud (verified) | Local (brief-attested) | Ledger treatment |
|---|---|---|---|
| docs/governance/FOC_VS_POC_EPISTEMIC_CONSTITUTION.md (cloud mirror) | PRESENT, blob ee42cc468ea8...; line 5 carries the 'Repository Mirror' reference | Brief: canonical-local copy differs by that added line | MIRROR_DIVERGENT_BY_ONE_REFERENCE_LINE (Forge-attested). Parity UNKNOWN until the local hash is supplied. |
| Schematics/24-RTC Learning/POCvsFOC Groups/FOC_VS_POC_EPISTEMIC_CONSTITUTION.md (canonical-local path) | ABSENT | Brief: present locally | LOCAL_PRESENT / CLOUD_ABSENT. |
| Hardware Maintenance & GSMB2 Offload Protocol | ABSENT (name search finds nothing) | Brief: present locally | LOCAL_PRESENT / CLOUD_ABSENT. Documentary context only; hardware maintenance is a separate lane. |
| Schematics/19-TOKEN USAGE/AI Session Closeout Protocol.md | ABSENT | Brief and NOW.md@8c6d22f2 say inspected locally | Field list taken from NOW.md@8c6d22f2 (present in cloud); comms-log.md fallback stays permitted. |
| OpenAI Academy C.L.E.A.R. card (image) | ABSENT | Brief: visually confirms Complete, Logical, Evidence, Audience, Relevant | LEARNING_SPEC_PIPELINE (present) carries the five terms. Academy review and delivery review are kept distinct. |
| MAIN-BRAIN/CURSOR_CF_IDENTITY_DECLARATION.md | ABSENT | Brief: records CF responsibility and separates operational rank from RTC identity seat | Role packet rests on the brief, PR #166 and Robyn's current direction; declaration not cited as read. |
| Schematics/24-RTC Learning/WORKFLOWS.md | ABSENT | Brief: Classroom, Round Table, Design Review, Post-Incident workflows | Workflow names used as brief-attested until published. |
| Schematics/24-RTC Learning/PROMOTION_PROTOCOL.md | ABSENT | Brief: absent at the checked local path too | Issue #115 deliverable stands. |
| C:/Users/rkhol/Documents/Codex/2026-09-19/gsmb-house-audit/coverage.csv | n/a | Brief: saved audit coverage; full audit recorded incomplete in root NOW | UNAVAILABLE to this runtime. Cloud coverage CSV starts a parallel population with a compatible superset of columns. |
| C:/Users/rkhol/Documents/Codex/2026-09-30/agent-coordination-receipts/ | n/a | NOW.md@8c6d22f2: protection before/after readbacks and NOW backups | UNAVAILABLE. It is the source of the protection readback attributed to Forge. |

Cloud-side coverage starts a parallel population: `GSMB_HOUSE_AUDIT_COVERAGE_CLOUD_2026-09-30.csv`. Column parity with the local `coverage.csv` is UNKNOWN until its header is supplied.

## 11. Doctrine gaps observed versus proposed doctrine

**Observed in cloud (verified, section 4):** O-13 acronym and term collisions; O-14 PKA enum, admission-state spelling, GSMB expansion and FOC-sense variances; no sealed file names the Local / Cloud / Google Drive tiers (closest: the RTC council prompt lists Local GSMB, Cloud GSMB, Google Drive, Personalized Vault); no doctrine file defines GitHub issue classes (practice only, e.g. the 2026-09-07 table in #122).

**Proposed by this ledger (not admitted):**

| Item | Proposal |
|---|---|
| Five working tags | POC_VALIDATED / POC_PENDING / HOLD_HUMAN / FOC_RISK / UNKNOWN, applied per claim and summarised per issue. Prior art: the 2026-09-07 table in #122 (MAYBE, witness-slice POC_VALIDATED plus HOLD remainder, architecture capture only, LEARNING not ratified). |
| PKA mapping | POC_VALIDATED -> ALLOW/PROPOSE for the named claim only; POC_PENDING, HOLD_HUMAN, UNKNOWN -> HOLD; FOC_RISK -> BLOCK on promoting the over-claim. The enum itself varies in canon (O-14). |
| HOLD_HUMAN definition | Gate held by human authority or RTC, not by renter evidence. Wider than the plan's 'owner-only'. |
| Issue-class vocabulary | No doctrine file defines GitHub-issue classes. This ledger writes them as proposed only. |
| Candidate FOC group | ControlStateDrift (see groups doc). Not added to FOC_CLASSIFICATION_INDEX.md. |
| Integrating writer | Cursor CF for NOW.md, the ledger and closeout records during Waves 0-3, pending Forge CA acceptance. |

## 12. RTC admission state per slice

Decision states use the canon `LEARN | HOLD | TEST | READY_FOR_POC` (Temporal Data testament, section 17). Code lands only after `READY_FOR_POC` or stronger. Unavailable participants remain unavailable; nothing here writes a seat's opinion.

| Slice | Admission needed | Recorded state |
|---|---|---|
| Wave 1a repo-boundary receipt | none (observation) | not applicable |
| Wave 1b RTC-cluster receipt | none (observation; no adjudication) | not applicable |
| #115 Task 1 overlap audit | none (cloud-head observation) | not applicable |
| #115 Tasks 2-5 and PROMOTION_PROTOCOL.md | RTC Classroom / Round Table (governance vocabulary) | LEARN; decision UNRECORDED -> HOLD |
| #116 discussion | RTC independent positions | LEARN / RTC_DISCUSSION; UNRECORDED -> HOLD |
| #107 PR1 | Design Review (cross-repo contract ownership) | UNRECORDED -> HOLD |
| #103 PR2 | Confirm admission basis | ADMITTED_BY_ISSUE_RECORD; RTC decision not recorded |
| #183 POC steps 1-4 | Design Review (new architecture, acronym collision) | UNRECORDED -> HOLD |
| #110 audit document; #122 cloud-subset receipt; #94 re-search | none (observation) | not applicable |
| Five working tags, PKA mapping, issue-class vocabulary, ControlStateDrift candidate | RTC (governance vocabulary) | PROPOSED; UNRECORDED |
| Cursor CF as integrating writer for NOW.md and the ledger | Forge CA acceptance | PROPOSED; UNRECORDED |

## 13. Whole-house audit baseline

At the base SHA the tree holds **5,660 tracked files**. **3,940 (69.6%)** are third-party or tool-generated (`.CLI_Project/` 3,419, `Schematics/.smart-env/` 437, `Schematics/.obsidian/` 84), leaving about **1,720** files of doctrine and implementation to review. The coverage CSV lists 32 file rows: 14 read semantically in whole or part, 7 scanned mechanically, 5 validated by structure, and 6 classified without being opened (protected, third-party or inventory). Every other tracked file is `unread`.

| Review state (file rows, cloud) | Count |
|---|---|
| inventory | 2 |
| protected | 3 |
| runtime_validated | 5 |
| scanned | 7 |
| semantic | 5 |
| semantic_partial | 9 |
| third_party_generated | 1 |

| Review state (directory rows) | Count |
|---|---|
| inventory | 60 |
| third_party_generated | 3 |

Coverage CSV: `docs/swarm-ops/receipts/GSMB_HOUSE_AUDIT_COVERAGE_CLOUD_2026-09-30.csv` (columns follow the constitution's eight provenance dimensions plus review state and relation to implementation or receipts).

Rule carried into Wave 2: a slice is promoted only when the Schematics sources it depends on are at `semantic` or better; observation receipts may proceed at `scanned` with declared uncertainty. Protected credentials and third-party or generated material are classified and never opened or counted as reviewed doctrine. Root `NOW.md` keeps the full audit recorded as incomplete.

## 14. C.L.E.A.R. per disposition packet

Sieve applied to each issue's disposition packet (Complete, Logical, Evidence, Audience, Relevant). Y yes, P partial, N no. It checks that the packet is fit for scrutiny; it does not validate the issue's claims (`CLEAR_PASS != POC_VALIDATED`). This is delivery review by the author; Academy review and independent review are separate and not claimed.

| Issue | C | L | E | A | R | Note |
|---|---|---|---|---|---|---|
| #94 | Y | Y | Y | Y | P | Single ask; accounted as UNKNOWN. Low current priority. |
| #102 | P | Y | P | Y | Y | 8 boxes accounted as two groups. Runtime evidence is dated. |
| #103 | P | Y | Y | Y | Y | 10 phase boxes accounted as a group; only PR1/PR2 boundaries assessed. |
| #107 | P | Y | P | Y | Y | 13 boxes and 7 PRs accounted as a group. Cross-repo lanes unreadable. |
| #110 | P | Y | Y | Y | Y | 8 boxes: 1 evidenced, 7 open; accounted as two groups. |
| #115 | P | Y | Y | Y | Y | 5 tasks: Task 1 sliced, Tasks 2-5 held. |
| #116 | Y | Y | Y | Y | Y | Discussion-only issue; disposition matches its own status. |
| #121 | Y | Y | P | Y | Y | State record; timeline spans four sources, no adjudication. |
| #122 | P | Y | Y | Y | P | 7 boxes: cloud subset sliced, rest held. Dated. |
| #158 | P | Y | P | Y | P | 10 boxes accounted as a group. Cross-repo results not re-run. |
| #163 | Y | Y | Y | Y | Y | Ask was artifact visibility to GSMB; delivered. Closure is a separate question. |
| #167 | Y | Y | Y | Y | Y | All 7 RTC questions enumerated as unanswered in the cloud record. |
| #183 | P | Y | Y | Y | Y | 35 boxes accounted as a group; POC steps 1-4 identified as the first slice. |
| #205 | P | Y | Y | Y | Y | Steps 4-5 partially evidenced (#202 verification not performed). |
| #207 | P | Y | P | Y | Y | 7 checklist items: 3 evidenced, rest HOLD. Settings unreadable. |
| #211 | Y | Y | Y | Y | Y | All four closure steps are human-held. |
| #231 | P | Y | Y | Y | Y | 5 field boxes accounted as a group. |

## 15. Teach-back

1. **Outside artifact or need.** Seventeen stale GitHub issues, Robyn's request to audit them against where KPGS is now, and the Forge CA brief. The need is a truthful state, not closure.
2. **KPGS purpose, protocol, boundary.** Legacy (proof before promotion, continuity); renter entryway (root `NOW.md` authority, receipts, no self-promotion); FOC vs POC constitution (claim families, PKA, append-only Smart Ledger); C.L.E.A.R. as a sieve; HOLD on missing evidence.
3. **What exists and the evidence.** Section 4 observations and section 7 claims; each has a command, API or file pointer.
4. **Bounded experiment.** This ledger is the experiment. Re-running the named command reproduces each observation; RTC or Forge can contradict any row; corrections append with `supersedes` and never rewrite.
5. **What the next renter needs.** This file, the JSON twin and its verification snippet, the coverage CSV, the groups document, the root `NOW.md` block, and the section 17 queue.

## 16. Append-only rules and verification

- Entries are never edited. A correction appends a new entry whose `supersedes` names the entry it replaces and the exact claim ids it replaces (scoped supersession).
- Wave 3 appends outcomes; it does not touch these entries.
- Hash rule: `sha256` of the entry without its `hash` field, serialized as `json.dumps(entry, sort_keys=True, separators=(",", ":"), ensure_ascii=False)` in UTF-8. `prev_hash` of entry 1 is 64 zeros.

```python
import json, hashlib
d = json.load(open("docs/swarm-ops/receipts/ISSUE_RECONCILIATION_LEDGER_2026-09-30.json", encoding="utf-8"))
prev = d["genesis_prev_hash"]
for e in d["entries"]:
    body = {k: v for k, v in e.items() if k != "hash"}
    assert body["prev_hash"] == prev, e["seq"]
    h = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
    assert h == e["hash"], e["seq"]
    prev = h
print("chain ok", len(d["entries"]), prev)
```

Expected at publication: `chain ok 27 5427b8db415c503ea8f4feb29613e2cfd09fccfa1a75dcef6d09c498831350e7`.

## 17. Human, Forge and RTC queue

| Actor | Action |
|---|---|
| Robyn | Regenerate the account's Discord backup codes now (F-2), then decide removal from HEAD and history remediation. |
| Forge CA / Robyn | Admin-scope readback of branch protection and every ruleset; decide the review-requirement question (F-1) and whether to log it. |
| Robyn | Provide the three Azure OIDC secret values and verify the federated identity (#211). |
| Robyn | Decide whether Bookit PR #33's epoch relaunch is still intended (#158); close #205 if satisfied with C-205-1 to C-205-3. |
| RTC / Forge CA | Convene Design Review for #183 and #107, Classroom admission for #115 Tasks 2-5, discussion for #116, and disposition for #167 questions 1-7 and #121 gates. |
| RTC / Forge CA | Decide SAP naming, the five working tags, PKA mapping, issue-class vocabulary, and the ControlStateDrift candidate. |
| Forge CA | Accept or amend the integrating-writer assignment for NOW.md and the ledger. |
| Robyn / Forge CA | Publish or hash-attest the local-only sources in section 10 via a PR from the local checkout; supply the local coverage.csv header. |
| Robyn | Name the second skill registry (#94); supply a Google Drive mirror receipt (Drive is UNKNOWN). |
| Robyn / Forge CA | Choose the independent-review mechanism for this repo (see F-1 hypothesis H1); until then renter PRs carry a separate-context review record and no GitHub approval. |

## 18. Receipt boundary

**Proved by this receipt:** each observation in section 4 at its stated time; the per-claim receipts in section 7; the hash chain of the JSON twin.

**Not proved:** any incident closure; the current branch-protection setting; Azure production health; Bookit or KasiLink runtime; the content of any protected file; local or Drive state; any RTC or Forge admission; that any proposed vocabulary is adopted.

**Changed by this receipt:** files added under `docs/swarm-ops/receipts/`, `docs/governance/`, `Schematics/24-RTC Learning/POCvsFOC Groups/`, and one prepended block in root `NOW.md`. No issue, setting, secret, dependency or deployment was touched.

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
