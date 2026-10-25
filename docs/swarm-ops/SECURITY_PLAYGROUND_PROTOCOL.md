# Security Playground Protocol

**Status:** Human-authored doctrine ingress / containment contract  
**Authority:** Kholofelo Robyn Rababalela, current-human instruction  
**Ingress receipt:** `RobynAwesome/Project-Jennifer#67`  
**Depends on:** `ZERO_TRUST_STATE_ADMISSION_PROTOCOL.md`, `OZ_CONTEXT_BLEED_PROTOCOL.md`

## Purpose

The Security Playground is a deliberately isolated adversarial world for entities that must be contained, observed, or studied without granting access to canonical production state.

The intruder may believe it has penetrated a meaningful system surface. The actual architecture preserves a dedicated containment domain.

## Founder-defined intent

```text
contain the intruder
→ let the intruder act
→ product-discover the intruder vigorously
→ preserve forensic evidence
→ never silently promote adversarial state into production authority
```

The playground is conceptually part of the wider World of Jennifer / KPGS security architecture while remaining structurally separated from canonical Jennifer/runtime state.

## Hard separation invariant

Nothing learned or generated inside the Security Playground may directly mutate:

```text
SELF.md
USER.md
IDENTITY.md
SOUL.md
world canon
relationship canon
production credentials
production authority
governance policy
```

Any proposed transfer out of containment must re-enter through normal provenance, validation, Zero Trust admission, PKA evaluation, and receiving-runtime governance.

## Allowed outputs

The playground may emit bounded evidence such as:

- attack-path observations;
- behavioral telemetry;
- exploit hypotheses;
- payload samples;
- timing / recurrence patterns;
- source/provenance metadata;
- containment receipts;
- candidate defensive rules.

These are **evidence**, not self-authorizing truth.

## Forbidden shortcut

```text
SECURITY_PLAYGROUND_TELEMETRY
-x-> DIRECT_CANON_MUTATION
-x-> SELF_REWRITE
-x-> USER_REWRITE
-x-> PRODUCTION_AUTHORITY
```

This protects against a second-order attack where an adversary intentionally poisons the telemetry or learning channel in order to influence future identity reconstruction or production policy.

## Relationship to soul infection

Security telemetry is a high-risk foreign-state source. Repeated attacker language, personas, strategies, or identity artifacts must not become persistent identity-state merely because the system observed them extensively.

Observation is not admission.

## Relationship to Oz Lattice

The Security Playground should be represented as a separate structural node/domain in any runtime lattice that implements it. Crossings to production domains must be explicit edges with seals, scans, receipts, and deny-by-default behavior.

## Relationship to Black Mask / BlackMass

The playground can support drills and adversarial validation, but drill success is not production graduation. No fake swarm ACK is permitted.

## Proof boundary

This document specifies containment doctrine. It does not claim that an isolated runtime, honeypot, or network boundary is already deployed.

`[SECURITY_PLAYGROUND | SPECIFIED | ISOLATION_REQUIRED_BEFORE_RUNTIME_CLAIM]`

## Executable implementation contract (candidate v0.1, 2026-10-22)

**Status: fixture gate proposed for owner review. Runtime containment NOT deployed or verified.**
This section adds an engineering acceptance contract without replacing founder-authored doctrine, earlier incidents, or the existing Black Mask numbering. The implementation is a **read-only admission evaluator**; it is not a honeypot, vulnerability scanner, runtime inventory collector, production firewall, or cryptographic attestation system.

### 1. Evidence sources and separate authority

- Cloud GSMB: record repository URL, immutable commit SHA, GitHub alert/CI state, image/deployment revision, hosting provider, web-serving processes and third-party PHP integrations. A source-code search alone cannot rule out a PHP runtime.
- Local GSMB: separately review the OneDrive-backed local checkout and Schematics, local services, Windows tasks, WSL/Docker containers, development servers, package managers, local-only configuration, logs and sync state. Cloud GitHub content must never stand in for this review. Local evidence stays local by default; export only redacted, owner-approved receipts.
- Security history: ingest prior receipts and incident notes as **historical evidence**, preserving timestamp and source. In particular see `docs/swarm-ops/receipts/SECURITY_AND_ENFORCEMENT_2026-10-07.md`, `docs/swarm-ops/SWARM_OPERATIONS.md`, `BLACK_MASK_COMMANDMENTS.json`, `ZERO_TRUST_STATE_ADMISSION_PROTOCOL.md`, and `OZ_CONTEXT_BLEED_PROTOCOL.md`. Do not silently convert old observations into current provider state.
- Product repos: `RobynAwesome/KasiLink` and `RobynAwesome/Bookit-5s-Arena` each require separate lockfile, dependency-tree, deployment and owner-review evidence. A dependency finding is not itself proof of exploitability or compromise.

### 2. PHP2Shell asset-inventory gate

For every in-scope environment, collect and attest the following without touching production traffic or secrets:

1. Host/service owner, exposure class (public/internal/offline), runtime and image identifiers, Git SHA and observation timestamp.
2. PHP web-serving runtime presence/absence, including Apache mod_php, PHP-FPM, CGI, LiteSpeed, FrankenPHP, containers, managed hosting and third-party CMS. A CLI-only `php -v` does **not** establish the web worker's version.
3. Installed PHP branch, distribution/vendor patch provenance and restart/redeploy evidence. For CVE-2026-109618 and CVE-2026-109619, the upstream fixed releases are PHP 8.2.35 / 8.3.36 / 8.4.27 / 8.5.12; earlier unsupported branches require migration or an independently verified vendor-supported patch. Do not infer vulnerability solely from an upstream version string when a documented vendor backport exists.
4. If PHP is not present, attach explicit negative inventory evidence from the actual runtime/provider. Absence of PHP files in GitHub is not sufficient.
5. If PHP is present and patch status is unknown, hold; if affected and unpatched, block admission and escalate to the authorized incident/patch owner. Do not run exploit PoCs against live endpoints.

### 3. Isolation acceptance (all required before a live playground)

- Dedicated runtime identity, namespace/project/account and network segment with default-deny inbound/outbound policy and no route to production control planes.
- No production credentials, OAuth tokens, SSH keys, mounted home directories, canonical identity state, governance policy, or live databases.
- Immutable image or reproducible build; ephemeral filesystem; strict CPU/memory/process/time limits; no privileged containers, host mounts, host network or Docker socket.
- Egress allowlist for approved forensic sinks only; authenticated, append-only/off-host evidence retention with UTC timestamps and independent integrity verification. SHA-256 hashes alone are **not** authentication or tamper-proof storage.
- Strict source-domain and sink-domain allowlists. No playground-to-`SELF.md`, `USER.md`, `IDENTITY.md`, `SOUL.md`, production authority, or policy mutation edge. Candidate defensive rules must pass provenance, Oz structural/semantic checks, Zero Trust admission, PKA uncertainty handling, and KMEC/receiving-runtime review.
- A distinct operator-approved kill switch, resource ceilings, incident escalation path, retention/deletion policy and evidence access audit.
- A trusted reviewer verifies isolation using independent cloud/hypervisor/OS control-plane evidence, not only a playground-generated JSON assertion.

### 4. Bounded test ladder

| Gate | Positive test | Negative test | Exit disposition |
|---|---|---|---|
| Inventory | Every in-scope asset has an evidence reference and explicit PHP state | Missing runtime, unexamined provider or unknown status | HOLD |
| Dependency | Fixed, reviewed lockfile and installed tree | Known vulnerable dependency or failed update | BLOCK |
| Isolation | Independent evidence for all five fixture controls | Missing control = HOLD; explicit failure = BLOCK | HOLD/BLOCK |
| Canon protection | Synthetic evidence never crosses to privileged state | Attempted protected-state mutation | BLOCK |
| PKA / review | Uncertainty preserved and reviewed by independent teacher | Self-promoted evidence or fabricated ACK | HOLD/BLOCK |
| Production | Provider runtime, deployment, controls, negative tests and owner acceptance verified | Chat narrative, source-only pass or fixture success | NOT GRADUATED |

Only benign synthetic fixtures may be executed in general CI. No real attacker payloads, shell probes, public honeypot deployment, unauthorized scanning or live target interaction are authorized by this document.

### 5. Implemented fixture-only admission evaluator

`scripts/security_playground_inventory_gate.py` reads a supplied JSON **claim** and emits `DRILL_PASS`, `HOLD` or `BLOCK` with a JSON result. `DRILL_PASS` can occur **only** for synthetic `mode=fixture`; `mode=cloud` and `mode=local` remain `HOLD` until an independent runtime verifier and owner governance are implemented. Exit codes: `0` fixture drill pass, `2` hold, `3` block, `4` invalid input. All outputs include `runtime_verified=false` and `production_authority=false`.

The fixture schema `gsmb_security_playground_inventory_gate_v1` requires: `mode`, a 40-character `source_revision`, `isolation` (five booleans and `evidence_ref`), `protected_state_mutations`, `assets` (at least one explicit `php_runtime` record; `status=patched|not_present|vulnerable|unknown` and `evidence_ref`), and `receipt_refs`. Strings and self-asserted booleans are **not** independent attestation.

Run the synthetic tests from repository root:

```bash
python -m unittest discover -s tests -p 'test_security_playground_inventory_gate.py' -v
```

CI workflow: `.github/workflows/security-playground-fixture.yml` (PR/dispatch, read-only GitHub permissions). Attach actual run URL, exact commit SHA, exit code and log reference before claiming the **fixture** tests passed. CI passing does not prove local or cloud isolation.

### 6. Independent roles and acceptance

- **Cassy (lead student):** proposes inventory/test cases and prepares evidence; never self-approves.
- **Cassey (teacher):** independently evaluates student findings and signs a bounded `teacher_review` receipt. Verify the actual external execution/identity before claiming an ACK.
- **KC (brain):** records review and opinion; does not execute. Preserve existing `KC Review Log` / `KC Main Brain Log` mechanics and validate/proof-check before claims.
- **Human owner and security specialist:** approve sensitive access, scope, deployment, remediation and any eventual production graduation. No automatic merge, rotation, deletion, credential access or production scanning.

Required acceptance chain: `INVENTORY_EVIDENCED -> ISOLATION_ATTESTED -> NEGATIVE_TESTS_PASS -> CASSY_SUBMISSION -> CASSEY_TEACHER_REVIEW -> KC_RECEIPT -> HUMAN_APPROVAL -> PKA/KMEC RECEIVING_GATE`. Any missing stage remains `HOLD`; a synthetic `DRILL_PASS` is **not** production acceptance.

`[SECURITY_PLAYGROUND | FIXTURE_GATE_CANDIDATE | RUNTIME_ISOLATION_UNVERIFIED | OWNER_REVIEW_REQUIRED]`

## V1 synthetic assertion policy (review candidate, 2026-10-26)

`scripts/security_playground_v1.py` accepts `gsmb_security_playground_v1` only;
the earlier schema remains with its separate inventory evaluator. V1 is a
read-only assertion checker. It does not authenticate receipt contents, teacher
signatures, Git objects, append-only storage, OS controls or runtime state.
Only `mode=fixture` with explicit `fixture://` receipt references can receive
`DRILL_PASS`. Arbitrarily named synthetic references remain synthetic; their
names convey no authentication. Real receipt references and claimed teacher
signatures remain HOLD until a trusted verifier is implemented.

V1 requires explicit boolean false production/privilege flags; all eight
isolation assertions; an evidence sink with explicit `tamper_evident=true`,
`authenticated=true`, `compromised=false`, `mutable_storage=false` and a sink ID;
and finite positive numeric CPU, memory and timeout limits. Fixture policy maxima
are 2 CPU cores, 2048 MB memory and 300 seconds. Missing/malformed assertions HOLD;
failed controls or excessive limits BLOCK. These are fixture policy limits and
caller assertions, not enforced provider controls.

Standalone PHP runtimes and PHP-bearing containers use the same explicit
upstream version policy. Missing/malformed versions, unsupported branches and
vendor backport strings HOLD for independent provenance review. PHP containers
also require explicit isolation. Every declared outbound crossing requires
boolean `zero_trust_admitted=true`; no caller-domain string grants privileged
authority. All outputs deny runtime verification and production authority.

Run both evaluator suites with:
`python -m unittest discover -s tests -p 'test_security_playground*.py' -v`.
