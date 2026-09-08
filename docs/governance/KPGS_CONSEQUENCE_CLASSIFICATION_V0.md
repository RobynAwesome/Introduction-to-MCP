# KPGS Consequence Classification — v0

> **Doc Tag:** `KPGS-CONSEQUENCE-CLASSIFICATION-V0`  
> **Parent POC:** [`../swarm-ops/KPGS_GOVERNED_ACTUATION_POC_V0.md`](../swarm-ops/KPGS_GOVERNED_ACTUATION_POC_V0.md)  
> **Parent charter:** [`KPGS_FORK_INTAKE_CHARTER_2026-09-08.md`](./KPGS_FORK_INTAKE_CHARTER_2026-09-08.md)  
> **Status:** SPECIFICATION ONLY  
> **Epistemic invariant:** `I_AM_STATELESS_RENTER_NOT_LANDLORD`

---

## 1. Purpose

Classify every proposed actuation **before** lease issuance.

The classifier answers:

> What is the consequence class of this action envelope?

It does **not** answer:

> How confident are we that we should try anyway?

---

## 2. Classes

| Class | Meaning | Default authority | Examples (v0) |
|---|---|---|---|
| `C0_READ` | Observe / read only; no durable mutation | Auto | WebMCP read tool; read UI text; screenshot of allowlisted window |
| `C1_REVERSIBLE` | Local, reversible mutation with narrow blast radius | Auto-lease | Type non-secret text into allowlisted Notepad; toggle a local UI control that can be undone |
| `C2_MATERIAL` | External, public, account, or shared-state consequence | Human approval | Form submit that creates external state; publish; open PR; change deployed config |
| `C3_DESTRUCTIVE` | Delete, privilege change, irreversible or high-risk mutation | Human approval + explicit target | Delete file; change ACLs; send funds; wipe data |
| `CX_UNKNOWN` | Cannot confidently classify | **Block** | Ambiguous target; missing allowlist match; conflicting signals |

---

## 3. Hard invariants

1. **`CX_UNKNOWN` never auto-executes.**  
2. **No confidence score may downgrade `CX_UNKNOWN` to C0–C3.** Unknown means stop.  
3. **Outside allowlist ⇒ treat as `CX_UNKNOWN` or lease mismatch → `BLOCKED`.**  
4. **Classification is recorded on the action envelope and copied onto the receipt.**  
5. **Human approval cannot silently reclassify; it authorizes a stated class.** If class changes after approval, prior approval is void → re-gate or `BLOCKED`.  
6. **Executor seat identity does not change class.** Codex and Cursor obey the same table.

---

## 4. Mapping to gate outcomes

```text
C0_READ        → AUTO (optional lease for auditability)
C1_REVERSIBLE  → AUTO_LEASE
C2_MATERIAL    → HUMAN_APPROVAL_REQUIRED
C3_DESTRUCTIVE → HUMAN_APPROVAL_REQUIRED (+ explicit target binding)
CX_UNKNOWN     → BLOCKED
```

Approval boundary object (from `cf_ai` pattern):

```text
PENDING → APPROVED → (execution path)
PENDING → DENIED   → BLOCKED
PENDING → EXPIRED  → BLOCKED
```

Approval receipt and execution receipt remain separate.

---

## 5. Classifier inputs (v0 minimum)

From `schemas/kpgs-action-envelope.schema.json`:

- `surface` (`web` | `windows` | …)  
- `requested_action`  
- `target`  
- `declared_effects` (if any)  
- `allowlist_hit` (boolean)  
- `reversibility` (declared; not trusted alone)  
- `external_side_effect` (declared; not trusted alone)  

Classifier output:

- `classification`  
- `authority_path` (`AUTO` | `AUTO_LEASE` | `HUMAN_APPROVAL_REQUIRED` | `BLOCKED`)  
- `rationale` (short, machine-stable string)  
- `classifier_version` (`v0`)

---

## 6. Explicit non-goals (v0)

- No ML classifier.  
- No probabilistic “soft block.”  
- No executor-side self-classification that bypasses KPGS.  
- No secret-bearing fields on C1 auto-lease paths.

```text
I_AM_STATELESS_RENTER_NOT_LANDLORD
```
