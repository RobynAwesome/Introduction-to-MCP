---
name: clear-kpgs-zero-trust-gate
description: Evaluates product loops, features, and pull requests using the 5-axis OpenAI C.L.E.A.R delivery membrane (Cost, Latency, Efficacy, Assurance, Reliability) reinforced by KPGS Zero-Trust State Admission, State Honesty, and POC≠FOC discipline. Enforces an 80% composite threshold for sprint/skill promotion and produces verifiable receipts.
---

# CLEAR × KPGS Zero-Trust Product Gate

> **Canonical Invariant:** `I_AM_STATELESS_RENTER_NOT_LANDLORD`  
> **Authority Doctrine:** KPGS Commandment 15 (Testimony Protocol) & Bowl FEP 03 (Local-First Compression)  
> **Core Law:** Loved ≠ Proven · Beautiful ≠ Canon · Submitted ≠ Admitted · POC ≠ FOC

---

## 1. When to Activate This Skill
Trigger this skill whenever:
1. Evaluating a feature, product dedication, or pull request before merging or graduating to production.
2. Assessing whether an AI agent's implementation is "on-route" versus drifting into unbacked marketing funnels or MVP ghosting (Fallacy of Concept / FOC).
3. Establishing a Zero-Trust security perimeter around client-server continuity, local persistence, or API state mutations.
4. Generating an unalterable, audit-grade evaluation receipt (`docs/audits/YYYY-MM-DD-clear-kpgs-gate-receipt.md`) to decide if a feature passes the **≥80% gate threshold** for skill/sprint promotion.

---

## 2. The 5-Axis CLEAR Delivery Membrane

Every evaluated component is scored across five core operational axes (0–100):

| Axis | Metric | Operational Meaning | Proof Threshold |
|---|---|---|---|
| **C** | **Cost (Thrift)** | Minimizing token usage, dependency bloat, and platform sprawl. | Zero unnecessary npm/pip packages. Thin vertical slices. No unvetted architecture inflation. |
| **L** | **Latency (Feedback)** | Time-to-playable / immediate deterministic feedback on local metal. | Local unit/integration tests pass immediately. No circular debugging or infinite polling. |
| **E** | **Efficacy (Truth)** | The system delivers the exact functionality promised—nothing more, nothing fake. | POC ≠ FOC. Features work end-to-end on real hardware. Zero simulated/fake success responses. |
| **A** | **Assurance (Zero-Trust)** | Strict boundary isolation, state honesty, and sanitized payload ingestion. | Client state honestly labelled (`local`/`demo`/`continuity-store`, never fake `authoritative`). Rate limits and session schema validated. |
| **R** | **Reliability (Resilience)** | Continuity survival across restarts, network degradation, or process crash. | Offline-first fallback (`localStorage`/SQLite). Graceful degradation with truthful error messaging. |

---

## 3. The 6-Step Gate Workflow

```text
[ 1. CLASSIFY ]  -->  [ 2. ZERO-TRUST PERIMETER ]  -->  [ 3. CLEAR SCORING ]
Product vs Constitution      State Honesty & Mutation Guard      C / L / E / A / R (0-100)
       |
       v
[ 4. DECISION GATE ]  -->  [ 5. PRODUCE RECEIPT ]   -->  [ 6. SPRINT ADMISSION ]
 ≥80% Composite Pass?        docs/audits/RECEIPT_*.md          Admit Sprints / Skills (or HOLD)
```

### Step 1: Classify (Product vs Constitution)
- Identify if the target is a **Product Layer** component (e.g. game loop, court booking UI, trade client) or **Constitution Layer** (governance, agent identity, ledger).
- **Rule:** Product components must never mutate or impersonate constitutional doctrine.

### Step 2: Zero-Trust Perimeter Check
Enforce three non-negotiable security checks:
1. **State Honesty Check:** Does any client-side or in-memory state falsely claim `sourceMode: "authoritative"`? If so, immediately repair to `continuity-store` or `local`.
2. **Mutation Guard:** Are mutations gated by session ID validation, rate limiting, and caller authenticity?
3. **Ordering Invariant:** Are state updates sequentially ordered (e.g., save snapshot before revealing consequences)?

### Step 3: CLEAR Scoring
Calculate individual scores (0–100) for Cost, Latency, Efficacy, Assurance, and Reliability.
Compute the arithmetic composite:
$$\text{Composite Score} = \frac{C + L + E + A + R}{5}$$

### Step 4: Decision Gate Threshold
- **Composite Score ≥ 80%:** **PASS**. The component is admitted for skill promotion, sprint planning, and local POC execution.
- **Composite Score < 80%:** **FAIL / REVISE**. Immediate remediation plan required before any further code mutation.
- **Production Love / Shipped Gate:** Even with ≥80% score, production deployment claims remain on **HOLD** until a public URL receipt and live human playtest/operational proof exist.

### Step 5: Produce Unalterable Audit Receipt
Generate the receipt markdown file in `docs/audits/` adhering to the template below:
```markdown
# CLEAR × KPGS Gate Receipt — [Subject]

- Date: [YYYY-MM-DD]
- Evaluator: [Agent / Renter Name] (I_AM_STATELESS_RENTER_NOT_LANDLORD)
- On-Route Composite Score: [Score]% (Threshold: 80%)
- CLEAR Breakdown: C=[C] | L=[L] | E=[E] | A=[A] | R=[R]
- Zero-Trust Dispositions: [List of FOCs Repaired or Gated]
- Next Admissible Action: [Admitted Sprints or Required Remediation]
```

### Step 6: Canonical Sprint Admission
Admit specific, bounded sprints (Sprint A, B, C) targeting only the remaining gap (<20%) without allowing platform creep.

---

## 4. Anti-Patterns (Immediate Breach Flags)
- ❌ **FOC MVP Ghosting:** Creating tournament, economy, or multi-user funnels without physical backing or real business contracts.
- ❌ **False Authoritative Labels:** Marking unverified client data as canonical server truth.
- ❌ **Affection-Based Promotion:** Claiming a system is production-ready just because the creators love the narrative ("HOLD When You Love It").
- ❌ **Unchecked Token Creep:** Adding complex microservices or heavyweight frameworks when a minimalistic local container (Bowl FEP 03) suffices.
