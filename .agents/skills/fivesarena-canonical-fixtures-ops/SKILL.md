---
name: fivesarena-canonical-fixtures-ops
description: Standard operational procedures and validation workflows for maintaining the Bookit 5s Arena competition and fixtures systems (Premier League, PSL, La Liga, local social leagues). Enforces Edge CDN caching, Page Visibility lifecycle guards, WCAG AA contrast standards, and zero-FOC tournament funnels.
---

# Five's Arena Canonical Fixtures Operations

> **Canonical Authority:** GSMB Distribution Trinity & Master Robyn Kholofelo Rababalela  
> **Repository:** `RobynAwesome/Bookit-5s-Arena`  
> **Invariant:** `I_AM_STATELESS_RENTER_NOT_LANDLORD`

---

## 1. When to Activate This Skill
Trigger this skill whenever:
1. Modifying or debugging `/fixtures`, `/fixtures/arena`, or home page match components (`HomeLiveFixtures.jsx`, `PremierLeagueFixturesHub.jsx`).
2. Optimizing API route caching or sports data ingestion pipelines (`app/api/football/*`, `lib/sports/football.js`).
3. Running pre-flight verification checks on fixtures, vault shapes, or live match feeds before deployment.
4. Ensuring that historical tournament campaigns (e.g. World Cup 2026) remain strictly archived and never reappear as live registration funnels (Zero-FOC).

---

## 2. The 4 Operational Invariants

1. **Zero-FOC Tournament Funnel Invariant:**
   - The World Cup 2026 campaign is concluded and historical.
   - It may only appear as a read-only historical archive link (`/tournament` Archive) in the footer.
   - It must **never** reappear on home heroes, banners, or login screens with entry fees, cash prize promises, or team spots.
2. **Page Visibility Lifecycle Guard:**
   - Client-side live polling (`HomeLiveFixtures.jsx`) must pause when `document.visibilityState !== "visible"`.
   - Never burn user network bandwidth or mobile battery in background tabs.
3. **Selective Event Timeline Fetching:**
   - Never run N+1 timeline queries on historical or scheduled fixtures.
   - Only fetch in-depth timelines when `match.status?.isLive === true`.
4. **Edge CDN Cache Invariant:**
   - Match and metadata API routes must include strict `Cache-Control` headers:
     `public, s-maxage=30, stale-while-revalidate=120` (matches) or `s-maxage=300, stale-while-revalidate=3600` (metadata).

---

## 3. Standard Verification Commands

Before committing or deploying any changes to the fixtures system, run the standard suite on local metal:

```bash
# 1. Run the live fixtures API health check
npm run fixtures:health-check

# 2. Validate the fixtures vault and client contract schemas
npm run validate:fixtures-vault

# 3. Validate progressive update and sync contracts
npm run test:apu

# 4. Verify zero TypeScript errors
npm run typecheck
```

All 4 commands must pass with zero errors.

---

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
