# Draft Dependency Remediation PR: Bookit-5s-Arena

**Target Repository:** `RobynAwesome/Bookit-5s-Arena`  
**Draft Branch:** `codex/bookit-security-triage-20261022`  
**Auditor / Lead:** Lead Dev AG (AntiGravity)  
**Authority:** Founder / RTC  
**Status:** Draft Remediation Proposal / No Merge or Deploy Authorized

---

## 1. Version Reconciliations: Committed vs Installed vs Deployed

| Dependency | Committed (Lockfile) | Installed (Local) | Deployed (Production Vercel) | Remediated Target |
|---|---|---|---|---|
| `undici` | `7.30.0` | Not installed locally | Mirrors committed `7.30.0` | **`7.30.1`** |
| `next` | `15.5.19` | Not installed locally | `15.5.19` (`x-nextjs-prerender: 1`) | **`15.5.28`** |
| `sharp` | `<= 0.35.5-rc.1` | Not installed locally | Mirrors committed lockfile | **`0.35.5`** |
| `nodemailer` | `6.9.16` | Not installed locally | Mirrors committed lockfile | **`10.2.1`** |

---

## 2. Technical Vulnerability Justification

### `undici` (October 2026 Advisories: CVE-2026-109841 & CVE-2026-109869)
- **Vulnerability:**
  - `CVE-2026-109841`: Subresource Integrity (SRI) algorithm matching bypass skips non-lowercase algorithm tokens (e.g. `SHA256`), treating response integrity lists as empty and accepting unsigned/unverified responses.
  - `CVE-2026-109869`: WebSocket client memory exhaustion and process crash DoS.
- **Doctrine Finding:** Committed `7.30.0` is **NOT fully clean**. Minimum required version in 7.x line is **`7.30.1`**.
- **Resolution Mechanism:**
  ```bash
  npm update undici --package-lock-only
  ```
- **Validation:** Executed package-lock update; `node_modules/undici` successfully resolves to `version: 7.30.1` under `@vercel/sandbox@^1.9.3`.

### `next` (GHSA-673q-mjm6-r5xr, CVE-2026-96889, GHSA-p3m5-59mp-jv5r)
- **Vulnerability:** Unauthenticated RCE via App Router cache components returning multiple typed arrays via `use cache`, and Image Optimization RCE via `sharp`/`librsvg`.
- **Resolution:** Update `package.json` to `"next": "^15.5.28"`.

---

## 3. Deployment Impact & Testing Plan

- **Framework Impact:** Upgrading Next.js to 15.5.28 maintains full backward compatibility with React 19, `@react-three/fiber`, and `@react-three/drei`.
- **Pre-Merge Test Suite:**
  ```bash
  npm test
  npm run build
  npm audit --package-lock-only
  ```
- **Deployment Safety:** Production deployment on Vercel (`bookit-5s-arena.vercel.app`) must be triggered only after founder merges the PR.

`[LEAD_DEV_AG | BOOKIT_DRAFT_PR | READY_FOR_FOUNDER_REVIEW]`
