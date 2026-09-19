# RUNE Session Seed — 2026-09-07

**Status:** session seed / pointer receipt — **not** COMPLETE / PROVEN / DEMO READY  
**Actor note:** Code patches ≠ owner endorsement. PENDING-001/002/003 remain `PENDING`.

## What to load this session

1. **Product repo:** https://github.com/RobynAwesome/Project-Rune  
2. **Branch for decision work:** `cursor/rune-pending-decisions-impl` @ `4e47382e12b1f30a32f1161fc0679eea7f07c183`  
3. **main tip (prior MVP):** `029d11e43d02b387ebf9f36e8288be4617905673`  
4. **Local checkout:** `C:\Users\rkhol\source\repos\Project-Rune`  
5. **Local vault:** `Schematics/28-Project Rune` (metal; often gitignored)  
6. **VOC immune cross-link:** `poc-vs-foc/RUNE_CROSSLINK.md`  
7. **Registry:** `ACTIVE_PROJECT_REGISTRY.json` → `PROJECT_RUNE`

## Decisions (claim-not-endorsed)

| ID | Proposal in code | Owner status |
|---|---|---|
| PENDING-001 | Ed25519 structured signatures; HMAC not identity | `PENDING` |
| PENDING-002 | `independence_claimed`; independence unsolved | `PENDING` |
| PENDING-003 | Fail-open only with `RUNE_DEV_ESCAPE=1` + non-production; high-risk never open; `gate_bypass` receipts | `PENDING` |

## Validation receipt (automated only)

- `pytest -q` on decision branch: **38 passed, 1 skipped** (2026-09-07)
- Does **not** replace owner live gate + ledger receipt

## Estate note

OneDrive `Introduction to MCP` checkout may still be mid-rebase on `Kopano-Labs` remote — do not force-merge dirty trees into this seed. Cloud canonical for this seed push: `RobynAwesome/Introduction-to-MCP`.
