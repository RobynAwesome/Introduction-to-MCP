# GSMB Security Discovery & Control Matrix

**Document ID:** SEC-MATRIX-2026-1022  
**Auditor / Lead:** Lead Dev AG (AntiGravity)  
**Authority:** Founder / RTC  
**Scope:** Forensic reconciliation of historical security doctrine, real incidents, forensic receipts, present-day implementation, and PR #326.  
**Classification Standard:** `SPECIFIED / IMPLEMENTED / TESTED / RUNTIME_VERIFIED / UNKNOWN`

---

## 1. Governance & Operational Hierarchy
1. **Founder / RTC:** Owns all architectural decisions, merges, rotations, and production authorizations.
2. **Lead Dev AG:** Leads engineering discovery, implementation, negative test suites, branches, and technical handoff.
3. **Z Code:** Independent security validation and adversarial challenge.
4. **Cassy:** Lead student evidence and learning lane.
5. **Cassey:** Independent teacher-review lane.
6. **KC:** Records reviews, receipts, and opinions in Review Log / Main Brain Log; does not execute.

---

## 2. Discovery Matrix

| Control | Historical Source | Implementation | Test | Actual Runtime Evidence | Classification | Gap |
|---|---|---|---|---|---|---|
| **Security Playground Isolation Contract** | `docs/swarm-ops/SECURITY_PLAYGROUND_PROTOCOL.md`, PR #326 candidate | `scripts/security_playground_inventory_gate.py` (v0.1), `scripts/security_playground_v1.py` | `tests/test_security_playground_inventory_gate.py`, `tests/test_security_playground_v1.py` | PR #326 CI fixture-admission passed (job 119844037350); 16 unit tests exit 0 | `TESTED` (Fixture) / `SPECIFIED` (Runtime) | Physical sandbox/hypervisor isolation not deployed; relies on read-only fixture admission evaluator. |
| **Dedicated Nonproduction Identity** | `docs/swarm-ops/SECURITY_PLAYGROUND_PROTOCOL.md#L30-L40`, `SECURITY_AND_ENFORCEMENT_2026-10-07.md` | `execution_identity` validation in `security_playground_v1.py` | `test_privileged_execution_identity` | Exit code 3 when privileged identity (`root`/`admin`) claimed | `IMPLEMENTED` | OS-level non-root daemon user not enforced in production CI workflows. |
| **Default-Deny Production Network Boundary** | `docs/swarm-ops/SECURITY_PLAYGROUND_PROTOCOL.md` Section 3 | `deny_production_network` gate assertion in `security_playground_v1.py` | `test_scenario_07_failed_isolation_control` | Exit code 3 when network boundary assertion fails | `IMPLEMENTED` (Gate) / `SPECIFIED` (Network) | Live host/container iptables or eBPF firewall dropping production IP egress is not deployed. |
| **Protected State Immutability (`SELF.md`, `USER.md`, `IDENTITY.md`, `SOUL.md`)** | `docs/swarm-ops/SECURITY_PLAYGROUND_PROTOCOL.md` ("Hard separation invariant"), `ZERO_TRUST_STATE_ADMISSION_PROTOCOL.md` | `protected_state_mutations` counter & target list in `security_playground_v1.py` | `test_scenario_08_attempted_protected_state_mutation` | Exit code 3 when mutation count > 0 or target matches protected canon | `IMPLEMENTED` (Gate) / `SPECIFIED` (Filesystem) | Local filesystem files are standard read-write NTFS files, not mounted as read-only WORM blocks. |
| **Oz Structural Lattice Boundary** | `docs/swarm-ops/OZ_CONTEXT_BLEED_PROTOCOL.md` (OZ-LATTICE-2026-001) | `kopano-core/kopano/oz_lattice_protocol.py` (LATTICE_NODES, ALLOWED_EDGES, SHA-256 seal) | `tests/test_oz_lattice_protocol.py`, `test_oz_boundary_unadmitted_bleed` | SQLite table `lattice_bleed_audits` in `db/datalake.db`; unit tests pass (SEALED vs BLEED_DETECTED) | `RUNTIME_VERIFIED` (Core nodes) / `IMPLEMENTED` (Playground) | `playground` node was absent in legacy `LATTICE_NODES`; now added with default-empty egress. |
| **Black Mask Testing Doctrine** | `docs/swarm-ops/BLACK_MASK_COMMANDMENTS.json` (15 Commandments + 5 Pillars) | `scripts/kc_blackmask_bracket_stress.py`, `kopano-core/kopano/blackmask_bracket_stress.py` | CI workflow `Agent build PoC (Bracket / BlackMask / Guardian / Identi / LPM / KPEFS)` | Check run 119844167281 passed on PR #326 | `RUNTIME_VERIFIED` (in CI) | Commandment 12: drill promotion is steward attestation, not production graduation. |
| **Zero-Trust State Admission Membrane** | `docs/swarm-ops/ZERO_TRUST_STATE_ADMISSION_PROTOCOL.md`, `governance/kpgs-vnext/security/zero-trust-policy.json` | `.github/workflows/kpgs-zero-trust-gate.yml`, `scripts/ci/validate_zero_trust_workflows.py`, `capability_lease.py` | `tests/test_zero_trust_workflow_policy.py`, `tests/test_capability_lease_runtime.py` | Check run 119844037011 passed on PR #326 | `RUNTIME_VERIFIED` (CI) | Evaluates GitHub workflow boundaries and capability leases; real-time API request admission in review. |
| **Partial Knowable Algebra (PKA) Uncertainty Gate** | `ZERO_TRUST_STATE_ADMISSION_PROTOCOL.md`, `AI_FLOW_PROTOCOL.md` | `.github/workflows/pka-skills.yml`, `skills/pka/**/wyc-01-receipt.schema.json` | `pka-skills.yml` package validation | CI runs validate YAML frontmatter and `/s/ Kholofelo Robyn Rababalela` signature | `IMPLEMENTED` | PKA evaluation is currently schema/signature checks rather than algebraic scoring engine. |
| **KMEC Alert & Coordination Engine** | `docs/swarm-ops/receipts/KMEC_OBSERVATION_ENGINE_107_ADMISSION_PACKET_2026-09-30.md` | `kopano-core/kopano/runtime.py`, event logs in `docs/swarm-ops/logs/` | Integration tests in `tests/test_security_tool.py` | Local datalake rows written during runner cycles | `IMPLEMENTED` | External SIEM / Pager alert webhook routing is not configured. |
| **Password Hashing & Admin Bootstrap (CodeQL #16)** | `SECURITY_AND_ENFORCEMENT_2026-10-07.md#L45-L55` | `kopano-core/kopano/database.py` (salted SHA-256), `runtime.py` | CodeQL high alert #16 open on master | Provider alert open; default public admin password in source; binds `0.0.0.0:8000` | `IMPLEMENTED` (Vulnerable legacy) | Migration to Argon2id/bcrypt and owner-reviewed first-run onboarding without public fallback required. |
| **OAuth Token Endpoint HTTPS Enforcement (CodeQL #43)** | `SECURITY_AND_ENFORCEMENT_2026-10-07.md#L57-L63` | PR #286 (`codex/security-oauth-token-tls-20261007`) | Rust CI checks | PR #286 open at `860da3fb`; checks pass; CodeQL alert #43 open on master | `TESTED` (PR) / `UNKNOWN` (Master) | PR #286 unmerged; requires owner review and rebase onto master. |
| **XSS Hardening & DOM Escaping (CodeQL #8-#14, #46)** | `SECURITY_AND_ENFORCEMENT_2026-10-07.md#L65-L75` | PR #285 (`08581a1b`), PR #287 (`f6046415`) | Pytest 2/2, Node regressions 7/7 pass | Provider CodeQL checks pass on PR merge refs; 32 alerts open on master | `TESTED` (PR) / `UNKNOWN` (Master) | PRs unmerged; Vercel preview status context rate-limit failure on #285; awaits owner review. |
| **Trusted Four Ws Provenance Gate** | `SECURITY_AND_ENFORCEMENT_2026-10-07.md#L77-L86`, PR #288 | `.github/workflows/kpgs-fourws-review-gate.yml`, PR #288 proposal | GitHub Actions PR runs | In PR #326, run was `cancelled`; check is not required in branch protection | `IMPLEMENTED` (Workflow) / `SPECIFIED` (Trusted successor) | Check currently runs validator from PR merge revision rather than trusted base; 0 required approvals on master. |
| **PHP2Shell Exposure Gate (CVE-2026-109618, CVE-2026-109619)** | Current incident briefing & threat intelligence | `scripts/security_playground_v1.py` (PHP asset evaluator) | `test_scenario_01` through `test_scenario_04c` | Local: absent; Cloud: absent; Production (IONOS): unknown | `IMPLEMENTED` (Gate) / `RUNTIME_VERIFIED` (Local/Cloud) / `HOLD` (Production) | IONOS shared hosting upstream PHP runtime configuration cannot be verified without control panel access. |
| **Production Deployment Boundaries** | `.github/workflows/deploy-web.yml`, `.github/workflows/deploy.yml` | `scripts/ci/production_deploy_gate.py`, IONOS FTP deploy, Azure `azd up` | `kpgs-gate` job in `deploy-web.yml` | Live deployments to Azure South Africa North, Vercel, and IONOS FTP | `RUNTIME_VERIFIED` | Production web deploy FTP credential scope must be audited against PHP execution permissions. |

---

## 3. Key Architectural Gaps & Immediate Remediations

1. **Security Playground Graduation Boundary:**  
   Synthetic fixture passing in CI (`fixture-admission`) must never be conflated with operational isolation. PR #326 correctly enforces `runtime_verified=false` and `production_authority=false`.
2. **Local vs Cloud Drift:**  
   Local GSMB `master` is 300 commits behind Cloud `origin/master`. Local working tree on branch `codex/kc-sovereign-gui-full-dev` has unstaged changes in `.CLI_Project/Lib/site-packages`. All security work must be committed to clean, revision-bound branches.
3. **IONOS FTP Exposure Risk:**  
   `.github/workflows/deploy-web.yml` pushes static files to IONOS shared hosting. If the IONOS package has PHP enabled on the root directory, an uploaded `.php` file or unpatched server worker could expose CVE-2026-109618 / CVE-2026-109619. This is held under `PRODUCTION_PHP_EXPOSURE: HOLD`.

`[LEAD_DEV_AG | DISCOVERY_MATRIX | COMPLETED | NO_PRODUCTION_WITHOUT_PROOF]`
