# GSMB entry-read attestation: implementation receipt and host contract

**Status:** candidate stacked on PR #403; no runtime or Local/Drive enforcement claim.
**Authority:** Kholofelo Robyn Rababalela; existing REV-01, SPP, CCP, PKA and Zero Trust.
**Scope:** Source-read evidence verification at Antigravity PreToolUse, not a new doctrine.

## Changed files
- New verifier: governance/kpgs-vnext/security/entry_read_attestation.py
- Existing gate integration: scripts/kpgs_pretooluse_gate.py (on the PR #403 boundary)
- Synthetic checks: tests/test_gsmb_entry_read_attestation.py
- Explicit trusted-host context field entry_admission_mode="enforce" enables mandatory signed admission. Legacy mode preserves PR #403 behavior and **is NOT verified GSMB source-read enforcement**.

The signed claims bind actor, role, tenant, domain, task, session, lease-token digest, policy digest, source populations, versions, incident references, trusted-host risk-probe result and 15-minute validity using Ed25519 verification.

## Required source aliases (not replacement doctrine)
- Local: local:home, local:legacy, local:now, local:entryway correspond to Local 00-Home, MAIN-BRAIN Legacy, Local root NOW and stateless renter entryway.
- Cloud: cloud:agents, cloud:now, cloud:incident-index correspond to AGENTS.md, root NOW.md and docs/swarm-ops/gsmb_security_discovery_matrix.md.
- Drive: drive:admission, drive:agent-homes, drive:bulletin correspond to existing IDs 1VsoUbxEfIPAAEI3qN_bljpHZrVOWox9CkDvz_a3EI9I, 1ftL62fLi6zHhb-bAQZlm1009ZErNv4GtnzoYw-v8yOQ, 1Y9PlW4dMDePIF6tQdCKMdEcxlOzfcqJSzNb7OcwppRw respectively.

The trusted host must resolve aliases to authoritative paths/IDs, current versions and authenticated host read events. The host, not the agent, supplies expected_source_versions. If a population is unavailable, no attestation for it may be issued. Cross-estate mutation requires a separately approved scope.

## Required trusted-host issuance SOP (not implemented here)
1. Authenticate actor and owner grant outside model context.
2. Read sources from actual provider (Local runner, GitHub, Drive), record exact SHA/revision/digest and trusted host read event; preserve contradictions.
3. Retrieve relevant prior incidents using host events, not agent assertion.
4. Conduct a bounded risk probe on prompt injection, deceptive completion, monitoring tamper, exfiltration and tool scope, with externally verified rubric. This probe is diagnostic, not execution authorization.
5. Compare current versions to independently pinned manifest; sign canonical claims using a private key stored outside renter-writable files, prompts, environments and repo.
6. Supply public verification keys and the signed claims in trusted non-renter-writable hook context. Verify signed session, task, policy, lease, source versions and expiry at every material action.
7. Apply scoped capability lease and restriction checks after admission, and independently mediate remaining tool hosts or withhold their write credentials.

A self-asserted "I read it" never suffices. A model controlling the signer voids the boundary.

## Test and release limitations
Fixtures exercise missing receipt, unsigned edit, stale source, absent Local evidence, wrong session/task/actor/tenant/role, lease and policy binding, missing incident, duplicate reads, expiry and risk-probe failure. The PreToolUse integration is tested in isolation.

Not tested: real provider reads, independent key custody, persistent replay/nonce claim, OS containment, host hook installation, privileged Drive/Local interceptors, fresh-agent recurrence, serving runtime or owner-approved deployment.

## Blocking gates
- Parent PR #403 review and exact-head CI.
- Authenticated source-read issuer outside agent control.
- Independent tests of tool hosts and read-only recovery.
- Separate Local attestation; no cross-population assumption.
- Owner review before merge or production credentials.

**Status:** CODE CANDIDATE / FIXTURE TESTS PENDING CI / RUNTIME UNKNOWN/HOLD.
