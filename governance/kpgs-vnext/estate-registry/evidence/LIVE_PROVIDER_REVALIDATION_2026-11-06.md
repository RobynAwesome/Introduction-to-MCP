# Issue #102 live provider revalidation — 2026-11-06 SAST

Fox Forge / Codex, stateless evidence reviewer under Robyn's oldest-first instruction. `I_AM_STATELESS_RENTER_NOT_LANDLORD`.

Observed Cloud `master@2ba850e458b93e9fe4b5c78cda8f00363f6e6836`, connected Vercel domain and deployment records, exact GitHub source commits, public GET responses and deployment-scoped logs. KasiLink route errors were recorded at 11:21 SAST. Local GSMB was outside this read.

| Host | Verified Vercel project | Serving deployment | Source commit | Root GET |
| --- | --- | --- | --- | --- |
| `starfallsalvage.kopanolabs.com` | `starfall-salvage` / `prj_rik2lQSlmHm7CIUhEGZMprZ5CFcN` | `dpl_d3pwryLL8Ra2DAWCdw9ScWNL5GWe` / READY | [`763380b01819`](https://github.com/RobynAwesome/starfall-salvage/commit/763380b01819a4b38c6fe048a33333fbc7c8d208) | 200 |
| `kasilink.com` | `kasi-link.rsa` / `prj_07Q4oRr2okeBiPO12YotAzHZM10b` | `dpl_AqG9ZsnQDgj3XP1rjkDKWf9wNGQi` / READY | [`13be1ba8df4a`](https://github.com/RobynAwesome/KasiLink/commit/13be1ba8df4a086394d998815d57c1c885f1ec2b) | 200 |
| `www.kasilink.com` | `kasi-link` / `prj_A1AvVl5WYRyTergoEcMsvEmMM3uX` | `dpl_G5E4CUipKezy11RXttg79ua9P1nD` / READY | [`13be1ba8df4a`](https://github.com/RobynAwesome/KasiLink/commit/13be1ba8df4a086394d998815d57c1c885f1ec2b) | 200 |

Vercel reported each domain as verified on the listed project, and each deployment response listed the domain as an alias. Both KasiLink projects serve the same source commit and remain separate deployments. These are current provider witnesses. The [August witness](LIVE_PROVIDER_WITNESS_2026-08-24.md) and canonical registry retain their dated provenance and admission status.

## KasiLink data routes

| GET route | Apex | www |
| --- | --- | --- |
| `/api/incidents` | 500 | 500 |
| `/api/water-alerts` | 500 | 500 |
| `/api/gigs` | 500 | 500 |

All six matching function errors show `querySrv ENOTFOUND` for the same MongoDB SRV hostname. The hostname and connection settings are omitted. The current failure is at DNS resolution. The earlier authentication error remains historical evidence, and current credential validity is unknown because the sampled requests failed before reaching authentication. Logs identify the runtime family as `nodejs24.x`. The exact Node binary patch was not measured.

**KasiLink cutover remains HOLD.** The KasiLink/Vercel/Atlas configuration owner should compare the configured production hostname with the current Atlas cluster, verify the SRV record from the serving environment, then repair the production configuration through the authorized provider path. Validate all three data routes and fresh logs on the chosen deployment before proposing domain convergence. [Owning runtime issue #15](https://github.com/RobynAwesome/KasiLink/issues/15)

## Starfall rollback and admission

The historical rollback target `dpl_9X3gbZpWuRWK5N3XC7Unvtd1doDR` still resolves as READY on the Starfall project at source `b3253e44a7e129d5d2f323d579666f6e5182fd94`. The filtered candidate listing was unavailable, so current eligibility for provider rollback is unverified. Rollback execution and adapter, renter, capability, policy and exact-release evaluation evidence remain HOLD. [Existing rollback procedure](LIVE_PROVIDER_WITNESS_2026-08-24.md#starfall-rollback-procedure)

[Issue #102](https://github.com/RobynAwesome/Introduction-to-MCP/issues/102) remains open. This dated witness records current serving identity and bounded HTTP/log behavior. No provider, credential, DNS or admission state was changed.
