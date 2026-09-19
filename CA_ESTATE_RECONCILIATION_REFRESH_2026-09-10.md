# Estate reconciliation refresh — 2026-09-10

> Observation time: `2026-09-10T07:30:16+02:00` (SAST) / `2026-09-10T05:30:16Z`.
> This refresh supersedes the August 29 `de019c650`-era snapshot as current-state evidence while preserving that snapshot as historical provenance.

## Current cloud lineage

| Surface | Confirmed observation |
|---|---|
| Canonical remote | `https://github.com/RobynAwesome/Introduction-to-MCP.git` `master` = `40a31fe8eb54d9943f79ea9b546a89fffc553a2b` |
| Mirror remote | `https://github.com/Kopano-Labs/Introduction-to-MCP.git` `master` = `40a31fe8eb54d9943f79ea9b546a89fffc553a2b` |
| PR #118 | merged at `01ec0c5c48ed804d928286407d4e3631a9c60eff`; source PR head included CodeQL follow-up `4a2514f88809054788f2be648e099ad5904c6d94`; v0.2 source hardening commit was `6c2f3bab2755859f07714dd3bd4be074473aa235` |
| September 5 Apache-2.0/provenance/CI chain | `c34a9fecf524379cc1db97d20e2aee09cdeb69d3` through `c98dc2351f185389ced6512a04b1d32e34c4ea94` |
| Later current-master lineage | PR #123 merge `75ef539301f1e118e935adee0047d0e87ed631bc`; PR #124 merge `5ef3a5428105c541f38a984d5da1068c257318c0`; PR #156 merge `8f1dda5b0aef87c1886fda3cd8b0e25af6742e5c`; PR #157 merge `40a31fe8eb54d9943f79ea9b546a89fffc553a2b` |

`de019c650e7ad5eed2d8c2a84b0e3d13274d55e4` is historical and is not the current cloud baseline.

## Checkout identities

| Checkout | State at observation | Authority |
|---|---|---|
| OneDrive preservation checkout | `codex/kc-sovereign-gui-full-dev` @ `f7ed0e308cb499c89dc4ea399f188697b1406f92`; dirty with pre-existing tracked/untracked material | preservation only; no pull, reset, merge, or bulk promotion performed |
| canonical integration branch ref | `codex/gsmb-canonical-integration-2026-09-05` @ `07cf68951e9c251c5df9c7160e057c1fc61f5615`; prior clean committed integration snapshot | comparison evidence, not current cloud state |
| canonical receipt checkout | `governance/kpgs-browser-mcp-metal-receipt` @ `152357270ce83575cd8de5c34961625713d79e47`; 2 commits ahead and 10 behind current `origin/master`; dirty `NOW.md` plus generated `dotnet/obj` paths | not clean; no claim of publication |
| isolated current-master worktree | detached @ `40a31fe8…`; clean validation surface | used for browser package install/build/tests and Windows-metal run |

## Windows-metal KPGS Browser MCP v0.2

- `npm ci` is **BLOCKED** in current cloud `master` because `tools/kpgs-browser-mcp/package-lock.json` is not tracked. No lockfile was generated or promoted from the dirty preservation checkout.
- Exact-version fallback `npm install --package-lock=false` passed with `0` reported vulnerabilities; `npm run test` built TypeScript and passed `16/16` governance/ledger tests.
- Dedicated Microsoft Edge `153.0.4234.19` ran through loopback CDP at `http://127.0.0.1:9223` using a dedicated profile. Port `9222` was excluded after it resolved to an unrelated Lenovo Vantage WebView.
- Real MCP stdio discovery passed: initialize, `tools/list`, and the seven expected tools were observed; no `approve` MCP tool exists.
- Stable target read/navigation passed: Edge target `83429D8C5E44B21570B747F68FAF63E4` remained stable from `about:blank` through policy-admitted loopback navigation (`HTTP 200`) and `read_page`; web text was labelled untrusted.
- No-side-effect staging passed: a benign type action returned only character count and SHA-256 digest; execution without approval returned `DENIED / HUMAN_APPROVAL_REQUIRED_OR_ALREADY_CLAIMED`.
- Non-TTY approval denial passed: the local approval CLI rejected approval with `DENIED: approval requires an interactive local terminal (TTY)`.
- A real TTY approval is currently waiting for the human gate on the staged `#driftTarget` action. Element-drift denial, one approved low-risk execution, replay denial, successful scrub, and receipt verification remain pending until that human input is supplied.

## Remaining limits

1. No production deployment, cloud MCP client, external provider, authenticated website, or non-loopback target was used or validated.
2. Live indeterminate/quarantine was not induced; the isolated source suite’s quarantine/no-replay test passed, but this refresh does not promote that unit result to live-metal evidence.
3. The missing browser-package lockfile remains a reproducibility blocker for `npm ci` and must be resolved in an explicitly authorized code change before claiming pinned install parity.
4. Dirty preservation and canonical receipt worktrees were not cleaned, reset, merged, or deployed.
