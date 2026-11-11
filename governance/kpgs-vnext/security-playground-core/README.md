# KPGS Security Playground Core

**Status:** draft review candidate; fixture-only; not activated for runtime use.  
**Base:** `RobynAwesome/Introduction-to-MCP@0a8950277656266273b813ce85f93c4230d4b0ff` (current Cloud default branch at review).  
**Authority boundary:** `I_AM_STATELESS_RENTER_NOT_LANDLORD`.

The Rust CLI has two fixture lanes. The default checks Node.js version and
deployment claims using the request and result contracts in `schema/`.
`--inventory` evaluates the existing `gsmb_security_playground_inventory_gate_v1`
claim used by the Python inventory evaluator. It checks supplied asset status,
containment assertions, protected-state mutation counts and receipt references.
Both lanes classify supplied data without fetching evidence or executing a
workload. Next.js lockfile analysis and GitHub advisory mapping remain outside
this slice.

The Python evaluators remain the current compatibility reference. This crate
does not suspend them. The Rust core must not become the default caller until
the shared corpus, parity review, caller migration and rollback path pass the
existing Progressive Updates gates.

## Synthetic cases

From the repository root, play the inventory and Node cases directly:

```sh
SPP_CORE=governance/kpgs-vnext/security-playground-core
cargo run --quiet --locked --manifest-path "$SPP_CORE/Cargo.toml" -- \
  --inventory --input "$SPP_CORE/tests/fixtures/inventory-clean.json"
cargo run --quiet --locked --manifest-path "$SPP_CORE/Cargo.toml" -- \
  --input "$SPP_CORE/tests/fixtures/node-conflicting-receipt.json"
```

The same modes support `--stdin`. Copy `inventory-clean.json` into a scratch
directory and change `deny_production_network` to `false` to exercise `BLOCK`.
Set the synthetic dependency status to `unknown` on a fresh copy to exercise
`HOLD`. Exit codes are `0` for `DRILL_PASS`, `2` for `HOLD`, `3` for `BLOCK` and
`4` for `INVALID_INPUT`.

The bundled cases contain synthetic claims and advisory identifiers.

| Fixture | Expected result | Meaning |
|---|---|---|
| `inventory-clean.json` | `DRILL_PASS` | All synthetic inventory assertions meet the fixture contract. |
| `node-fixed.json` | `DRILL_PASS` / `FIXED_VERSION_CANDIDATE` | Version meets the supplied synthetic fix boundary; not a verified estate fix. |
| `node-affected-prerequisite.json` | `BLOCK` / `AFFECTED_VERSION_PREREQUISITE_MATCHED` | Synthetic affected range and prerequisite match; not live exposure. |
| `node-missing-runtime.json` | `HOLD` / `MISSING_RUNTIME_EVIDENCE` | Missing evidence stays unknown even when the fixture labels its target production. |
| `node-stale-deployment-sha.json` | `HOLD` / `STALE_DEPLOYMENT_SOURCE` | A stale deployment source cannot support a fix claim. |
| `node-conflicting-receipt.json` | `HOLD` / `CONFLICTING_RUNTIME_EVIDENCE` | Conflicting receipts remain unresolved. |

Every result sets `runtime_verified=false` and `production_authority=false`.
`DRILL_PASS` means only that a synthetic fixture reached its expected evaluator
classification. It is not proof of isolation, exploitability, safety, or
production graduation.

## Local validation

Use the declared Rust 1.91 minimum and generated dependency lockfile:

```sh
cargo fmt --manifest-path governance/kpgs-vnext/security-playground-core/Cargo.toml -- --check
cargo test --locked --manifest-path governance/kpgs-vnext/security-playground-core/Cargo.toml
cargo clippy --locked --manifest-path governance/kpgs-vnext/security-playground-core/Cargo.toml --all-targets -- -D warnings
python3 governance/kpgs-vnext/security-playground-core/tests/inventory_parity.py \
  --core governance/kpgs-vnext/security-playground-core/target/debug/spp-core
python3 -m unittest discover -s tests -p 'test_security_playground*.py' -v
python3 -m unittest discover -s tests -p 'test_swfus_progressive_updates.py' -v
```

The inventory replay sends the same bytes to both CLIs and compares their
exit codes, verdicts, reasons and authority flags. Rust deliberately holds
fixture claims with real or unnamed references and rejects duplicate JSON
keys, inputs over 64 KiB and more than 256 asset records. Malformed input
uses `INVALID_INPUT` in Rust. Python retains its existing behavior. The
separate `gsmb_security_playground_v1` Python schema still needs a Rust port.
Cryptographic receipt verification, runtime isolation and a runner remain
**PROPOSED / NOT_RUN**. The Progressive Updates suite exercises its existing
stage contract. This crate is outside that engine's state-update path.

Current workspace rerun (2026-11-09): all 42 Python Security Playground,
13 Progressive Updates and 4 Zero Trust workflow-policy tests passed. Six
Rust/Python inventory parity cases passed using the prebuilt Rust candidate
binary; its three Rust source files were hash-compared with this checkout.
`cargo` and `rustup` are unavailable in the current workspace, so a fresh Rust
compile, `cargo test`, `fmt`, and `clippy` rerun is not claimed here. The
fixture workflow is prepared to run these checks on the review branch.

## Progressive upgrade procedure

Use the existing `governance/kpgs-vnext/progressive-updates/README.md` ordering;
do not create a second update protocol. Each Rust-core upgrade must preserve
the stage order and emit a reviewable receipt for every reached or skipped
stage:

1. **Telemetry:** pin source SHA, toolchain, lockfile, advisory policy version,
   case-corpus digest and update/idempotency identity.
2. **Classification:** label the change as fixture evaluator, compatibility
   adapter, or runtime runner. This crate is only the first category.
3. **Routing:** keep Local, Cloud, Drive, production, preview, build/CI and
   tooling evidence separate; route any missing or conflicting evidence to
   `HOLD`.
4. **Protocol selection:** use the existing SPP, Black Mask/Bracket, PKA and
   capability-lease contracts for their existing lanes. No adapter inherits
   execution authority from this crate.
5. **Invariant audit:** confirm bounded parsing, schema-specific field handling,
   deterministic classification, no privileged I/O, no production paths and
   `runtime_verified=false` in every output.
6. **POC / FOC check:** follow current Cloud terminology, where FOC means
   **Field of Concepts**. A Drive report's historical “Full Operational
   Capability” wording remains attributed to Drive and is not a current
   Cloud definition or runtime receipt. `GREEN` is not POC evidence by itself;
   `YELLOW` holds; `RED` rejects before mutation.
7. **State update:** update only this non-authoritative source candidate after
   tests pass. This crate does not mutate Security Playground policy or estate
   state.
8. **Distribution:** this user-directed work is staged as a draft review
   candidate for hosted fixture validation. It does not authorize merge,
   rollout, deployment or authority change. Any later release needs its own
   task-specific scope and receipts. Rollback restores the prior evaluator and
   policy revision, retains the failed receipt, and re-runs both the Rust
   fixtures and Python reference tests before further distribution.

Promotion order is fixture comparison → shadow comparison on the same corpus →
reviewed caller migration → non-production canary only after independent
containment evidence → separately authorized operational use. The current SPP
contract says runtime isolation is unverified. No production activation is
available from this crate.

## Existing systems to connect in later bounded updates

This is a discovery map, not an integration claim. The listed systems remain
separate until an adapter is implemented and tested against their current
contracts.

| Existing system | Existing contract to reuse | Core status |
|---|---|---|
| Black Mask / Bracket | `docs/swarm-ops/BLACK_MASK_COMMANDMENTS.json`, `BRACKET_PROTOCOL.md` | Scenario and containment references only; no runner. |
| PKA / POCvsFOC | `skills/pka/`, `poc-vs-foc/` | Not integrated; preserve `MAYBE` and the existing admission boundary. The Rust evaluator emits no POC/FOC tag, creates no FOC group, and classifies no actor. |
| Zero Trust / capability leases | `governance/kpgs-vnext/security/CAPABILITY_LEASE.md` | Not integrated; no grant or lease is consumed. |
| Oz lattice | `docs/swarm-ops/OZ_CONTEXT_BLEED_PROTOCOL.md` | Not integrated; no cross-domain edge is created. |
| RUNE / consignment | Existing RUNE repository receipts and current verifier tests | Not integrated; verifier/role findings remain a prerequisite. |
| Browser MCP approvals | Existing approval and receipt-ledger contracts | Not integrated; no browser action is exposed. |
| KMEC / evidence logs | Existing receipt and alert contracts | Not integrated; no external alert delivery is claimed. |
| APU / Progressive Updates / SWFUS | `governance/kpgs-vnext/progressive-updates/` | Used only as the future upgrade sequence; this crate does not distribute. |
| Procurement replay #342 | `RobynAwesome/Introduction-to-MCP#342` | Existing fixture lane remains separately owned; not implemented here. |
| Dependency and deployment gates | Existing workflows and exact artifact receipts | Fixture workflow candidate runs both evaluators. No artifact or deployment gate integration. |

Local GSMB was unavailable at implementation time. The Cloud repo and Drive
document remain separate evidence populations; no parity or synchronization is
claimed.

The current Cloud `AGENTS.md` uses FOC to mean **Field of Concepts**. The
`FOC-G01` to `FOC-G08` failure-pattern identifiers remain scoped to their
existing classification index. The September 30 POC/FOC issue-classification
document is marked **PROPOSED / NOT ADMITTED**; this candidate does not use it
to change terminology or create a new classification.
