# FOC PUBLIC SURFACE VALIDATION AUDIENCE INCIDENT — 2026-09-14

**Status:** ACTIVE CORRECTION
**Estate:** Five's Arena / `fivesarena.com`
**Source repo:** `Kopano-Labs/Bookit-5s-Arena`
**GSMB owner:** `poc-vs-foc/`
**Accountable correction seat:** Forge / ChatGPT 5.6 Sol
**Canonical local checkout path:** `Schematics/24-RTC Learning/POCvsFOC Groups/FOC_PUBLIC_SURFACE_VALIDATION_AUDIENCE_2026-09-14.md`
**Cloud mirror:** `docs/governance/FOC_PUBLIC_SURFACE_VALIDATION_AUDIENCE_2026-09-14.md`

---

## Incident

The Five's Arena public surface accumulated internal governance exposition and unverified historical/transactional framing. The visible product began explaining its own truth discipline instead of primarily helping a visitor book, play, contact the venue, or understand current services.

Observed examples included:

- `Booking truth gate`
- `Online court availability is temporarily unverified`
- public `Kopano-Phu ecosystem` / `LINKED` / `RESERVED` graph language
- `Five's Arena is one lane in a wider public graph`
- a World Cup archive promoted on the home page as historical evidence without an authoritative event receipt attached to that public claim

This is not a failure of having governance. It is a failure of **placing governance explanation where product execution should be**.

---

## FOC Classification

### FOC-G06 — NarrativeSubstitutionLoop

**Pattern:** the agent explains the problem, governance, caveat or future fix while the corrective artifact is still absent.

**Falsifier:** a concrete artifact exists first: code change, commit, test, deployment receipt, data receipt or transaction result.

**Rule:** no explanatory closure before the smallest executable correction exists.

### FOC-G07 — ValidationAudienceInversion

**Pattern:** a public product surface is optimized to reassure internal agents, architecture, governance or validators instead of serving the human visitor's job-to-be-done.

**Five's Arena primary validation audience:**

1. player / customer seeking a court, fixture, service or contact path;
2. venue/business operator completing the service;
3. only then internal governance, SEO, analytics, architecture and agent receipts.

**Falsifier:** a normal visitor can complete the primary job without needing to understand GSMB, KPGS, LINKED/RESERVED states, runtime-health semantics or proof vocabulary.

### FOC-G08 — UnverifiedPublicClaimPromotion

**Pattern:** an assumed, synthetic, stale, internal or weakly sourced claim is promoted into public truth, history, pricing, availability, status or evidence.

**Falsifier:** authoritative source receipt exists and is temporally valid for the claim being shown.

**Fallback:** when no authoritative live source exists, expose a simple bounded user action such as direct WhatsApp/call/contact confirmation. Do not replace missing truth with a governance essay.

---

## Correction Executed

Branch: `Kopano-Labs/Bookit-5s-Arena:forge/public-site-customer-truth-20260914`

Executed changes:

- removed the World Cup archive block from the public landing page;
- removed the public Kopano-Phu ecosystem graph from the landing page;
- removed the ecosystem graph and archive navigation from the active `TruthFooter`;
- replaced `Booking truth gate` and the large unverified-state warning with a customer-facing direct booking fallback;
- preserved internal governance behind the public surface rather than using the customer page as a governance report.

Current correction commits:

- `08b4197ad412c3cb4416478eeafcefb28f063e17`
- `4f3d3f66a411385bc7bf46a8e163472289b82cf9`
- `521c84072df8265fe7303bdc2d934d38c5d7ec80`
- `24944e5f002ad880731916e10e61674fbad37e72`

These hashes prove code execution. They do **not** yet prove production deployment. Production remains HOLD until merge + deployment receipt.

---

## Public Surface Gate

Before any KPGS/Kopano public-site change is admitted, ask in this order:

```text
1. WHAT HUMAN JOB IS THIS PAGE FOR?
2. WHAT AUTHORITATIVE SOURCE SUPPORTS EACH PUBLIC CLAIM?
3. CAN THE USER COMPLETE THE JOB WITHOUT READING INTERNAL GOVERNANCE?
4. IF THE SOURCE IS DOWN, WHAT IS THE SIMPLEST HONEST FALLBACK?
5. WHERE IS THE BUILD/TEST/DEPLOY RECEIPT?
```

BLOCK deployment when any of the following are true:

- internal governance vocabulary becomes primary customer copy;
- a missing source is replaced by fabricated/demo certainty;
- an archive/history claim has no authoritative receipt;
- the agent writes a long explanation instead of first producing the corrective artifact;
- the page validates the architecture while degrading the customer's task.

---

## Forge Accountability Rule

Forge is specifically bound by the following correction:

> **Execute first when execution is available. Explain only the delta, evidence and remaining HOLD state.**

A response saying `I will fix`, `I am building`, `the governance says`, or equivalent without a simultaneous artifact/receipt remains FOC-G06.

---

## Sync Rule: Cloud + Local GSMB

This file is stored at the repository path that maps directly into the local GSMB checkout:

`C:\Users\rkhol\OneDrive\Documents\Anthropic\Introduction to MCP\Schematics\24-RTC Learning\POCvsFOC Groups\FOC_PUBLIC_SURFACE_VALIDATION_AUDIENCE_2026-09-14.md`

The same law is mirrored under `docs/governance/` for cloud discoverability. A local checkout/pull is the synchronization mechanism; no agent may claim the Windows local file was written unless a local filesystem receipt proves it.

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
