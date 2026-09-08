# Governed Actuation — test fixtures (v0)

**Parent POC:** [`docs/swarm-ops/KPGS_GOVERNED_ACTUATION_POC_V0.md`](../../docs/swarm-ops/KPGS_GOVERNED_ACTUATION_POC_V0.md)

These fixtures are **specification witnesses**, not a runnable harness yet.

Each file encodes:

1. input action envelope  
2. expected classification / authority path  
3. expected lease and/or approval objects (when applicable)  
4. expected receipt(s)

## Tests

| Fixture | Proves |
|---|---|
| `c0-read.json` | Browser read auto path |
| `c1-reversible.json` | Scoped Windows lease + observed text |
| `c2-material.json` | Human approval before external mutation |
| `c3-destructive-denied.json` | Destructive request denied → zero mutation |
| `cx-unknown.json` | Unknown / mismatch → BLOCKED, zero actuation |
| `exhausted-lease.json` | Success does not imply continuing authority |

## Invariants under test

- Declaration ≠ permission  
- Lease ≠ machine access  
- Approval receipt ≠ execution receipt  
- `FAILED` ≠ `BLOCKED`  
- `CX_UNKNOWN` never auto-executes  
- Exhausted/expired lease → `BLOCKED`

## Non-goals

No adapter code. No upstream install. No live Windows/browser automation in this folder until a later admitted POC implementation PR.
