# AI Frontier Map

> **Status:** Phase 1 — provenance-first corpus construction  
> **Authority:** KPGS / Introduction-to-MCP

The AI Frontier Map converts public AI repositories into an evidence-backed engineering-intelligence graph. The unit of analysis is not a repository name; it is a provenance record linking the observed repository to its upstream developer, original source, technical primitive, capability/risk surface, licence and permitted reuse mode.

## Pipeline

```text
OyaAIProd corpus
  -> enumerate every repository
  -> classify provenance
  -> resolve upstream parent/source
  -> recover original developer + project metadata
  -> locate SafeSkill scan/PR evidence
  -> extract security surface
  -> identify technical primitive
  -> resolve licence
  -> score frontier value
  -> calculate KPGS convergence
  -> ADOPT / ADAPT / STUDY / MONITOR / REJECT
```

## Immutable rules

1. **No primitive without provenance.**
2. **No code without licence.**
3. **No convergence without validation.**
4. **Do not equate `fork:false` with original authorship.** Detached forks require commit/PR/history evidence.
5. **Do not rank by stars alone.** Frontier value measures engineering signal, not popularity.
6. **Collector facts and analyst inferences remain separate fields.**
7. **Repository ID outranks owner/name for identity.** Owner transfers and renames must preserve historical names while the stable GitHub repository ID anchors lineage.

## Reuse membrane

- **CODE REUSE** — licence explicitly permits reuse and all obligations are preserved.
- **ARCHITECTURAL REUSE** — understand the public pattern and independently implement it.
- **RESEARCH ONLY** — study the project but do not import implementation code.

Every reuse receipt records:

```text
UPSTREAM + AUTHOR + REPOSITORY + COMMIT SHA + LICENSE + DISCOVERY DATE
+ WHAT WE LEARNED + WHAT WE TOOK + HOW WE CHANGED IT
```

## Frontier score

| Dimension | Weight |
|---|---:|
| Novelty | 20% |
| Technical depth | 20% |
| Composability | 20% |
| Ecosystem relevance | 15% |
| KPGS relevance | 15% |
| Current activity | 10% |

Each dimension is scored 0–5 and normalized to 100. `confidence_score` is independent: value and evidentiary certainty are not the same thing.

## Product map × risk map

**Product:** problem, capability, architecture, protocol, integrations, composability, novel abstraction.

**Risk:** filesystem, network, secrets, database, browser, process execution, repository mutation, cloud access, authentication, prompt injection and taint flow.

## Convergence verdicts

- **ADOPT** — directly reusable and worth integrating.
- **ADAPT** — valuable primitive; independently implement/adapt for KPGS.
- **STUDY** — important intelligence; no implementation decision yet.
- **MONITOR** — immature/emerging and worth tracking.
- **REJECT** — redundant, incompatible, unsafe or irrelevant.

## Phase 1 deliverables

- `provenance-record.schema.json` — canonical record contract.
- `tools/ai_frontier_map/collect_oya_corpus.py` — deterministic GitHub metadata collector.
- `tools/ai_frontier_map/validate_corpus.py` — local/CI invariant gate.
- `data/ai-frontier-map/seed.records.jsonl` — verified seed evidence.
- `.github/workflows/ai-frontier-map-gate.yml` — provenance/reuse CI gate.

The collector intentionally does **not** invent technical-intelligence fields. Those are populated only after source inspection.

## 11 November 2026: unified intake evolution (review candidate; not canonical release)

This section extends, and does not replace, the original OyaAI collector and provenance graph.
Source families now include historical OyaAI discoveries, owner-fork research and independently
discovered upstream repositories. Their **stable repository identity is never inferred from a name**.
The existing Oya seeds remain valid; the contract accepts new `provenance.origin_kind` and
`observed_repo` fields, keeping unknown source IDs, licences and commit SHAs null rather than inventing them.

The offline adapter `tools/ai_frontier_map/ingest_discoveries.py` consumes JSONL discovery
observations into the existing schema. It imports the original Oya collector's blank-score
template and always emits research-only `STUDY` records. It neither scans the user's machine nor
contacts GitHub, executes external code, imports sources or grants reuse rights.

The actual 10 November five-repository discovery is recorded under
`data/ai-frontier-map/intake-2026-11-10.jsonl`, linked to prior issues #371–#375.
The existing CI workflow validates old seeds, generates/validates the new records,
runs negative tests, and runs the already-present KPGS renter/Black Mask/Bracket
and Security Playground fixture checks on a disposable hosted runner. Those drills
cannot establish Windows Local parity, physical sandbox isolation, independent
agent agreement or production authorization.

Owner directive: do not split unfinished Oya work from new discovery work. The original
Oya Phase 1 corpus and today's five new candidates are source populations of ONE
AI Frontier Map. The full generated Oya corpus on Cloud default branch was absent
at last read; restore/verify that population as an incremental source lane, not as a
new product or a pretext to block present intake. Do not label this review branch
as a ratified protocol version until independent review and actual receipts exist.

**Acronym versioning:** Current `docs/swarm-ops/KPGS_PROTOCOL_REGISTRY.json` specifies
**BMP = Black Mask Protocol** with five pillars and fifteen commandments. Earlier
UBP source-local "Blueprint Management Protocol" terminology is a historical
name conflict, not an equally authoritative current expansion of BMP. Preserve
that dated source as evidence while following the registry/current owner instruction.
