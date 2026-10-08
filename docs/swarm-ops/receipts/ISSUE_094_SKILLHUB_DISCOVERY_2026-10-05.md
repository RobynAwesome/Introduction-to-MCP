## Owner-disposition and live-source revalidation — 2026-10-06T22:14:50Z

Robyn merged [PR #257](https://github.com/RobynAwesome/Introduction-to-MCP/pull/257) at `2026-10-06T22:08:01Z` as `cf6cdaa5769465f7c2f7b4c5797e60b7122e7ac9`. After a fresh read-only SkillHub query at `2026-10-06T22:07:50Z`, issue #94 was closed as `COMPLETED`; [the closeout comment](https://github.com/RobynAwesome/Introduction-to-MCP/issues/94#issuecomment-6026432635) records the Four Ws, live listing count, source versions, hash boundaries, and exclusions.

The completion boundary is the issue's **registry discovery** objective. The current SkillHub owner search returned four entries: three Introduction-to-MCP entries and one Project-Jennifer entry. The PKA-related listing is case material, not the standalone private root skill. The Project Jennifer provider entry remains version `1.0.0` / content SHA `8dbc8ae6bc212063b8401b595a1daf9efb180408f58352f34ed465b4bf163820`; the observed current source remains at `cc74b56b879881defbbb885167b1b75a4a26f6db`, version `1.2.0` / SHA `a4df61972bd1913f32a59d8a744f4481b3786180b3ad3e884edf27cd2dfe3903`. This is a listing-freshness gap, not a reason to expand the closed discovery issue into catalog publication.

This owner disposition supersedes the earlier instruction below to keep #94 open pending PR landing and owner acceptance. Follow-up publication, freshness, or full-catalog work needs its own bounded scope. No registry or source was mutated.

`I_AM_STATELESS_RENTER_NOT_LANDLORD`

---
# Issue #94 — SkillHub registry discovery receipt

**Actor:** Forge / Codex CA, stateless renter; bounded investigation delegated to `issue_triage`. `I_AM_STATELESS_RENTER_NOT_LANDLORD`.

**Question:** Is there a live external skill registry beyond AwesomeSkills with PKA-related and Project Jennifer material, and can the listings be bound to source provenance?

**Observation time:** 2026-10-05T11:30:35Z for the read-only registry and GitHub source checks reported by the delegated investigator. Cloud repository baseline: `master@a2d0b8fcca1a3340b31b9570797223e9a97e3464`.

## Provider evidence

The SkillHub owner search returned four `RobynAwesome` listings: three under `Introduction-to-MCP` and one under `Project-Jennifer`. Each relevant listing has a provider detail record and item page.

### PKA-based case skill

- Provider ID: `RobynAwesome/Introduction-to-MCP/pka-bapedi-cultural-game-hub`.
- Provider path: `skills/pka/bapedi-cultural-game-hub`; branch `master`; no version declared in its source frontmatter; MIT; `securityStatus=pass`; `isVerified=false`.
- Provider `rawContent` SHA-256: `019c7ed1c78ff9e625b737b5ace73465ca3d719735f0d4cc377534e2e3b72639`.
- The digest matches the source file in the current Cloud `master` tree and its source-add commit `96c3451ab9159435e17dfab4fbc8ed3d66af8c4d` (blob `5de8c5e9166e56e5db380c38f117a6900a562d06`).
- The skill describes a Bapedi Cultural Game Hub case and names `RobynAwesome/Partial-Knowable-Algebra` as the canonical protocol source. It is **PKA-based case material**, not the standalone canonical PKA root skill.
- The canonical PKA repository is private at `main@0abc68810ee5799f4bb703f8bb99fb2bf11b3e86`; its root `SKILL.md` is named `partial-knowable-algebra` and has no version field. The two queried standalone PKA provider IDs returned 404, so there is no standalone PKA SkillHub listing receipt in this observation.

### Project Jennifer listing

- Provider ID: `RobynAwesome/Project-Jennifer/jennifer-runtime-memory`.
- Provider path: `skills/jennifer-runtime-memory`; provider version `1.0.0`; branch `main`; MIT; `securityStatus=pass`; `isVerified=false`; `isStale=false` in the provider record.
- Provider `rawContent` SHA-256: `8dbc8ae6bc212063b8401b595a1daf9efb180408f58352f34ed465b4bf163820`. It matches the skill source at historical Project-Jennifer commit `f1ec4b27c5c238cb53125ff0aad8e857ea6c45a3` (blob `736272a22d23b834e3296a527000bea4bc034c58`).
- Current Project-Jennifer `main` was `cc74b56b879881defbbb885167b1b75a4a26f6db`; its current skill frontmatter is `1.2.0`, with SHA-256 `a4df61972bd1913f32a59d8a744f4481b3786180b3ad3e884edf27cd2dfe3903` (blob `8128948b8a17f5b1041a9734b6ff9acb05d4b534`). Thus the listing is present but the content is behind current source. This is one runtime-memory skill, not the full Project Jennifer catalog.
- `securityStatus=pass` is a provider scan result; `isVerified=false` remains the provider verification state. Neither proves publisher identity or a complete/current catalog.

## Finding and disposition

**Discovery criterion met, with a bounded result:** SkillHub is a live additional registry, and it exposes one PKA-based case skill plus one Project Jennifer runtime-memory listing with provider-level provenance. The owner-search result, detail records, item pages, and matching source hashes distinguish actual listings from keyword-only discovery.

Do not claim that SkillHub contains the standalone PKA skill, the full Project Jennifer catalog, current Jennifer source content, a publisher-account claim, or a fully verified publisher identity. The absence of the standalone PKA listing is limited to the inspected SkillHub provider responses; it says nothing about other registries.

This receipt supports completing issue #94's stated registry-discovery objective. Keep the GitHub issue open until this receipt lands through its protected PR and Robyn accepts it; then close #94 with the exact bounded finding. Any later request to publish the private PKA root, refresh the Jennifer listing, claim a provider account, or audit the full catalogs should be scoped as separate work rather than silently expanding this discovery issue.

No registry content, provider account, GitHub issue state, source repository, or external listing was mutated.

## Direct source links

- [SkillHub owner search](https://skills.palebluedot.live/api/skills?q=RobynAwesome&limit=100)
- [SkillHub PKA-based case skill item](https://skills.palebluedot.live/skill/RobynAwesome/Introduction-to-MCP/pka-bapedi-cultural-game-hub)
- [SkillHub PKA-based case skill provider record](https://skills.palebluedot.live/api/skills/RobynAwesome%2FIntroduction-to-MCP%2Fpka-bapedi-cultural-game-hub)
- [SkillHub Project Jennifer item](https://skills.palebluedot.live/skill/RobynAwesome/Project-Jennifer/jennifer-runtime-memory)
- [SkillHub Project Jennifer provider record](https://skills.palebluedot.live/api/skills/RobynAwesome%2FProject-Jennifer%2Fjennifer-runtime-memory)
- [Project Jennifer historical source commit](https://github.com/RobynAwesome/Project-Jennifer/commit/f1ec4b27c5c238cb53125ff0aad8e857ea6c45a3)
- [Project Jennifer current source commit observed](https://github.com/RobynAwesome/Project-Jennifer/commit/cc74b56b879881defbbb885167b1b75a4a26f6db)
- [Introduction-to-MCP PKA case skill source commit](https://github.com/RobynAwesome/Introduction-to-MCP/commit/96c3451ab9159435e17dfab4fbc8ed3d66af8c4d)

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
