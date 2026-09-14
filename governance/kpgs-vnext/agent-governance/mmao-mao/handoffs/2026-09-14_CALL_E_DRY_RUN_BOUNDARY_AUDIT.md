# CALL-E / KasiProof Dry-Run Boundary Audit — 2026-09-14

**Status:** `HOLD_LIVE_RUNTIME_PROOF`
**Authority:** Forge cloud GSMB validation lane
**KasiLink commits audited:** `d1d182bbf7cbdb0dd4ecf75013b2a0e46480bbf3`, `e92f1de39c18f9915598af722f1575aa44606afe`

## Proven progress

- The previous hard-coded-only CALL-E section has been replaced with a real CLI integration path using `call plan`, `call run`, and `call status`.
- The integration commit exists on KasiLink main.
- The subsequent dry-run receipt commit exists.
- The mandatory upstream skill PR remains separately proven.

## Boundary breach still present

The committed `--dry-run` branch fabricates provider-shaped evidence:

- synthetic `plan_dryrun_*` and `run_dryrun_*` identifiers;
- `terminalStatus = "completed"`;
- a synthetic transcript and summary;
- synthetic structured extraction;
- downstream `PKA = KNOWN` with justification claiming "Direct telephony evidence".

The committed receipt therefore looks like provider actuation evidence even though no provider was called. This is not admissible as CALL-E runtime proof.

## Additional implementation risks

1. `runId` falls back to a fabricated `run_live_*` identifier when CALL-E returns no run id. This must never happen. If execution may have been accepted without a returned id, preserve provider recovery state and do not invent evidence.
2. Human approval currently occurs before the provider plan is produced, and the script then immediately runs the call. The governed boundary should be `plan -> inspect -> explicit approval -> run`.
3. The Windows integration resolves and executes `calle.cmd`; current CALL-E guidance recommends resolving the published JS entry point and executing it with `process.execPath` / shell-free child process when embedding in Node on Windows.
4. `idempotency_enforced: true` is asserted in the receipt without a demonstrated idempotency implementation in the audited script.
5. PKA promotion to `KNOWN` is too permissive: a summary containing `open` or any transcript containing `yes` can promote certainty without independently confirming both opportunity status and listed pay.
6. The first poll begins after 5 seconds; CALL-E guidance recommends waiting roughly 60 seconds before the first status poll, then polling every 5–10 seconds.

## Correct admissible states

```text
CALL_E_CLI_WIRING_PRESENT   = PROVEN
DRY_RUN_CONTRACT_PATH       = PROVEN
LIVE_CALL_E_RUNTIME_PROVEN  = HOLD
PROVIDER_BOUND_RECEIPT      = HOLD
PKA_LIVE_RECEIPT_PROVEN     = HOLD
DEMO_READY                  = HOLD
```

## Smallest correction

Do not redesign the product. Modify only the execution/evidence boundary:

- Dry run must emit `mode: dry_run`, `provider_called: false`, `run_id: null`, `provider_status: NOT_CALLED`, and PKA `UNKNOWN` (or a clearly separate fixture-validation state), never `KNOWN` from synthetic telephony.
- Produce the CALL-E plan first. Display masked target, exact bounded goal, provider plan/confirmation summary, and region/capability state. Then ask for explicit human approval. Only after `YES` may `call run` execute.
- Remove fabricated live run-id fallback. Preserve `recovery_id` / retry-safety information if the provider returns it.
- On Windows, use the documented shell-free JS CLI entry point rather than invoking `calle.cmd` from the Node integration.
- Make PKA deterministic against explicit structured fields: both `position_open === true` and `confirmed_pay === "500 ZAR"` for `KNOWN`; contradictory pay/status -> `CONFLICTING`; one confirmed fact -> `PARTIAL`; no provider evidence -> `UNKNOWN`.
- Do not claim idempotency unless an actual duplicate-call control exists.
- Preserve the ZA unsupported result as provider capability evidence. Do not infer opportunity falsehood from provider incapability.

## Closure rule

A demo can truthfully show the dry-run contract and the region-unsupported guard, but it must not label the synthetic receipt as real CALL-E evidence. `CALL_E_RUNTIME_PROVEN` requires a real supported-region controlled call with a provider-issued run id and terminal provider evidence.

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
