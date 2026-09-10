# KPGS Callable Artifacts

Status: POC / additive governance surface

This directory defines small, callable governance artifacts that compose existing KPGS/GSMB engines rather than replacing them.

## Core contract

Each artifact is a package with:

- `artifact.yml` — declarative identity, model-deliberation, protocol, evidence, parser, skill, and ledger contract.
- `agent.py` — Python adapter compatible with Google ADK-style `Agent` construction.
- optional supporting schemas/tests as the artifact graduates.

The artifact layer must preserve the RTC Evolution separation:

`IDENTITY != SEAT != INTERFACE != MODEL != TASK != AUTHORITY`

Every invocation must produce or carry a runtime envelope recording the resolved identity, seat, interface, model, task, scope, evidence refs, and receipt target.

## Model deliberation

`interface_auto` is a KPGS orchestration policy, not a claim that Google ADK accepts a literal model named `auto`.

The IDE/interface may choose its preferred model. Before ADK agent construction, that selected model must be exported into the runtime envelope (default environment binding: `KPGS_INTERFACE_SELECTED_MODEL`). If the interface has no Auto mode, the caller chooses a model explicitly and records that choice.

No model selection may be silently invented by the artifact.

## Existing engines this layer composes

- `kopano-core/kopano/fep_engine.py` — FEP reconstruction and E1-E4 evidence classes.
- `kopano-core/kopano/pka_kmec_jennifer_bridge.py` — KMEC parser fabric, Apple/Android deployment stages, PKA admission, offline reconciliation, Smart Ledger receipts.
- `kopano-core/kopano/swfus_engine.py` and `kopano-core/kopano/protocols.py` — SWFUS surfaces, with historical semantic drift that must remain versioned rather than flattened.
- `skills/awesome/` and `skills/pka/` — reusable skill surfaces.

## Five artifact groups

The registry is `groups.yml`.

1. **FEP — Forensic Evolution Protocol**
2. **Epistemic Proof & Possibility**
3. **Runtime State, Sync & Smart Ledger**
4. **Identity, RTC & Model Deliberation**
5. **Design, Skills & Product Translation**

Each group starts with five artifact slots. Slots are roadmap entries, not proof of implementation.

## Governance rules

1. Artifact YAML is orchestration metadata, not canonical truth by itself.
2. E1 testimony, E2 repository evidence, E3 inference, and E4 unknown must remain distinguishable.
3. `CRUD != truth`; mutation requires an epistemic/admission gate before authoritative ledger persistence.
4. Auto-selected models must be receipted with provider/model/interface provenance.
5. Acronym drift is versioned. A later expansion does not erase an earlier historical meaning.
6. A selected CCP candidate is not POC until validation/reality evidence supports it.
7. Smart Ledger history is append-only; correction happens through supersession/reversal lineage, not silent rewrite.
8. Network skill references are pointers. Their availability and version must be checked at invocation time.
9. High task authority does not imply estate-wide GSMB structural authority.
10. Promotion from POC to canonical use requires tests, receipts, and the correct canonical owner.

## First POC

`fep/depiction-of-nature-and-society/`

Its job is to create an evidence-bearing depiction of how natural conditions and social systems interact while explicitly separating observation, testimony, inference, unknowns, and causal claims.
