# Frontier Map and KPGS Protection: ROADMAP
Date baseline: 11 November 2026. Status: ENGINEERING CANDIDATE, NOT A COMMITTED DELIVERY PROMISE.
Priorities: production-security hard gates are P0; preserving incoming frontier work is P1. Both share the same existing code and evidence membrane.

| Target date (SAST) | Lane | Owner | Deliverable | Closure evidence |
|---|---|---|---|---|
| 11 Nov | P0 Gate authenticity | Chat Forge candidate, owner review | Production roadmap denies the 19 historical URL-based rows without authenticated live verifier | Failing-by-default CLI + unit/CI negative receipts |
| 11–12 Nov | P0 Host discovery | Owner supplies actual serving environment, security authority approves read-only probe | Exact product/runner/provider inventory | Provider-specific deployment ID, serving SHA, audit identity, no secrets in chat |
| 12–13 Nov | P0 Real isolation | AG / authorized runtime/security engineer | Host-specific sandbox/namespace/container/WASM policy, denied egress/filesystem/credential cases | Real-host test outputs + cleanup/restart/side-effect receipts |
| 12–13 Nov | P0 Lease binding | Security authority + AG | Issuer/handler verified scope, revocation/replay persistence | Real worker denied cross-tenant, tampered token, wrong caller/action, expired/revoked and restarted attempts |
| 13 Nov | P0 Local parity | Owner's local agent/authorized PC operator | Hashed Local Schematics vs exact Cloud/Drive lineage | Local read receipt + list of changed/missing/stale entries; no file exfiltration |
| 13–16 Nov | P0 Fresh independent agent | Independent authorized actor | Two clean-context retrieval probes with malicious/stale distractions | Complete prompts, retrieval refs, action comparison, independent scoring |
| 16–18 Nov | P1 Original + new intake | AG implementation, Chat Forge source/proof review | Oya stable ID historical coverage plus five new candidates through same schema; source/licence/relevance and hazard review | Full corpus counts/provenance refs, five candidate bounded reviews, CI replay |
| 18–20 Nov | P1 Product pilot | Product owner + AG | Applicable first product adapter with SPEC/ARCHITECTURE/scripts/CI/DEBUGGING | Preview deployment under owner authorization, E2E runtime proof, rollback and observability |
| After gates | Release | Founder + authorized reviewers | Human-approved capability or documented not-applicable decision | Exact deployment SHA, real user journey, lease/containment receipts, rollback tested |

Dates are engineering targets subject to actual access, independent review and owner capacity, NOT claims of delivery or automated background execution. Missed date => visibly HOLD and rescope. Escalate any critical P0 weakness before making an unrelated P1 release.

## Current blockers, no gloss
- RUNTIME_VERIFIER: no authenticated serving provider verifier installed in roadmap interface; fail closed.
- OS_ISOLATION: Linux hosted namespace check denied permission; deploy-host proof absent.
- LEASE_PERSISTENCE: reference tests only; actual distributed restart/replay and caller binding not proven.
- LOCAL_PARITY: OneDrive connector search for Schematics and NOW.md returned no accessible results; Windows PC not reachable here.
- FRESH_AGENT: no independent connected KPGS agent/evaluation runnable from this interface was found; test not performed.
- PRODUCT: no authorized pilot target, environment and production verification receipts selected.
- OYA_COVERAGE: stable-ID recovery of 4 seed rows only, NOT full corpus inventory.

## Prioritization invariant
Every new discovery is eligible for immediate STUDY/source receipt while critical security stays HOLD. No unsafe execution or release. Historical Oya work and recent source candidates are branches of ONE capability evolution chain, never separate backlog engines.
