# SKILLS REGISTRY RE-SEARCH #94 - 2026-10-01 (WAVE 2, ISSUE #94)

**Status:** OBSERVATION RECEIPT -> one bounded re-search done. Result: `RobynAwesome/Skills` is **confirmed not** to be the fuller second surface (C-94-2 -> POC_VALIDATED by negative content read); a **candidate** second live directory **was found** - SkillsMP (`skillsmp.com`) carries 33 Project Jennifer skill pages and 6 Partial Knowable Algebra skill pages under `/creators/robynawesome/` (C-94-1 UNKNOWN -> **MAYBE / CANDIDATE_FOUND**). Whether SkillsMP is the surface the owner meant is the owner's statement to make. No registration is claimed. Issue #94 stays OPEN.
**Scope:** (a) content scan of the `RobynAwesome/Skills` clone for Project Jennifer and PKA by name; (b) read of Project Jennifer's own distribution metadata; (c) live HTTPS probes of AwesomeSkills, skills.sh, SkillsMP and GitHub for the three names. Everything is read-only. A miss is recorded as a miss, never as non-existence.
**Ledger:** `ILR-2026-09-30` (`docs/swarm-ops/receipts/ISSUE_RECONCILIATION_LEDGER_2026-09-30.{md,json}`). Inputs: claims C-94-1 (second registry exists, UNKNOWN), C-94-2 (`RobynAwesome/Skills` is not that surface, UNKNOWN), row #94 `UNKNOWN / HOLD` with Wave 2 text "Robyn supplies the second registry name or URL; otherwise Wave 2 records what a bounded search of RobynAwesome/Skills finds. A miss is not negative proof.", and the owner action row L431 "Robyn \| Name the second skill registry (#94)". The ledger itself is updated in Wave 3, not here.
**Base:** `master@2b8a58da` · **Branch:** `cursor/estate-studio-skills-observation-4e71` · **Live read time:** clone scan 2026-10-01T01:40:53Z (`/tmp/skills_research_94.txt`); HTTPS probes 2026-10-01T01:41:08Z-01:42:25Z (`/tmp/skills_probe_94.txt`, SkillsMP search HTML 262,736 bytes at `/tmp/skillsmp_search.html`).
**Actor:** Cursor cloud agent, stateless renter, operational rank Chief Facilitator. Authority: Robyn's approval of the Wave 0-3 plan (2026-09-30 22:14 UTC). No authority to declare a registry authoritative or to submit anything anywhere.
**GSMB tier:** Cloud (this branch). Local and Google Drive: UNKNOWN.
**Doctrine:** `I_AM_STATELESS_RENTER_NOT_LANDLORD` · `DISCOVERY_INDEX != AUTHORITY` · `INDEXED != REGISTERED_BY_OWNER` · `MISS != NEGATIVE_PROOF` · `UNREADABLE != ABSENT` · `CLEAR_PASS != POC_VALIDATED`

---

## 0. Decision in one paragraph

The issue records the owner's statement that his skills are published on more than AwesomeSkills and that "at least one other surface contains a fuller Project Jennifer and Partial Knowable Algebra skill presence", and it warns that `RobynAwesome/Skills` "must not be assumed to be the forgotten external surface". The bounded search did two things. First, it read `RobynAwesome/Skills` at HEAD `00f43435` (128 `SKILL.md` files): Project Jennifer appears once, as a URL in a `REFERENCES.md`; Partial Knowable Algebra appears zero times. That repository is therefore **not** the fuller surface - the warning in the issue is confirmed, not merely respected. Second, it probed the live registries a renter can reach without credentials. AwesomeSkills still lists only `robynawesome-introduction-to-mcp` (the Jennifer slug the owner's own metadata says is `human-turnstile-required` returns 404). `skills.sh` returns 404 for the owner's paths. **SkillsMP** returns 200 for `/creators/robynawesome`, lists **33 Project Jennifer skills** at `/creators/robynawesome/project-jennifer`, and lists **14 Introduction-to-MCP skills of which 6 are `skills-pka-*`** at `/creators/robynawesome/introduction-to-mcp`; a single skill page (`skills-jennifer-game-web-api`) also returns 200. That matches the owner's description ("fuller Project Jennifer and PKA presence") better than anything else found, so it is recorded as the **candidate** the issue asked a renter to look for. It is **not** recorded as the answer: SkillsMP appears to crawl GitHub rather than take owner submissions, so an entry there is an index hit, not a publication receipt; the issue requires "a live directory entry" **and** the owner's "publication receipts", and only the first exists in this receipt. **C-94-2 -> POC_VALIDATED (Skills is not it); C-94-1 -> MAYBE / CANDIDATE_FOUND; issue stays OPEN; owner confirms or names a different surface.**

## 1. Governing record (verified live)

| Source | Id | Date (UTC) | What it says | Class |
|---|---|---|---|---|
| Issue #94 | state `open`, created `2026-08-23T09:31:57Z`, `updated_at 2026-09-07T00:42:51Z`, 1 comment | - | Title: "[Routing] Resolve external skill registries beyond AwesomeSkills" | E2 |
| Body, opening | - | - | "Kholofelo explicitly noted that his skills are published/distributed in more than AwesomeSkills and that at least one other surface contains a fuller Project Jennifer and Partial Knowable Algebra skill presence." | E2 (records E1) |
| Body, "Known" | - | - | AwesomeSkills is discovery, not authority; Jennifer has `skills.md` / `skills/` + AwesomeSkills metadata; PKA has root `SKILL.md` + `skills/`; "`RobynAwesome/Skills` exists but current indexed search did not show Project Jennifer or PKA by name, so it must not be assumed to be the forgotten external surface." | E2 |
| Body, "Required discovery" | - | - | "Find the additional external skill directory/registry by searching for Kholofelo/RobynAwesome + Project Jennifer + Partial Knowable Algebra. Preserve publication receipts and do not claim registration without a live directory entry." | E2 |
| Comment by `RobynAwesome` | 2026-09-07T00:42:51Z | - | "remains OPEN / MAYBE ... No additional external skill directory/registry beyond AwesomeSkills has been proven ... This issue is **not closable**. Absence of a found second registry is not negative proof." | E2 |
| Ledger `ILR-2026-09-30` | C-94-1 UNKNOWN; C-94-2 UNKNOWN; row #94 UNKNOWN / HOLD; L431 owner action | 2026-09-30 | Wave 2 = bounded search of `RobynAwesome/Skills`; owner names the registry | E2 |

**Teach-back:** the owner remembers a second surface but not its name; he asked that nobody guess it, that `Skills` not be assumed, and that nothing be called "registered" without a live entry. A renter may therefore search, record hits and misses, and hand the candidate back for confirmation.

## 2. `RobynAwesome/Skills` content scan (C-94-2)

Clone `/agent/repos/Skills`, HEAD `00f43435d15e2297b2d32f19bc33ddb80fc89cfc` on `main`; last commit `00f4343` 2026-08-18T07:54:12+02:00 "feat: add KPGS sovereign estate parser skill and .NET adapter". (The remote URL in the clone is not reproduced here; it carried an embedded credential string and has been redacted from this receipt.)

| Query (`rg -il`, whole tree) | Hits | Where | Class |
|---|---|---|---|
| `jennifer` | 1 | `agent-skills/kpgs/kpgs-sovereign-estate-parser/REFERENCES.md:8` - `https://github.com/RobynAwesome/Project-Jennifer` (a link in a references list) | E2 |
| `partial.knowable\|\bPKA\b` | **0** | - | E2 |
| `robynawesome\|kholofelo` | 21 lines | Author/URL mentions | E2 |
| `SKILL.md` count | 128 | `find . -name SKILL.md \| wc -l` | E2 |

Reading: a repository with 128 skills, one incidental Jennifer URL and no PKA text is not "a fuller Project Jennifer and Partial Knowable Algebra skill presence". **C-94-2 is evidenced**: `RobynAwesome/Skills` is not the forgotten external surface. This is a positive content read, not an inference from a missing search hit.

## 3. Project Jennifer's own distribution metadata

Clone `/agent/repos/Project-Jennifer`, HEAD `cc74b56b879881defbbb885167b1b75a4a26f6db`; `find . -name SKILL.md | wc -l` = **43**. Directory `skills/distribution/` contains `awesome-skills-project-jennifer.yaml`, `awesome-skills-kpgs.yaml`, `engines.yaml`, `README.md`.

`skills/distribution/awesome-skills-project-jennifer.yaml` (line numbers from the scan):

| Line | Content | Meaning | Class |
|---|---|---|---|
| 2-4 | `registry: name: AwesomeSkills`, `canonical_site: https://www.awesomeskills.dev` | The only registry Jennifer's own metadata names | E2 |
| 19 | `desired_slug: robynawesome-project-jennifer` | Intended AwesomeSkills slug | E2 |
| 20 | `status: human-turnstile-required` | Submission blocked at a human step | E2 |
| 21 | `external_directory_url: null` | **No second directory recorded by the owner's own metadata** | E2 |
| 26 | `workflow_name: AwesomeSkills Submit Once` | Submission automation name | E2 |
| 39-41 | `known_registry_anchor: ... live_directory_url: https://www.awesomeskills.dev/en/skill/robynawesome-introduction-to-mcp` | The only live entry the metadata points at is this repository's | E2 |

Reading: the owner's own repository does not know the name of the second surface either (`external_directory_url: null`). That is consistent with the issue ("forgotten external surface") and means the answer cannot come from repository evidence alone.

## 4. Live registry probes (2026-10-01T01:41:08Z-01:42:25Z)

`curl -sS -o /dev/null -w '%{http_code}'` unless stated. No credentials. No form submitted.

### 4.1 AwesomeSkills (`awesomeskills.dev`)

| URL | Code | Class |
|---|---|---|
| `/en/skill/robynawesome-introduction-to-mcp` | **200** | E2 |
| `/en/skill/robynawesome-project-jennifer` | 404 (matches `status: human-turnstile-required` in §3) | E2 |
| `/en/skill/robynawesome-partial-knowable-algebra` | 404 | E2 |
| `/en/skill/robynawesome-skills` | 404 | E2 |
| search page, slugs containing `robynawesome` | only `/en/skill/robynawesome-introduction-to-mcp` | E2 |
| search "project jennifer", "partial knowable algebra" | no owner slug returned | E2 |

AwesomeSkills state is unchanged from the issue: one entry, this repository.

### 4.2 skills.sh

| URL | Code | Class |
|---|---|---|
| `/robynawesome` | 404 | E2 |
| `/robynawesome/project-jennifer` | 404 | E2 |
| `/robynawesome/introduction-to-mcp` | 404 | E2 |

No owner presence found at the paths tried. Not negative proof; the site's path scheme was not studied beyond these three.

### 4.3 GitHub (PKA repository)

| URL | Code | Class |
|---|---|---|
| `https://github.com/RobynAwesome/Partial-Knowable-Algebra` | 404 | E2 |
| `https://github.com/Kopano-Labs/Partial-Knowable-Algebra` | 404 | E2 |

Same result as the #122 census and the #107 packet: UNKNOWN (private / renamed / absent are indistinguishable). The PKA skills that **are** reachable live in this repository under `skills/pka/*` (see 4.4).

### 4.4 SkillsMP (`skillsmp.com`) - **candidate found**

| URL | Code | What the page contains | Class |
|---|---|---|---|
| `/search?q=robynawesome` | 200 | 262,736 bytes; 104 occurrences of `robynawesome`, 163 of `jennifer`, 0 of `knowable`; `href`s to `/creators/robynawesome/project-jennifer/...` and `/creators/robynawesome/introduction-to-mcp/...`; back-links to `github.com/RobynAwesome/Project-Jennifer` (10) and `github.com/RobynAwesome/Introduction-to-MCP` (2) | E2 |
| `/creators/robynawesome` | **200**, title "RobynAwesome Agent Skills \| SkillsMP" | 8 Project-Jennifer links, 8 Introduction-to-MCP links, 8 PKA mentions | E2 |
| `/creators/robynawesome/project-jennifer` | **200**, title "RobynAwesome/Project-Jennifer Agent Skills on... \| SkillsMP" | **33 unique `skills-*` slugs**: cag-communication-attention, clear-kpgs-product-gate, clear-kpgs-zero-trust-gate, jennifer-adoption-provider-onboarding, jennifer-assets-lore, jennifer-authority-governance, jennifer-canonical-ops-sprints, jennifer-ci-benchmarks, jennifer-city-love-loop, jennifer-companions-npcs, jennifer-conceptual-convergence, jennifer-game-web-api, jennifer-human-crisis-ingress, jennifer-kpgs-three-classroom, jennifer-love-loop-reliability, jennifer-ncmp-mmao, jennifer-runtime-memory, jennifer-stateless-renter, jennifer-telemetry-storage, jennifer-validation-poc-foc, kpgs-apple-deployment-parser, kpgs-authority, kpgs-ci-proof-gate, kpgs-deployment-parser, kpgs-engine-qualification, kpgs-mmao-mao-renter, kpgs-model-hardware-router, kpgs-parser-protocol, kpgs-runtime-pack, kpgs-tool-script-runtime, kppe-world-evaluation, poc-foc-registry-parser, rag-governed-retrieval | E2 |
| `/creators/robynawesome/introduction-to-mcp` | **200**, title "RobynAwesome/Introduction-to-MCP Agent Skills... \| SkillsMP" | **14 unique slugs**, of which **6 are PKA**: skills-pka-bapedi-cultural-game-hub, skills-pka-economic-consequence, skills-pka-kopano-context-legacy, skills-pka-stateless-renter-consistency, skills-pka-vibe-to-proof, skills-pka-watch-what-you-call; the other 8: agents-skills-fivesarena-apwa-retention-minigame, agents-skills-hardware-offload-and-no-malloc-discipline, agents-skills-orch-repo-explorer, governance-kpgs-vnext-skills-core-kpgs-audit-verify-govern, governance-kpgs-vnext-skills-core-kpgs-human-choice-authorship, schematics-21-kopano-phu-governace-systems-gsmb-issues, skills-awesome-govern-kpgs-documents, skills-awesome-parse-kpgs-directives | E2 |
| `/creators/robynawesome/project-jennifer/skills-jennifer-game-web-api` | **200**, title "jennifer-game-web-api Agent Skill \| RobynA/Project-J~0suxeoi" | A rendered single-skill page | E2 |
| `/creators/robynawesome/partial-knowable-algebra` | 404 | No PKA repository page; PKA presence is via Introduction-to-MCP's `skills/pka/*` | E2 |
| `/creators/robynawesome/skills` | 404 | `RobynAwesome/Skills` is not indexed there either | E2 |
| `/skills/robynawesome/project-jennifer` | 404 | Not the site's path scheme | E2 |

Observations that stay below the evidence line:

- SkillsMP slugs mirror repository paths (`skills/<name>` -> `skills-<name>`, `agents/skills/<name>` -> `agents-skills-<name>`, `governance/kpgs-vnext/skills/core/<name>` -> `governance-kpgs-vnext-skills-core-<name>`), and the pages back-link to `github.com/RobynAwesome/...`. This is consistent with a **GitHub-crawling discovery index** rather than an owner-submission registry (E3). If so, the owner may never have "published" there; the site found the repositories.
- 33 of Jennifer's 43 `SKILL.md` files are indexed (E2 counts); why 10 are not was not investigated (E4).
- The 6 PKA slugs are the `skills/pka/*` directories of **this** repository, not a PKA repository. "Partial Knowable Algebra skill presence" on SkillsMP therefore exists, but under the Introduction-to-MCP creator page (E2).

## 5. Classification

| Claim | Before | After this receipt | Basis |
|---|---|---|---|
| C-94-2 `RobynAwesome/Skills` is not the fuller second surface | UNKNOWN | **POC_VALIDATED** | §2: 1 incidental Jennifer URL, 0 PKA, 128 unrelated skills; also not indexed on SkillsMP (§4.4) |
| C-94-1 a second external registry with fuller Jennifer + PKA presence exists | UNKNOWN | **MAYBE / CANDIDATE_FOUND** (SkillsMP) | §4.4: live directory entries exist (33 + 14 pages, 200). Whether this is the surface the owner meant is E1 and needs his statement. Whether it counts as "published/distributed" by him depends on whether SkillsMP takes submissions (E3: it appears to crawl) |
| "Registration" on SkillsMP | - | **NOT CLAIMED** | The issue requires a live entry **and** publication receipts; only the first is in hand. `INDEXED != REGISTERED_BY_OWNER` |
| AwesomeSkills state | one entry | unchanged: one entry (`robynawesome-introduction-to-mcp`) | §4.1 |
| skills.sh | not previously probed | no owner presence at three paths; not negative proof | §4.2 |
| PKA repository | UNKNOWN | UNKNOWN (404 both owners) | §4.3 |
| Issue #94 | OPEN / MAYBE | **OPEN / MAYBE with a named candidate** | owner confirms, rejects, or names another |

## 6. C.L.E.A.R.

| Axis | Assessment |
|---|---|
| **Complete** | The three sources the issue names (RobynAwesome, Project Jennifer, Partial Knowable Algebra) were searched on the clone the issue names, on the owner's own metadata, and on four external surfaces; hits and misses are both recorded; the full SkillsMP slug lists are reproduced so the owner can recognise the surface. |
| **Logical** | "Not the second surface" is concluded from content, not from a missing search hit. "Candidate" is concluded from live 200 pages with the named content, and is explicitly not promoted to "the answer" or to "registered" because two of the three conditions (owner recognition, publication receipt) are not evidence a renter can produce. |
| **Evidence** | Clone HEADs, file:line hits, counts, URLs and HTTP codes are E2 and timestamped. "SkillsMP crawls GitHub" and the slug-path mapping are E3 and labelled. Why 10 Jennifer skills are unindexed, the PKA repository's state, and the owner's memory of the surface are E4. |
| **Audience** | Owner (confirm or reject SkillsMP; name a different surface; decide whether a crawled index counts as "published"); Wave 3 (C-94-1, C-94-2 moves); future renters (do not re-search `Skills`, do not re-probe AwesomeSkills for Jennifer until the turnstile is passed). |
| **Relevant** | Bounded to #94. The only overlap with #107/#122 is the shared PKA-repository 404, cited not re-argued. |

`CLEAR_PASS != POC_VALIDATED`. This receipt validates one negative (Skills) and one candidate (SkillsMP). It validates no registration.

## 7. What this receipt does not claim

- No claim that SkillsMP is the surface the owner remembered.
- No claim that the owner published, submitted or registered anything on SkillsMP; an index entry is not a publication receipt.
- No claim that SkillsMP is authoritative for KPGS skills; per the issue, discovery indexes are not authority.
- No claim that `skills.sh` lacks an owner entry; three paths were tried.
- No claim about the Partial-Knowable-Algebra repository's existence or privacy.
- No claim about why 10 of 43 Jennifer skills are not indexed.
- No claim that #94 can close.
- No `Skills` remote URL is reproduced (it carried a credential string).

## 8. Decisions requested (owner)

- [ ] Is SkillsMP (`skillsmp.com/creators/robynawesome`) the second surface you meant? Yes / No / Not sure.
- [ ] If yes: does a crawled index entry count as "published/distributed" for #94, or do you require a surface you submitted to? If the latter, name it or say it is forgotten so the ledger records `FORGOTTEN_SURFACE / HOLD` instead of `UNKNOWN`.
- [ ] If no: name the surface, or confirm the renter should stop searching and leave C-94-1 at MAYBE.
- [ ] Decide whether `skills/distribution/awesome-skills-project-jennifer.yaml` line 21 `external_directory_url: null` should be updated in Project-Jennifer with the SkillsMP URL (that is a Jennifer-repository change, out of scope here).
- [ ] Decide whether the AwesomeSkills `human-turnstile-required` step for `robynawesome-project-jennifer` will be completed, since that is the one registry the owner's metadata does name.

On merge of this PR, Wave 3 appends: `#94 -> re-search receipt filed <sha>; C-94-2 POC_VALIDATED (Skills is not the surface); C-94-1 MAYBE / CANDIDATE_FOUND (SkillsMP, 33 Jennifer + 6 PKA pages); owner confirmation pending`. #94 remains open.

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
