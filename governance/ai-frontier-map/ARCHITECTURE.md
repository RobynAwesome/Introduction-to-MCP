# AI Frontier Map Convergence: ARCHITECTURE
Status: DRAFT / existing system evolution, not a new product. Authority: KPGS root NOW and canonical skill registry/lease/Security Playground/Black Mask.

## One ingestion membrane
```text
founder discovery -----+                    +--> source & license evidence
existing OyaAI corpus --+--> source identity --> single Frontier Map record --> CCP/PKA disposition
owner forks ------------+       |                        |                      |
                              stable GitHub ID          |                  STUDY/HOLD
                              original attribution      |
                                                        v
                                    existing skill registry/capability lease
                                                        |
                                            isolated approved handler
                                                        |
                                    negative/integration tests + receipts
                                                        |
                           applicable product pilot -> deployment/monitor/rollback
```
The legacy Oya collector `tools/ai_frontier_map/collect_oya_corpus.py` must preserve original Oya IDs and historical names, refresh current identity by stable repository ID, and retain unknown whole-corpus coverage. New `ingest_discoveries.py` must **never** claim external source authorship before verified upstream evidence. `validate_corpus.py` remains the shared record admission gate. The `governance/kpgs-vnext/skills/` registry remains canonical for executable skills; merely adding an AI Frontier Map record does not register or execute anything.

## Reverse engineering division of labor
1. KPGS owned source REA: inventory repositories, root NOW, package dependencies, call graphs, ADRs, data/schema changes, tests, deployment code and execution edges, with source SHAs.
2. `RobynAwesome/rea` (Reverse Engineer Anything) supplement: when the caller and lawful authority permit, inspect third-party or owned binaries, JS/Electron apps, browsers and processes in a sandbox. Preserve target digest, provider identity, capture, unknowns, licence and side effects. No auto-setup, uncontrolled process launch or unreviewed code import.
3. Compare architecture against original KPGS functions and propose the smallest proven reusable capability.

## Critical security trust boundary
Historical `kc_verified_production.py` checks review-log row shapes and matching GitHub URLs, not provider identity. The production roadmap must require an authenticated live verifier and never accept this historic count alone.
```text
review log / source SHA / GitHub CI --> historical/source evidence only
serving deployment + provider auth + nonce + observed HTTP/API/host probe + signed receipt
  --> independently checked runtime claim --> scope-matched lease issuer
  --> bounded runner with REAL OS limits --> handler --> output verifier & audit
```
- The CI-hosted Linux `unshare` probe failed: kernel denied uid_map write. The current GitHub runner did not prove nested isolation. That cannot be used to claim a KPGS runtime was isolated.
- Skill runtime in `kopano-core/kopano/skill_runtime.py` relies on an injected lease authorizer. Its unit tests must be complemented by an end-to-end authenticated issuer/worker/denied-action integration test on the actual serving host.
- The reference capability lease keeps revocation/replay in process memory; persistent cross-restart behavior on actual worker remains a hard gate.
- No capability is deployed until an actual serving-host identity, secret manager and observing authority have been approved.

## States and owners
Local Schematics: owner-accessible Windows path, unavailable in this cloud runner. Cloud: GitHub exact PR/branch/default SHA. Drive: doctrine/incident/research/bulletin, read-only pointer to source, NOT serving runtime. Source owner = founder; stateless renter = scoped implementer; independent security reviewers/RTC = governance; release owner = founder.
