# KPGS Continuous Behavioural Authorization — v0

> **Doc Tag:** `KPGS-CONTINUOUS-BEHAVIOURAL-AUTHORIZATION-V0`  
> **Parent POC:** [`../swarm-ops/KPGS_GOVERNED_ACTUATION_POC_V0.md`](../swarm-ops/KPGS_GOVERNED_ACTUATION_POC_V0.md)  
> **Runtime:** `kopano-core/kopano/kpgs_continuous_authorization.py`  
> **Receipt schema:** `schemas/kpgs-continuous-authorization-receipt.schema.json`  
> **Tests:** `tests/test_kpgs_continuous_authorization.py`  
> **Status:** `POC_CANDIDATE` — deterministic gate implemented; repository CI still required for promotion  
> **Epistemic invariant:** `I_AM_STATELESS_RENTER_NOT_LANDLORD`

## 1. Finding

The newly observed security finding is simple but load-bearing:

```text
LEGITIMATE_IDENTITY != LEGITIMATE_BEHAVIOUR
```

Authentication can prove which actor or credential is present. It cannot, by itself,
prove that the actor's current action still belongs to its authorized mission.

KPGS therefore separates two questions:

```text
WHO_ARE_YOU?                         -> identity / provenance
IS_THIS_ACTION_STILL_AUTHORIZED_NOW? -> continuous behavioural authorization
```

Doctrine:

> **Identity establishes provenance. Behaviour earns continued authority.**

Operational form:

> **Authenticate identity at entry. Authorize behaviour at every actuation boundary.**

This extends the existing Governed Actuation POC without changing its settled
architecture. The executor remains a renter; authority stays outside the model.

## 2. Threat distinction

### A. Impersonation

```text
credential / identity check fails
→ REVOKE session
→ zero mutation
```

### B. Behavioural compromise

The identity can remain authenticated while observed behaviour diverges from
declared intent, scoped capability, state-transition contract, provenance or
temporal authority.

Examples of deterministic signals:

- observed action differs from the action envelope;
- observed target differs from the bound target;
- undeclared state transition;
- unrelated resource access;
- cross-session persistence without authority;
- sub-agent spawn outside the current lease;
- credential-boundary access;
- privilege-boundary change.

```text
VALID_IDENTITY
+ INVALID_CURRENT_BEHAVIOUR
→ CONTAIN or REVOKE current lease
```

### C. Governance block

A valid actor may also be blocked without being compromised:

- lease missing;
- lease expired;
- lease exhausted;
- allowlist miss;
- `CX_UNKNOWN`;
- approval pending/denied/missing;
- class/authority-path mismatch.

A governance block is not evidence of malicious behaviour. KPGS keeps that
distinction explicit in receipts.

## 3. No trust-score bypass

The runtime emits a boolean trust vector:

```yaml
identity: true|false
authority: true|false
intent: true|false
provenance: true|false
state: true|false
behaviour: true|false
temporal: true|false
```

There is deliberately no weighted aggregate score.

```text
ONE_FAILED_INVARIANT
!=
AVERAGE_IT_AWAY
```

A strong identity signal cannot compensate for an invalid lease. A valid lease
cannot compensate for behaviour drift. Confidence cannot downgrade `CX_UNKNOWN`.

## 4. Continuous gate

```text
ACTION ENVELOPE
    ↓
IDENTITY ATTESTATION
    ↓
ROLE BOUNDARY
    ↓
ALLOWLIST + CONSEQUENCE CLASS
    ↓
AUTHORITY-PATH CONSISTENCY
    ↓
OBSERVED ACTION / TARGET
    ↓
INSTRUCTION + CONTEXT PROVENANCE
    ↓
DECLARED vs OBSERVED STATE TRANSITION
    ↓
TEMPORAL / CROSS-SESSION CHECK
    ↓
LEASE BINDING + EXPIRY + EXHAUSTION
    ↓
HUMAN APPROVAL BOUNDARY (C2/C3)
    ↓
ALLOW | CONTAIN | REVOKE
    ↓
HASH-CHAINED RECEIPT
```

### Verdict semantics

| Verdict | Meaning | Mutation |
|---|---|---|
| `ALLOW` | Every required invariant passed for this action | allowed |
| `CONTAIN` | Current action is stopped; authority is not assumed forward | zero |
| `REVOKE` | Session or current lease is explicitly revoked | zero |

`ALLOW` applies only to the current evaluated action. It does not mint permanent
trust and does not silently increment or renew a lease.

## 5. KC, Cassy and Cassey separation

The steward lane remains intact:

```text
KC      = Save | Watch       (observer / receipt attention)
Cassy   = executor/student   (subject to the gate)
Cassey  = teacher/reviewer   (review, no policy override)
```

The runtime hard-blocks mutation requests whose actor is `kc` or `cassey`.

KC receives a watch receipt only:

```text
mutation_authority = false
```

Cassey can record teacher review but cannot turn a `CONTAIN` or `REVOKE` into an
`ALLOW`. Approval is evidence at a defined approval boundary, not constitutional
override.

## 6. Receipt continuity

Each authorization decision emits:

```text
decision_id
verdict
compromise_class
revoke_scope
actor_id
intent_id
session_id
reason_codes[]
trust_vector{}
continued_authority
mutation_allowed
observer_seat
teacher_seat
previous_receipt_hash
receipt_hash
```

`previous_receipt_hash` allows decisions to form a tamper-evident temporal chain
without treating prior success as continuing authority.

```text
RECEIPT_n
  └─ hash → RECEIPT_n+1

prior_success != future_permission
```

## 7. POC test matrix

The initial deterministic test suite covers:

1. valid identity + scoped behaviour → `ALLOW`;
2. failed identity → `REVOKE SESSION` / `IMPERSONATION`;
3. valid identity + action drift → `CONTAIN` / `BEHAVIOURAL_COMPROMISE`;
4. valid identity + credential-boundary touch → `REVOKE LEASE`;
5. unauthorized cross-session persistence → `CONTAIN`;
6. exhausted lease → `CONTAIN` as governance block;
7. material action without separate approval → `CONTAIN`;
8. KC/Cassey mutation role-boundary violation → `CONTAIN`;
9. KC/Cassey review receipts cannot override policy;
10. receipt chaining preserves decision semantics.

The isolated implementation harness passed all 10 tests before repository commit.
That is a local implementation receipt, **not** repository-wide CI proof.

## 8. Evidence classification

The workshop-derived insight is admitted conservatively:

```yaml
finding:
  legitimate_identity_not_equal_legitimate_behaviour:
    source_class: E1_DIRECT_TESTIMONY_PLUS_USER_CAPTURED_WORKSHOP_CONTEXT
    repo_translation: E3_WORKING_INFERENCE_UNTIL_IMPLEMENTED_AND_TESTED

implementation:
  deterministic_gate:
    source_class: E2_REPOSITORY_ARTIFACT_AFTER_COMMIT
    promotion_requires:
      - repository CI
      - review
      - no settled-architecture regression
```

No external research statistic from the workshop slide is promoted here as a
KPGS fact without a separately verified source.

## 9. Non-goals

- no ML anomaly classifier;
- no probabilistic soft-block;
- no computer-use adapter;
- no shell, PowerShell, registry or credential automation;
- no executor self-authorization;
- no permanent authority derived from successful prior actions;
- no teacher/observer override of failed governance invariants.

## 10. Closing law

```text
IDENTITY_ESTABLISHES_PROVENANCE
BEHAVIOUR_EARNS_CONTINUED_AUTHORITY
PRIOR_SUCCESS_DOES_NOT_MINT_FUTURE_PERMISSION
UNKNOWN_STAYS_BLOCKED
```

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
