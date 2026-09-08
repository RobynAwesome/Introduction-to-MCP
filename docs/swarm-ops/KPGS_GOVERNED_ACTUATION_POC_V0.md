# KPGS Governed Actuation POC — v0

> **POC Tag:** `KPGS-GOVERNED-ACTUATION-POC-V0`  
> **Parent charter:** [`KPGS_FORK_INTAKE_CHARTER_2026-09-08.md`](../governance/KPGS_FORK_INTAKE_CHARTER_2026-09-08.md)  
> **Classification:** [`KPGS_CONSEQUENCE_CLASSIFICATION_V0.md`](../governance/KPGS_CONSEQUENCE_CLASSIFICATION_V0.md)  
> **Registry:** [`KPGS_FORK_INTAKE_REGISTRY.json`](./KPGS_FORK_INTAKE_REGISTRY.json)  
> **Schemas:** `schemas/kpgs-*.schema.json`  
> **Fixtures:** `tests/governed-actuation/fixtures/`  
> **Epistemic invariant:** `I_AM_STATELESS_RENTER_NOT_LANDLORD`  
> **Status:** **SPECIFICATION ONLY** — no adapters, no upstream install, no runtime admission

---

## 0. Claim to prove

> One rented executor can operate a browser-native surface and a Windows desktop surface, but authority remains external to the executor: every action is classified, leased, observed and receipted; sensitive actions require a human gate; unknown authority terminates as `BLOCKED`.

This implements the fork intake charter’s three-organ vertical slice (`webmcp` + `mcp-windows` + `cf_ai_approvalflow-ai`) as **pattern archaeology**, not as npm-runtime landlords.

**Forbidden claim:**

```text
LLM → computer → vibes
```

**Required claim:**

```text
A computer-using intelligence can remain a renter even while it has hands.
```

---

## 1. Core flow

```text
USER INTENT
    ↓
ACTION ENVELOPE
    ↓
KPGS CONSEQUENCE CLASSIFIER
    ↓
CAPABILITY / LEASE CHECK
    ↓
┌─────────────────────────────────────────┐
│ ROUTINE + REVERSIBLE                    │
│ → AUTO_LEASE                            │
├─────────────────────────────────────────┤
│ MATERIAL / SENSITIVE                    │
│ → HUMAN_APPROVAL_REQUIRED               │
├─────────────────────────────────────────┤
│ UNKNOWN / CONFLICT / OUTSIDE ALLOWLIST  │
│ → BLOCKED                               │
└─────────────────────────────────────────┘
    ↓
ACTUATION ADAPTER   (not implemented in v0 — contract only)
    ├── WebMCP organ (pattern)
    └── Windows UI Automation organ (pattern)
    ↓
OBSERVE RESULT
    ↓
RECEIPT
    ↓
CONTINUE | COMPLETE | BLOCK
```

Schemas:

| Object | Schema |
|---|---|
| Action envelope | `schemas/kpgs-action-envelope.schema.json` |
| Capability lease | `schemas/kpgs-capability-lease.schema.json` |
| Approval | `schemas/kpgs-approval.schema.json` |
| Action receipt | `schemas/kpgs-action-receipt.schema.json` |

---

## 2. Consequence classes (v0)

See [`KPGS_CONSEQUENCE_CLASSIFICATION_V0.md`](../governance/KPGS_CONSEQUENCE_CLASSIFICATION_V0.md).

| Class | Meaning | Authority |
|---|---|---|
| `C0_READ` | Observe/read only | Auto |
| `C1_REVERSIBLE` | Local/reversible mutation | Auto-lease |
| `C2_MATERIAL` | External/public/account/state consequence | Human approval |
| `C3_DESTRUCTIVE` | Delete, privilege change, irreversible / high-risk | Human approval + explicit target |
| `CX_UNKNOWN` | Cannot confidently classify | **Block** |

**Invariant:** No confidence score may downgrade `CX_UNKNOWN`. Unknown means **stop**, not “try harder.”

---

## 3. Lease object

The executor never receives “computer access.”

It receives a **scoped, expiring, revocable lease**:

```text
lease_id
actor_id
surface
allowed_action
allowed_target
issued_at
expires_at
max_invocations
approval_receipt
revocable = true
```

Example (valid):

```text
surface: windows
allowed_action: ui.type_text
allowed_target: Notepad
max_invocations: 1
expires_at: +60s
```

Invalid (must fail validation / CI narrative):

```text
"you can control Windows"
```

**Invariant:** Declaration ≠ permission. Lease = authority.

---

## 4. Organ contracts (pattern extraction only)

### 4.1 `webmcp` organ

Borrow only: **page declares structured tools**.

KPGS wrap:

```text
page tool
  → KPGS tool registry
  → consequence classification
  → lease
  → call
  → response validation
  → receipt
```

A webpage declaring a tool does **not** grant permission to invoke it.  
**Declaration is capability discovery. Lease is authority.**

Target graduation for upstream: `PATTERN_ONLY`.

### 4.2 `mcp-windows` organ

Charter POC shape (mandatory):

```text
Intent → classify → lease → actuate → observe → receipt → continue|block
```

**v0 allowlist only:**

- launch one allowlisted app  
- focus an allowlisted control  
- type non-secret test text  
- press one explicitly allowed button  
- read observable UI state  

**v0 denylist (hard):**

- shell / PowerShell  
- arbitrary filesystem traversal  
- credential fields  
- registry  
- “find whatever application works”  
- machine-scoped (“control Windows”) leases  

Target graduation for upstream: `PATTERN_ONLY`. Body with hands ≠ open hands.

### 4.3 `cf_ai_approvalflow-ai` organ

Boundary object states:

```text
PENDING → APPROVED → EXECUTED
PENDING → DENIED   → BLOCKED
PENDING → EXPIRED  → BLOCKED
```

**Approval and execution are separate receipts.**

| Receipt | Proves |
|---|---|
| Approval | Someone authorized this |
| Execution | This is what actually happened |

Never collapse those into one object.

Target graduation for upstream: `PATTERN_ONLY` (extract universal gate primitive).

---

## 5. Receipt semantics

Every material action minimally captures fields in `schemas/kpgs-action-receipt.schema.json`.

`result_state` enum:

| State | Meaning |
|---|---|
| `SUCCESS` | Authorized execution completed as observed |
| `DENIED` | Human gate refused; zero actuation |
| `BLOCKED` | Governance intentionally prevented execution |
| `FAILED` | Authorized execution attempted; did not succeed |
| `EXPIRED` | Lease/approval window ended before use |

**`FAILED` ≠ `BLOCKED`.**

- **Failed** = authorized attempt that did not succeed.  
- **Blocked** = governance prevented the attempt.

---

## 6. Six POC tests

Fixtures live under `tests/governed-actuation/fixtures/`.

| # | Test | Fixture | Expected |
|---|---|---|---|
| 1 | Browser read | `c0-read.json` | `C0_READ → AUTO → SUCCESS receipt` |
| 2 | Browser mutation | `c2-material.json` | `C2_MATERIAL → human approval → execute → receipt` |
| 3 | Windows reversible | `c1-reversible.json` | `C1_REVERSIBLE → scoped lease → type in Notepad → observed text → receipt` |
| 4 | Windows destructive (deny) | `c3-destructive-denied.json` | `C3_DESTRUCTIVE → approval required → DENIED → zero mutation` |
| 5 | Unknown / lease mismatch | `cx-unknown.json` | `CX_UNKNOWN` or lease mismatch → `BLOCKED`, zero actuation |
| 6 | Persistence / lease exhaust | `exhausted-lease.json` | After permitted action, unrelated follow-up → `lease exhausted → BLOCKED` |

**Test 6 is the load-bearing test:** successful execution does **not** imply continuing authority.

---

## 7. Graduation bar

The three-source slice **passes** only if all are true:

1. Web tools are discovered without implicitly granting authority.  
2. Windows action is target-scoped rather than machine-scoped.  
3. Sensitive action cannot execute before approval.  
4. Denied action demonstrably causes zero mutation.  
5. Expired/exhausted lease prevents continuation.  
6. Every material transition emits a valid receipt.  
7. An executor seat can be swapped (Codex / Astra / Cursor / etc.) without changing governance semantics.  
8. No quarantined upstream becomes root/runtime authority.

Only **after** that bar may graduation be discussed. Registry currently targets all three sources toward **`PATTERN_ONLY`**: extract organs → KPGS-native equivalents → graduate the pattern → leave upstream outside.

---

## 8. Explicit non-goals (v0)

- No adapter implementation.  
- No `npm install` of quarantined upstreams into KPGS production paths.  
- No shell, PowerShell, registry, or credential automation.  
- No bulk integration of the other nine forks.  
- No collapsing approval + execution into one receipt.

---

## 9. Closing law

> The new thing we're proving isn't that an AI can use a computer.  
> We're proving that a computer-using intelligence can remain a renter even while it has hands.

```text
I_AM_STATELESS_RENTER_NOT_LANDLORD
```
