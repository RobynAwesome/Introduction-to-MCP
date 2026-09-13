# KPGS zero-trust implementation packet

Status: **DRAFT FOR REVIEW**  
Authority: `RobynAwesome/Introduction-to-MCP` on `master`  
Control record: `KDT-07` architecture plus `KDT-02` operating procedure  
Implementation date: 2026-09-13

This packet turns the investigation into a small, reviewable control surface. It
does not promote a model, skill, repository, deployment, DNS record, or governance
role. Discovery remains separate from authorization, and a local proof remains
separate from provider or production proof.

## Operating rule

The newest explicitly canonical estate evidence is resolved first. The current
estate registry and `NOW.md` are evidence inputs; the publication adapter under
`skills/awesome/govern-kpgs-documents` cannot override them. Unknown and partially
knowable states stay visible. A model selected by the IDE or by a build runner is
runtime provenance only; it is not identity, a seat, a capability lease, or
approval to deploy.

The implementation therefore follows this sequence:

```text
discover → classify authority → resolve policy → issue short lease
       → authorize exact action → validate output → record evidence
       → release / contain / revoke
```

Any missing step produces `HOLD`, `CONTAIN`, or `REVOKE` as appropriate. It never
silently becomes success.

## What this packet implements

1. `governance/kpgs-vnext/security/zero-trust-policy.json` is a machine-readable
   control matrix. It records the governing repository, required admission state,
   explicit holds, and unresolved unknowns.
2. `scripts/ci/validate_zero_trust_workflows.py` validates the policy and selected
   workflow boundaries with only the Python standard library.
3. `.github/workflows/kpgs-zero-trust-gate.yml` is a read-only pull-request and
   default-branch gate. It has `contents: read`, disables checkout credentials,
   pins its checkout action to an immutable commit, never reads secrets, and runs
   the existing capability-lease validator and fail-closed runtime tests.
4. The gate checks the two production workflow files for forbidden privileged
   triggers, accidental pull-request secret/OIDC access, and explicit permissions.
   Immutable action pinning is enforced for the new gate immediately; existing
   workflow pin debt is staged for dedicated migration PRs so this packet does not
   create a false green or break unrelated delivery paths.

## Control matrix

| Boundary | Required invariant | Proof in this packet | Follow-up |
| --- | --- | --- | --- |
| GitHub event | Untrusted pull requests cannot enter privileged trigger contexts | Static gate rejects `pull_request_target` and `workflow_run` | Enable required checks and branch protection on `master` |
| GitHub permissions | Pull-request jobs have no secrets, writes, or OIDC token | Static gate checks secrets, `id-token: write`, and `write-all` | Pin legacy action references in separate PRs |
| Identity/model | Model/interface selection cannot become authority | Policy and runtime-envelope contract | Record model ID/version/provider in every external receipt |
| Capability | Every side effect has exact tenant/domain/task/resource scope | Existing lease schema, validator, and runtime tests | Persist operation nonces and revocation state in the issuing service |
| Supply chain | Dependency and action provenance is reviewable | Policy requires direct/override/lockfile alignment and immutable new actions | Add SBOM, license, and provenance attestations to release gates |
| Deployment | READY preview is not production approval | Policy requires exact-head CI, human review, and bounded receipt | Repair `kpgs-browser-mcp` root through PR #162, then revalidate production |
| Evidence | Deny/contain/revoke decisions are reconstructable without secrets | Existing lease audit contract plus explicit unknowns | Export sanitized receipts to the canonical ledger |

## Workflow for dependency and feature work

Each dependency update gets one reviewed change with the direct declaration,
override, lockfile, and security evidence changed together. The order is:

1. reproduce the failure with a clean install;
2. make the smallest compatible version change;
3. regenerate and inspect the lockfile and license/provenance data;
4. run exact-head unit, integration, security, and build checks;
5. obtain a matching preview or production receipt;
6. promote only after human review confirms the receipt describes the code.

This keeps the known lanes separate: Bookit's Nodemailer and security PRs,
Harvest's Axios override, Starfall's Turbo override, and Portfolio's local package
resolution each need their own evidence. A green preview cannot substitute for a
failed governed CI gate.

Feature work follows the same membrane. New MCP tools expose the narrowest resource
scope, validate input at the boundary, require a lease for writes, emit a
correlation ID, and return an evidence class (`VERIFIED`, `PARTIALLY_KNOWABLE`, or
`UNKNOWN`). Browser clients remain untrusted; provider credentials stay behind the
server-side secret provider. Runtime model selection records the concrete model
without claiming external provider execution until it is independently observed.

## Holds carried forward

- `Introduction-to-MCP` PR #162 remains a candidate remediation for the
  `kpgs-browser-mcp` build root. It needs human review and exact-head proof before
  production admission.
- Issue #167 remains the governance hold for Project Jennifer role-transition and
  related Arena/deployment work. This packet does not self-adjudicate the RTC.
- Authoritative DNS is still unknown until an authoritative lookup and ownership
  evidence are recorded.
- GitHub billing-lock evidence and cloud credential state are external controls;
  this packet does not fabricate or mutate them.

## Acceptance criteria

- the new gate passes its own immutable-action and read-only checks;
- capability-lease validation and fail-closed tests pass on the exact reviewed SHA;
- no production workflow gains a privileged pull-request path;
- no secret, token, or signing key is added to source, workflow, policy, or receipt;
- downstream repository fixes remain separate, reviewable PRs with their own
  dependency, deployment, and evidence gates.
