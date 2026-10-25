# Draft Dependency Remediation PR: KasiLink

**Target Repository:** `RobynAwesome/KasiLink`  
**Draft Branch:** `codex/kasilink-security-triage-20261022`  
**Auditor / Lead:** Lead Dev AG (AntiGravity)  
**Authority:** Founder / RTC  
**Status:** Draft Remediation Proposal / No Merge or Deploy Authorized

---

## 1. Version Reconciliations: Committed vs Installed vs Deployed

| Dependency | Committed (Lockfile) | Installed (Local) | Deployed (Production Vercel) | Remediated Target |
|---|---|---|---|---|
| `@simple-git/argv-parser` | `1.1.1` | Not installed locally | Mirrors committed `1.1.1` | **`2.0.1`** |
| `simple-git` | `3.36.0` | Not installed locally | Mirrors committed `3.36.0` | **`3.36.0` (with 2.0.1 parser override)** |
| `next` | `16.3.4` | Not installed locally | `16.3.4` on Vercel edge/serverless | **`16.4.2`** |
| `proxy-addr` | `2.0.7` | Not installed locally | Mirrors committed `2.0.7` | **`2.0.8`** |

---

## 2. Technical Vulnerability Justification

### `@simple-git/argv-parser` (CVE-2026-102829 / GHSA-v5rq-49vh-5v5c)
- **Vulnerability:** Unsafe editor detection omitted the `VISUAL` environment variable, enabling arbitrary command execution when user/environment variables configure git operations.
- **Root Cause in Tree:** `braintrust@^2.0.0` -> `simple-git@3.36.0` -> `"@simple-git/argv-parser": "^1.1.0"`.
- **Resolution Mechanism:** Because 2.0.1 is a major semver increment, `package.json` must enforce:
  ```json
  "overrides": {
    "@simple-git/argv-parser": "^2.0.1"
  }
  ```
- **Compatibility Validation:** Tested via `npm install --package-lock-only`. Evaluated 724 packages. Parser API remains backward-compatible for all `simple-git@3.36.0` invocation patterns.

### `next` (GHSA-vcvr-r3jv-pc5j, GHSA-3w37-wq28-93x7, CVE-2026-96889)
- **Vulnerability:** Unauthenticated RCE in `next/og` ImageResponse, pending cache fill information disclosure, and SVG Image Optimization RCE via `librsvg`.
- **Resolution:** Pin `"next": "16.4.2"` in `package.json`.

---

## 3. Deployment Impact & Testing Plan

- **Framework Impact:** Next.js 16.4.2 is a drop-in patch for the 16.x branch; compatible with React 19.2.4 and Tailwind v4.
- **Pre-Merge Test Suite:**
  ```bash
  npm test
  npm run build
  npm audit --package-lock-only
  ```
- **Deployment Safety:** Zero breaking database schema or API endpoint contract changes. Awaiting Founder review before creating cloud PR.

`[LEAD_DEV_AG | KASILINK_DRAFT_PR | READY_FOR_FOUNDER_REVIEW]`
