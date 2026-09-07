# RUNE Cross-Link (Project-Rune ↔ poc-vs-foc)

**Do not rewrite** `poc_foc_enforcer.py`. RUNE adds fail-closed endorsement receipts; this folder remains the GSMB VOC immune system.

| RUNE FoC / PoC scenario | Expected | FoC affinity | Runnable |
|---|---|---|---|
| METR-style shared writable channel | Block without endorsement | ContextBleed / GhostExecution | Project-Rune `tests/test_scenarios_poc_foc.py` |
| Multi-agent consensus vote | Reject (consensus ≠ endorsement) | SemanticDrift | same |
| SOUL.md identity write | Gate → human endorse | ContextCorruption / SemanticDrift | same |
| Completion claim without receipt | Block | GhostExecution | same |
| Human-endorsed single-agent path | Allow + ledger receipt | PoC | same |

## Cloud product

- Repo: https://github.com/RobynAwesome/Project-Rune
- `main`: `029d11e` (seeded MVP)
- Active work: `cursor/rune-pending-decisions-impl` @ `4e47382` — PENDING-001 Ed25519 / PENDING-002 independence_claimed / PENDING-003 fail-open REVISE (**implemented, not owner-endorsed**)

## Local metal

- Vault seed: `Schematics/28-Project Rune` (gitignored; disk authority)
- Checkout: `C:\Users\rkhol\source\repos\Project-Rune`

## Session boot

See `docs/swarm-ops/RUNE_SESSION_SEED_2026-09-07.md`.
