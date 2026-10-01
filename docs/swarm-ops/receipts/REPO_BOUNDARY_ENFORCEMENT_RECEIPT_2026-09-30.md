# REPOSITORY BOUNDARY ENFORCEMENT RECEIPT - 2026-09-30 (WAVE 1a)

**Status:** OBSERVATION RECEIPT. No repository setting, secret, dependency, workflow or issue was changed.
**Scope:** issues #205 (dependency admission), #207 (branch and PR proof at the repository boundary), #211 (Azure production deploy HOLD).
**Ledger:** `ILR-2026-09-30` (`docs/swarm-ops/receipts/ISSUE_RECONCILIATION_LEDGER_2026-09-30.{md,json}`, pull request #240 at the time of writing). Claim and observation ids below (C-xxx-n, O-nn, F-n) refer to it.
**Base:** `master@8c6d22f22dbc600a38b52daf3b2887940b8841fb` · **Live reads:** 2026-09-30T22:15Z to 23:15Z.
**Actor:** Cursor cloud agent, stateless renter, operational rank Chief Facilitator. Authority: Robyn's approval of the Wave 0-3 plan (2026-09-30 22:14 UTC). This receipt needs no RTC admission (observation only).
**GSMB tier:** Cloud (this file once merged). Local and Google Drive: UNKNOWN.
**Doctrine:** `I_AM_STATELESS_RENTER_NOT_LANDLORD` · `WRITTEN_INSTRUCTION != RUNTIME_ENFORCEMENT` · `FAILURE_SURFACED_BY_CALL != FAILURE_CAUSED_BY_CHANGE`

---

## 1. Claims this receipt supports, and what each does not

| Claim | Tag (proposed) | Supported by | Not supported |
|---|---|---|---|
| C-205-1 ESLint 10 pair landed in the studio lock | POC_VALIDATED | section 2.2 | anything outside `kopano-core/studio` |
| C-205-2 Dispositions of #198-#204 | POC_VALIDATED | section 2.1 | Dependabot's reason for three closures |
| C-205-3 #202 upload/download and runner-fleet check | UNKNOWN | section 2.3 | no such verification was performed |
| C-207-1 Provenance gate detects as designed | POC_VALIDATED | section 3.1 | prevention |
| C-207-2 Direct pushes are prevented at the settings boundary | HOLD_HUMAN | section 3.2 | which rule rejected the recorded push |
| C-207-3 Master requires one approving review | FOC_RISK | sections 3.2 and 3.3 | whether the setting is on, off, or bypassable |
| C-211-1 Azure deploy still fails at the credential contract | POC_VALIDATED | section 4.1 | any fix; the HOLD stands |
| C-211-2 Closure requires owner-held secrets | HOLD_HUMAN | section 4.3 | n/a |

## 2. Issue #205 - dependency admission

### 2.1 Disposition of the seven pull requests in scope

| PR | Change | Final state | When (UTC) | How |
|---|---|---|---|---|
| #198 | openai 3.8.0 to 3.16.0 | closed, not merged | 2026-09-28T18:16:24Z | closed by `dependabot[bot]` |
| #199 | @vitejs/plugin-react 6.0.1 to 6.1.1 (`kopano-core/studio`) | merged | 2026-09-29T06:19:15Z | with integration PR #213 |
| #200 | @eslint/js 9.39.4 to 10.0.1 (`kopano-core/studio`) | merged | 2026-09-29T06:19:15Z | with PR #213 |
| #201 | @types/node 24.12.0 to 26.6.1 (`kopano-core/studio`) | closed, not merged | 2026-09-28T18:16:26Z | closed by `dependabot[bot]` |
| #202 | actions/upload-artifact 4 to 7 | merged | 2026-09-29T06:19:15Z | with PR #213 |
| #203 | azure-monitor-opentelemetry 1.8.9 to 1.8.10 | merged | 2026-09-29T06:19:15Z | with PR #213 |
| #204 | eslint 9.39.4 to 10.10.0 (`kopano-core/studio`) | closed, not merged | 2026-09-28T18:16:31Z | closed by `dependabot[bot]`; `NOW.md` records it as superseded |

Sources: `gh pr view <n>`; `gh api repos/.../issues/<n>/events` (class E2). No human closure decision for #198, #201 or #204 appears in the issue or the PRs; the reason Dependabot closed them is not recorded.

### 2.2 The lock that landed

`kopano-core/studio/package-lock.json` at `8c6d22f2` (blob `ad46697a9e206fc4294520eb1646a7212aa681f1`, identical at `65975a12`): `node_modules/eslint` is 10.11.0 and `node_modules/@eslint/js` is 10.0.1. `package-lock.json` at the repository root and `apps/kc-dashboard/package-lock.json` carry no eslint entries. 10.11.0 is newer than the 10.10.0 in #204, which fits the lock having been regenerated instead of taking #204 as opened (inference, E3). `NOW.md` (2026-09-29 block) attributes a local studio proof and the hosted `gui-check`; this receipt did not re-run them.

### 2.3 Mapping to the issue's own five steps

| Step in #205 | Status | Evidence |
|---|---|---|
| 1 Reconcile root `NOW.md` to master | met | root `NOW.md` leads with current blocks; the 2026-09-05 state no longer leads |
| 2 Merge #199 and #203, check #198 first | partly met | #199 and #203 merged; #198 was closed by Dependabot, so its `connector_id` question was never exercised |
| 3 Stage #200 and #204 as one ESLint 10 migration | met in effect | #200 merged with the regenerated lock; #204 closed as superseded |
| 4 Verify Node and `tsc -b` before #201; verify artifact upload/download before #202 | not met for #202 | #201 never merged; #202 merged and `NOW.md` says a manual artifact download was not performed, though required checks that run `upload-artifact@v7` passed |
| 5 Record exact heads, check runs and post-merge receipts | met by attribution | `NOW.md` 2026-09-29 block lists the merged set and the Kopano CI and CodeQL runs on `1a529b55` |

### 2.4 Owner close checklist

1. Read C-205-1 to C-205-3 and section 2.3.
2. Decide that leaving the openai and @types/node bumps unapplied (both closed by Dependabot) is acceptable.
3. Decide that the unperformed #202 download and runner-fleet check is acceptable, or ask for it.
4. Close #205. Open Dependabot PRs #238 and #239 are outside this issue.

## 3. Issue #207 - proof at the repository boundary

### 3.1 Detection gate (validated)

`.github/workflows/kpgs-branch-proof-gate.yml` (job name `Require PR provenance`). On a pull request it prints a pass line. On a push to `master` it asks GitHub for the pull requests associated with the pushed SHA and fails if none is a merged PR targeting `master`. Its own text says enforcement still needs repository settings.

Observed: push runs for `65975a12` and `8c6d22f2` succeeded; pull-request runs on the PR heads succeeded (ledger O-08). Negative path, re-observed by the independent reviewer: `gh api repos/RobynAwesome/Introduction-to-MCP/commits/a9f0d075/pulls` returns 0 pull requests for that 2026-09-05 direct commit. The check is one of the 14 required contexts (section 3.2).

### 3.2 What the settings reveal, and what they hide

| Item | Observable with this token? | Value | Source |
|---|---|---|---|
| Branch is protected | yes | true | `GET /branches/master` summary |
| Required status checks | yes | 14 contexts, `enforcement_level: everyone` | branch summary (ledger O-06) |
| Required pull request (or approvals) | no | UNKNOWN | summary has no such field; `GET .../protection` returns 403 |
| Approving-review count, stale dismissal, last-push approval, code owners | no | UNKNOWN | same |
| `bypass_pull_request_allowances` | no | UNKNOWN | same |
| `enforce_admins` | no | UNKNOWN (`NOW.md` attributes it on) | same |
| Up-to-date branches (`strict`), conversation resolution, force-push and deletion flags, linear history, push restrictions | no | UNKNOWN (`NOW.md` attributes several) | same |
| Ruleset `24144685` | yes | active; target branch `refs/heads/master`; `bypass_actors` null; `current_user_can_bypass` never; one rule, `code_scanning` for CodeQL at `high_or_higher`, `alerts_threshold` none | `GET /rulesets/24144685` |
| Ruleset `19244487` | yes | disabled; Copilot review only | `GET /rulesets` |
| Rules that apply to `master` via the rules API | yes | `code_scanning` only | `GET /rules/branches/master` |

The recorded rejection of a direct push (`NOW.md@8c6d22f2:L74`) does not name the rule that rejected it. Either the `code_scanning` ruleset or the required status checks would reject a direct push of a commit with no scan result or passing checks.

### 3.3 Merge and review timeline (E2 unless marked)

| When (UTC) | Event | Reviews on the PR |
|---|---|---|
| 2026-09-24 | #207 opened; issue text says `master` is unprotected | n/a |
| before 2026-09-29 | Protection enabled with one approving review (`NOW.md` security-controls block; before-state was HTTP 404), attributed | n/a |
| 2026-09-29 04:55:43 | #232 merged under the owner's identity (`RobynAwesome`) | none |
| 2026-09-29 05:43:16 | #233 merged under the owner's identity | none |
| 2026-09-29 06:19:12 | #213 merged by `app/cursor` | one COMMENTED |
| 2026-09-29 06:30:25 | #234 merged by `app/cursor` | none |
| 2026-09-30 about 06:33 | Forge block (`08:33:10+02:00`): `required_pull_request_reviews` was null at recovery; one approving review, stale-review dismissal and latest-push approval restored; removal attribution UNKNOWN (attributed; local readbacks unavailable) | n/a |
| 2026-09-30 09:32:22 | #235 merged under the owner's identity; it carries the Forge block | none |
| 2026-09-30 21:05:03 | #236 merged by `app/cursor` | none |
| 2026-09-30 22:32:09 | #237 merged under the owner's identity | none |
| 2026-09-30 22:42 and 23:02 | #238 `CLEAN` with no review decision; #239 `BLOCKED` while checks were pending, then `CLEAN` | no review decision |

No merge since 2026-09-29 shows an approving review, including the three merges after the recorded restoration. A merge recorded as `RobynAwesome` is made under the owner's GitHub identity; the record does not show whether Robyn personally or a tool acting with her credentials performed it.

### 3.4 What the two rules mean in GitHub terms (E3, from GitHub's API semantics; not verified against this repository)

In GitHub's classic branch-protection API one object, `required_pull_request_reviews`, represents both "require a pull request before merging" and the approval count. A null value turns the pull-request requirement off entirely, not only the approvals. Two consequences:

- **#207's own checklist** asks that changes to `master` require pull requests and that the team decide whether required status checks gate merges. It does not ask for an approval count. The approval count came from the later hardening recorded by Forge.
- With required status checks but no pull-request requirement, a direct push of a commit that already passed the checks (for example a pull-request head) would be accepted, and only the detection gate would notice afterwards. `NOW.md@8c6d22f2:L74` describes exactly that shape: the direct push was refused "until CodeQL and the 14 required checks existed".

### 3.5 Hypotheses consistent with the observations (none confirmed)

| Id | Hypothesis (E3) | What would confirm it |
|---|---|---|
| H1 | One required approval cannot be satisfied when agent pull requests are authored as the sole owner (`RobynAwesome`, ledger O-19), because GitHub does not let an author approve their own PR; the rule keeps being removed or bypassed | Readback shows a count of 1 and no second eligible approver |
| H2 | A bypass-pull-request allowance names the owner and the Cursor app, so the rule is on but bypassed for exactly these two actors | Readback shows `bypass_pull_request_allowances` with both |
| H3 | `required_pull_request_reviews` is null (pull requests are not required at all) | Readback shows null |

Only an admin-scope readback separates them.

### 3.6 Admin readback protocol (read-only; for Forge CA or Robyn)

Run with a token that has repository administration read access, and save the output unedited in a receipt file. None of these calls changes anything.

```bash
R=RobynAwesome/Introduction-to-MCP
gh api repos/$R/branches/master/protection
gh api repos/$R/rulesets
gh api repos/$R/rulesets/24144685
gh api repos/$R/rules/branches/master
gh api repos/$R/branches/master
```

Record these fields and the UTC time of the read:
`required_pull_request_reviews` (present or null; `required_approving_review_count`, `dismiss_stale_reviews`, `require_last_push_approval`, `require_code_owner_reviews`, `bypass_pull_request_allowances`), `enforce_admins.enabled`, `required_status_checks.strict` and contexts, `required_conversation_resolution`, `allow_force_pushes`, `allow_deletions`, `required_linear_history`, `restrictions`, and every ruleset's `enforcement` and `bypass_actors`.

For attribution of who changed a rule and when, use the change history GitHub exposes for this repository owner (an organization audit log if the owner is an organization; otherwise the account security log). Whether that history is available here is UNKNOWN; if it is not, attribution stays UNKNOWN.

The destructive alternative, pushing directly to `master` to see what is rejected, is not recommended and was not attempted: a readback is the equivalent proof that #207's checklist item 7 allows.

### 3.7 Decision options (proposed for Forge CA and Robyn; Robyn decides)

| Option | Setting | Meets #207's text | Consequence |
|---|---|---|---|
| A | Pull request required, one approval, plus a second approver identity | yes, and more | Strongest; needs an account other than `RobynAwesome`; fits H1 |
| B | Pull request required, one approval, agent PRs authored by a machine identity the owner approves | yes, and more | Needs a machine identity that authors the PRs |
| C | Pull request required, zero approvals, the 14 required checks, the detection gate, and a recorded independent review in each PR description | yes (the minimum) | Matches current practice; weaker; review is convention, not enforcement |
| D | No pull-request requirement (what the observations may describe) | no | Direct writes that pass the checks stay possible |

Whatever is chosen, the `NOW.md` instruction to "preserve the review requirement" must be made to match, or every later renter will follow a rule the settings do not enforce.

### 3.8 Status of #207's seven checklist items

| Item | Status |
|---|---|
| Decide the enforcement mechanism (protection and/or ruleset) | HOLD: needs the decision in 3.7 |
| Require changes to `master` through pull requests | UNKNOWN: not observable |
| Break-glass route, if wanted, receipted | HOLD: not decided |
| Required status checks gate merges; identify the workflows | met: 14 contexts observed (section 3.2) |
| Reconcile root `NOW.md` so its current state is not older than the history it governs | met: `NOW.md` leads with current blocks |
| Do not treat the issue as proof of protection | observed |
| Capture settings evidence and a rejected direct-write test or equivalent | partly: status checks and ruleset evidence captured; the review and pull-request settings need the readback in 3.6 |

## 4. Issue #211 - Azure production deploy HOLD

### 4.1 Evidence

Workflow `Kopano Context: Production Hardening Deployment` (`.github/workflows/deploy.yml`), job `Deploy authorized production change`:

- Run 36777088537 on `65975a12` (2026-09-30T21:05Z) and run 36786135007 on `8c6d22f2` (2026-09-30T22:32Z): the authorization job passed and the deploy job failed at step `KPGS Azure credential preflight`.
- In run 36777088537 the log shows `AZURE_CLIENT_ID`, `AZURE_TENANT_ID` and `AZURE_SUBSCRIPTION_ID` all empty and the error `Missing required GitHub Actions secrets: AZURE_CLIENT_ID,AZURE_TENANT_ID,AZURE_SUBSCRIPTION_ID`.
- Runs `2fae1480` and `d6126890` are green only because the deploy job was skipped.

The failure happens before any code is deployed, so it is not caused by the content of #236 or #237.

### 4.2 What the workflow requires

- Triggers: a push to `master`, or a manual `workflow_dispatch`, which passes `--explicit-release` to the gate and is authorized regardless of paths.
- `scripts/ci/production_deploy_gate.py` authorizes a push when a changed path is a root runtime file (`Dockerfile`, `kpgs_config.json`, `main.py`, `package-lock.json`, `package.json`, `pyproject.toml`, `uv.lock`) or sits under `infra/`, `kopano-core/` or `src/` with a listed suffix. Documentation and receipt files do not qualify. So Dependabot bumps of `uv.lock` or `package-lock.json` trigger a deploy attempt and currently fail it; this campaign's receipt pull requests do not.
- The deploy job has `permissions: id-token: write` and declares **no `environment:`**. The three values are read as `secrets.AZURE_*`, so they must exist as repository-level (or organization-level) Actions secrets, not environment secrets.

### 4.3 Closure checklist (Robyn; issue #211 steps 1-4)

1. Add repository Actions secrets `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`. Do not paste their values into issues, pull requests, logs, `NOW.md` or chat.
2. Verify the federated identity. With no `environment:`, GitHub's OIDC token for a run on `master` carries the branch-form subject `repo:RobynAwesome/Introduction-to-MCP:ref:refs/heads/master`. The Microsoft Entra federated credential should use issuer `https://token.actions.githubusercontent.com`, that subject, and audience `api://AzureADTokenExchange` (per GitHub and Azure documentation; E3, unverified in this tenant).
3. Re-run an authorized deploy without a code change: run the workflow manually on `master` (`workflow_dispatch`).
4. Close #211 only with a run receipt showing `KPGS Azure credential preflight`, `Log in to Azure` and `Provision & Deploy (azd)` (`azd up --no-prompt`) all successful. To read it:

```bash
gh run list --repo RobynAwesome/Introduction-to-MCP --workflow deploy.yml --limit 3
gh run view <run-id> --repo RobynAwesome/Introduction-to-MCP --json jobs --jq '.jobs[] | {name, conclusion, steps: [.steps[] | {name, conclusion}]}'
```

A green workflow with the deploy job skipped is not proof (`VERCEL_STATUS != AZURE_DEPLOY_PROOF`). A successful login does not prove `azd up` succeeded; the issue requires both.

## 5. Receipt boundary

**Proved here:** the disposition and lock facts of section 2; the detection gate's behavior and the ruleset's details in section 3; the merge and review timeline in section 3.3; the failing step and emptiness of the three variables in section 4; the workflow's triggers and path contract.

**Not proved:** the current setting of the pull-request requirement, approval count, bypass allowances or admin enforcement; Azure production health; the federated credential's actual configuration; any RTC or Forge admission.

**Changed by this receipt:** one file added. No setting, secret, workflow, dependency or issue was changed, and no direct push or bypass was attempted.

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
