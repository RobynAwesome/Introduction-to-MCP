# Issue #158 — Bookit booking-priority conflict

**Observed:** 2026-10-07 00:12 SAST. **Cloud GSMB source:** `RobynAwesome/Introduction-to-MCP@cf6cdaa5769465f7c2f7b4c5797e60b7122e7ac9`. **Target source:** `Kopano-Labs/Bookit-5s-Arena@ae40d1dfbf7abc18508d579703fce1403fd9b999`.

**WHO:** Codex Forge coordinating renter / CA task role; a delegated renter performed a read-only source/issue audit. No RTC identity seat or target-repository write authority is claimed.

**WHAT:** Determine whether any safe code slice can complete Cloud #158 without contradicting target Bookit #42.

**WHERE:** Cloud issue [#158](https://github.com/RobynAwesome/Introduction-to-MCP/issues/158), target issue [#42](https://github.com/Kopano-Labs/Bookit-5s-Arena/issues/42), target draft [PR #33](https://github.com/Kopano-Labs/Bookit-5s-Arena/pull/33) and [PR #43](https://github.com/Kopano-Labs/Bookit-5s-Arena/pull/43). No change was made to either repository, production, Local GSMB, or Drive.

**WHY:** Avoid changing a public booking surface while the current acceptance directions conflict.

## Findings

- Cloud #158 asks to remove booking calls-to-action from the active public root.
- Target Bookit #42 asks to retain booking links in the hero and navigation and pauses decorative Three.js work. Those directions conflict on the active root.
- Target PR #33 is open/draft with merge state `DIRTY`; it includes the disputed root-surface change. PR #43 is open/draft with merge state `UNSTABLE`. Their checks fail; Vercel preview checks passed but are not production evidence.
- The target repository's API context reported `push:true` and `admin:true`; this does not establish that the GitHub App associated with the historical #158 `403` currently has write access. No write was attempted.
- A bounded Drive search found no Bookit/FivesArena document modified after Oct 1 and no result for “FivesArena #42”; the available Sept 21–27 orientation has a Sept 20 evidence cutoff. This limited search is not proof that no later Drive record exists.

## Decision gap and next admissible action

No conflict-independent implementation was identified. The owner needs to choose whether the public root is booking-first or a neutral parked relaunch, whether booking links remain exposed, and whether KPGSTHREE remains paused. After that direction is recorded against #158/#42, re-scope one isolated change from current target `main` with matching acceptance checks. Until then, keep #158 open and make no public-surface, booking-data, deployment, merge, or branch-protection change.

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
