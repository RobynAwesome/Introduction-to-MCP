# ALP as Temporal Witness + Homecoming Depth — CANDIDATE

**Status:** LEARNING / RTC DISCUSSION CANDIDATE — **NOT RATIFIED**  
**Date:** 2026-09-07  
**Source:** Human architectural reading of ALP idle FOC + local GSMB MICRO-HOMECOMING  
**Constraint:** `I_AM_STATELESS_RENTER_NOT_LANDLORD`

This document captures meaning. It does not rewrite ALP code strings, change thresholds, or claim production governance OS status.

## Core distinction

```text
A continuity failure is not automatically a system failure.
```

ALP idle FOC says:

```text
I cannot prove uninterrupted continuity across this gap.
```

It does **not** say:

```text
The estate is compromised.
```

## Continuity state machine (candidate)

```text
RUNNER ACTIVE
  → ticks inside expected window
  → CONTINUITY OBSERVED
  → POC (for the heartbeat claim)

expected tick missed
  → blind interval
  → CONTINUITY NOT OBSERVED
  → FOC_FLAGGED (observability gap)
  → runner returns
  → reconcile current state
  → continue / HOLD
```

**not observed ≠ did not exist.**

## Witness Mesh role (candidate)

```text
AGENT CLAIM: "I maintained continuity"
ALP:        "N min unobserved"
GSMB:       FOC_FLAGGED → reconstruct at proportional depth
```

Neither claim wins by volume. Reconstruction depth follows gap consequence.

## Mental rename

Keep canonical log token `BREACH` if already wired.

Interpret as:

```text
TEMPORAL CONTINUITY BREACH
OBSERVABILITY GAP
```

Not:

```text
SECURITY BREACH / North Korea in MongoDB
```

## Homecoming depth bands (CANDIDATE THRESHOLDS — not governance yet)

| Blind interval | Depth | Minimum actions |
|---|---|---|
| < 30 min | NORMAL | no special homecoming |
| 30–120 min | MICRO-HOMECOMING | read root NOW; compare current commit; inspect pending receipts; reconcile missed tick |
| 2–24 hr | DOMAIN HOMECOMING | current estate lane; local/cloud divergence; blockers; material changes |
| days / weeks / model replacement | FULL HOMECOMING | rebuild estate map |

Do **not** crawl the entire GSMB for every coffee gap. Do **not** ignore repeated gaps that change handoff confidence.

## NOW mutation law (candidate)

```text
An idle breach does not require NOW mutation
unless the continuity gap changes material current-state confidence.
```

Material factors may include: repeated idle breaches, unfinished mission, local mutations, agent/model change, cloud divergence.

## Gap cause taxonomy (candidate — before “schedule harder”)

```text
EXPECTED_IDLE
SLEEP
USER_PAUSE
RUNNER_FAILURE
MISSED_SCHEDULE
UNKNOWN_GAP
```

Only the last few deserve escalating concern. Wiring Task Scheduler ≤25 min without cause classification can amplify noise without fixing sleep.

## Convergence pattern (observational)

| Axis | System | Expected vs observed |
|---|---|---|
| SPACE | KPGSthree / estate | required ≠ observed |
| TIME | ALP | expected continuity ≠ observed continuity |
| IDENTITY | RTC | claimed ≠ reconstructed |
| WORK | Hub / assignment | assigned ≠ completed |
| EVIDENCE | Witness Mesh | claimed ≠ witnessed |

Shared deeper law:

```text
EXPECTED STATE ≠ OBSERVED STATE ≠ VERIFIED STATE
```

Governance is the machinery between them.

## Hub Center law (candidate)

> **Homecoming does not always mean “repair where you landed.” Sometimes Homecoming means “recognize that you landed in history.”**

A renter may return to a GSMB surface and must say:

```text
This is a preservation surface.
I can learn from it.
I must not mutate it as if it were current authority.
```

Specimen: OneDrive `Introduction to MCP` MICRO-HOMECOMING 2026-09-07 — STALE_PRESERVATION declared at root NOW while nested Now and dirty history remain useful forensics.

## Explicit non-claims

- Not ratified RTC law
- Not a replacement for threat-model security breaches
- Threshold numbers are candidates only
- Does not authorize FULL HOMECOMING from a single 50.1 min gap alone
- Does not claim Project Rune / Hub Center already implement this end-to-end
- Does not authorize cleaning/merging a declared preservation surface “to make it current”

## Admission path

RTC review → endorse / revise / reject → if endorsed, update ALP docs vocabulary + homecoming protocol + Hub Center landing rules without silently rewriting historical BREACH_LOG entries.
