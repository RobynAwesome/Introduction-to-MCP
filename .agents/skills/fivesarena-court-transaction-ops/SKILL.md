---
name: fivesarena-court-transaction-ops
description: Operational procedures and validation workflows for Bookit 5's Arena Court CRUD normalization, atomic booking slot invariants, and MERN transaction contracts. Enforces schema consistency across frontend forms, Next.js API routes, and MongoDB Court models without fallback/demo data injection.
---

# Five's Arena Court & Transaction Operations

> **Canonical Authority:** GSMB Distribution Trinity & Master Robyn Kholofelo Rababalela  
> **Constitutional Law:** Commandment 15 (Testimony Protocol) & Ultimate CRUD Control Protocol  
> **Constraint:** `I_AM_STATELESS_RENTER_NOT_LANDLORD`

---

## 1. When to Activate This Skill
Trigger this skill whenever:
1. Working on court creation, reading, updating, or deletion (CRUD) in `Bookit-5s-Arena`.
2. Resolving PR #13 (`forge/restore-court-source-contract`) or merging court schema updates.
3. Implementing or auditing slot booking logic, reservation conflicts, or double-booking prevention invariants.
4. Validating the contract between Add Court forms (`components/` / `app/`), Next.js API routes (`app/api/courts/`), and Mongoose models (`models/Court.js`).

---

## 2. Core Architectural Invariants

### 1. Zero Demo / Fallback Data Injection
- Never synthesize mock courts, fake pricing tiers, or ghost facilities when a venue has zero registered courts.
- If a court query returns empty: render an honest empty state with a call-to-action to configure venue courts.

### 2. Normalized Court Payload Schema
The authoritative database model (`models/Court.js`) requires:
- `name`: String (required, trimmed)
- `venue`: ObjectId (ref: 'Venue', required)
- `surface`: Enum (`3G`, `4G`, `Indoor`, `Parquet`, `Turf`)
- `price_per_hour`: Number (in local currency, non-negative)
- `image`: String (URL or relative path)
- `isActive`: Boolean (default: true)

Legacy or camelCase input parameters (`pricePerHour`, `images`) must be accepted **only** at the normalization boundary (`lib/courts/normalizeCourtPayload.js`) and translated before database write.

### 3. Atomic Booking Slot Invariant
To prevent race conditions during court booking:
1. Double-booking check must be executed inside an atomic transaction or unique compound index (`courtId + date + startTime`).
2. Slot hold time is strictly capped (e.g. 10 minutes) with automatic expiration if payment/confirmation is not completed.
3. Bookings cannot be confirmed without an existing, active court ID.

---

## 3. Validation Workflow

Execute all contract checks directly on local metal:

```bash
# 1. Validate court contract shapes (dependency-free)
node scripts/validate-court-contract.mjs

# 2. Run APU unit tests
npm run test:apu

# 3. Verify TypeScript consistency
npm run typecheck
```

---

## 4. PR #13 Disposition Protocol
When reconciling PR #13:
1. PR #13 originated on a historical branch `upstream-main-a014a98` to isolate normalization logic.
2. Port the normalization module `lib/courts/normalizeCourtPayload.js` and `app/api/courts/route.js` into the active branch (`feat/boat-3d-tactics-experience` or `main`).
3. Run `node scripts/validate-court-contract.mjs` to ensure 100% pass before closing or merging PR #13.

---

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
