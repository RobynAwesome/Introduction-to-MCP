# GSMB POINTER UPDATES

> **Current pointer correction — 2026-09-11T14:51:29+02:00:** Applied into `Schematics/21-KOPANO-PHU GOVERNACE SYSTEMS/MAIN-BRAIN/GSMB_SOVEREIGN_POINTER_REGISTRY.json` (seed pass `GSMB_SEED_UPDATE_2026-09-11`).  
> - `INTRODUCTION_TO_MCP.current_revision` → `7556c8aa727ce332f8c73190b2773ff66cdd5b35` (RobynAwesome = Kopano-Labs master)  
> - Local preservation remains dirty `codex/kc-sovereign-gui-full-dev` @ `f7ed0e308cb499c89dc4ea399f188697b1406f92`  
> - `FIVES_ARENA.current_revision` → `c5a4bd1978b22b36538ab690c78fe18d49a0305e` (RobynAwesome/main); PR #13 still OPEN (`d40a5e2f` → `1be66aee`)  
> Receipt: `docs/governance/GSMB_SEED_UPDATE_2026-09-11.md`

> **Prior pointer correction — 2026-09-10T07:30:16+02:00:** Treat the August 29 values below as historical. `INTRODUCTION_TO_MCP` current cloud master is `40a31fe8eb54d9943f79ea9b546a89fffc553a2b`; the preserved local checkout is dirty `f7ed0e308cb499c89dc4ea399f188697b1406f92`. `FIVES_ARENA` current RobynAwesome/main is `c5a4bd1978b22b36538ab690c78fe18d49a0305e`; PR #13 is still open at `d40a5e2fdf9fb20f2d95c904b5dae9caccd2280b` against declared baseline `a014a98f53e91b99de061c48f962350a006cf154`. See `CA_ESTATE_RECONCILIATION_REFRESH_2026-09-10.md` and the Bookit validation receipt.

> **Authority:** AntiGravity (Seat 10 / CF)  
> **Generated:** 2026-08-29T03:55:00+02:00 (SAST)  
> **Target file:** `Schematics/21-KOPANO-PHU GOVERNACE SYSTEMS/MAIN-BRAIN/GSMB_SOVEREIGN_POINTER_REGISTRY.json`  
> **Rule:** Update pointers only — **do not copy source repos into GSMB.**

---

## Required pointer corrections

### INTRODUCTION_TO_MCP

| Field | Current (stale) | Corrected |
|-------|-----------------|-----------|
| `current_revision` | `f512a38b` | `7973d64b74a1e037a234f1ac45381c8f1ef5f730` |
| `last_verified` | 2026-08-28 | 2026-08-29 |
| `validation_receipts` | add | `rtcp_pipeline_8_tests_pass`, `estate_reconciliation_20260829` |
| `epistemic_limits` | add | `12 uncommitted local files including RTCP pipeline` |

### KMEC

| Field | Current | Corrected |
|-------|---------|-----------|
| `local_path` | `null` | `C:\\Users\\rkhol\\kpgs-morning-engine-core--kmec-` |
| `current_revision` | `HEAD/main` | `ce7017060f1dd530992d413374e11c0742dbf6a7` |

### PKA (new pointer — missing from registry)

```json
{
  "entity_id": "PKA",
  "canonical_name": "Partial Knowable Algebra",
  "generation": "GEN_III",
  "primary_sources": ["https://github.com/RobynAwesome/Partial-Knowable-Algebra"],
  "local_path": "C:\\Users\\rkhol\\Partial-Knowable-Algebra",
  "remote_repository": "https://github.com/RobynAwesome/Partial-Knowable-Algebra",
  "current_revision": "0abc68810ee5799f4bb703f8bb99fb2bf11b3e86",
  "purpose": "Observational D/F/G/R membrane + 13 FOC diagnostic groups",
  "authority_domain": "epistemic_governance",
  "current_state": "OPERATIONAL",
  "dependencies": ["INTRODUCTION_TO_MCP", "KMEC"],
  "last_verified": "2026-08-29T03:55:00+02:00",
  "reconstruction_path": "git clone ... && python -m pytest"
}
```

### SEARCH_ENTITY_ARCHITECTURE (new pointer)

```json
{
  "entity_id": "SEA",
  "local_path": "C:\\Users\\rkhol\\Search-Entity-Architecture",
  "current_revision": "f67b57184b97617ef5e711cfbb6c7e73dc2ea4c4",
  "dependencies": ["KOPANO_LABS_WEBSITE"]
}
```

### AYA_AI, AMAPHU_APP, PROJECT_JENNIFER, SOVEREIGN_HUB, INTERNS

Set `local_path` from `null` to actual `C:\Users\rkhol\...` paths (all verified ALIGNED).

### FIVES_ARENA

| Field | Current | Corrected |
|-------|---------|-----------|
| `primary_sources` | Kopano-Labs only | **Add** `RobynAwesome/Bookit-5s-Arena` as canonical |
| `current_revision` | `1fb48e91653cc1c016de85130eaf2c42c57abe64` | RobynAwesome main `91b8a7e0...`; archive branch `b1cdfaf7...` |
| `current_state` | `REMEDIATION_PR_OPEN` | `RECONCILIATION_REQUIRED` |
| `epistemic_limits` | add | `Local checkout tracks Kopano-Labs fork — diverged from RobynAwesome` |

### CRISISCONNECT

| Field | Current | Corrected |
|-------|---------|-----------|
| `primary_sources` | Kopano-Labs/CrisisConnect | **RobynAwesome/crisis-connect** (Gen III) |
| `local_path` | `C:\Users\rkhol\CrisisConnect` | `C:\Users\rkhol\crisis-connect` |
| `current_revision` | HEAD/master | `97de0b60273be8a8440193623499e0054d06c0af` |
| `supersedes` | — | `Kopano-Labs/CrisisConnect` |

### KASILINK

| Field | Current | Corrected |
|-------|---------|-----------|
| `remote_repository` | Kopano-Labs/kasi-link URL | `https://github.com/RobynAwesome/KasiLink` (canonical; Kopano-Labs mirror same SHA) |
| `epistemic_limits` | add | `kasi-link-clean is diverged — do not use` |

### STARFALL_SALVAGE

| Field | Current | Corrected |
|-------|---------|-----------|
| `current_revision` | HEAD/main | `1cdfb3024f71fcec8a2c4ff69f539858dd34db8f` |
| `current_state` | `PROVEN` | `WITNESSED_HOLD` per NOW.md |
| `epistemic_limits` | add | `Local checkout 8 commits behind` |

### CLASSROOM50 (new pointer)

```json
{
  "entity_id": "CLASSROOM50",
  "local_path": null,
  "remote_repository": "https://github.com/RobynAwesome/classroom50",
  "current_revision": "1ca4604c20d8e7433ef33d0148fdf3ecb5012edc",
  "sync_status": "CLOUD_ONLY",
  "reconstruction_path": "git clone https://github.com/RobynAwesome/classroom50"
}
```

### DIRISA_CORNERSTONE (new pointer — Master's 5-month GSMB spine)

```json
{
  "entity_id": "DIRISA_CORNERSTONE",
  "canonical_name": "DIRISA 2026 Talk 26 — POC vs FOC in Data Governance",
  "generation": "GEN_III_THESIS_ROOT",
  "primary_sources": [
    "Schematics/21-KOPANO-PHU GOVERNACE SYSTEMS/Kholofelo Robyn Rababalela/Educational Work Ecosystem/DIRISA/contribution.pdf",
    "Schematics/21-KOPANO-PHU GOVERNACE SYSTEMS/Kholofelo Robyn Rababalela/Educational Work Ecosystem/DIRISA/book-of-abstracts.pdf"
  ],
  "local_path": "Schematics/21-KOPANO-PHU GOVERNACE SYSTEMS/Kholofelo Robyn Rababalela/Educational Work Ecosystem/DIRISA",
  "authority_domain": "institutional_research",
  "governance_lane": "DIRISA_RESEARCH",
  "current_state": "CANONICAL_GROUND_TRUTH",
  "dependencies": ["INTRODUCTION_TO_MCP"],
  "reconstruction_path": "Read contribution.pdf + RTCP_PIPELINE_CRUD_SWFUS_BP_BMP_POCvsFOC_VNEXT.md"
}
```

---

## Schematics navigation updates (not pointer JSON)

1. Add `21-KOPANO-PHU GOVERNACE SYSTEMS` to root `Schematics/index.md` Top-Level Map.
2. Add `DIRISA - Index.md` under DIRISA folder (markdown index for PDFs).
3. Wire `Ecosystem-Index.md` → DIRISA path.
4. Bulk-fix `21-KOPANO LABS ECOSYSTEM` stale links (~34).

---

## Registry file location

Primary: `ACTIVE_PROJECT_REGISTRY.json` (repo root, this reconciliation pass)  
Canonical long-term: merge deltas into `GSMB_SOVEREIGN_POINTER_REGISTRY.json` on Master approval.
