---
name: kpgs-estate-provenance-sync
description: Standard operational procedures for multi-repo estate synchronization, remote tracking alignment (RobynAwesome upstream vs Kopano-Labs estate fork), and credential-aware git operations on Windows metal using GitHub CLI (gh). Enforces zero-loss rebasing, branch isolation, and preservation surface protection.
---

# KPGS Estate Provenance & Multi-Repo Sync

> **Canonical Authority:** GSMB Distribution Trinity & Master Robyn Kholofelo Rababalela  
> **Constitutional Law:** Commandment 15 (Testimony Protocol) & Bowl FEP 03 (Local-First Compression)  
> **Constraint:** `I_AM_STATELESS_RENTER_NOT_LANDLORD`

---

## 1. When to Activate This Skill
Trigger this skill whenever:
1. Synchronizing branches, commits, or tags across the multi-repository estate (`Introduction-to-MCP`, `Bookit-5s-Arena`, `lefa-ai`, `Project-Jennifer`, `KasiLink`, `starfall-salvage`).
2. Pushing local commits to GitHub remotes without risking credential rejections, headless prompts, or detached HEAD state.
3. Managing the relationship between upstream primary (`RobynAwesome`) and organizational fork (`Kopano-Labs`).
4. Protecting preservation/forensic worktrees (such as `Introduction-to-MCP` on `codex/kc-sovereign-gui-full-dev`) from accidental upstream overwrites or unauthorized auto-merges.

---

## 2. Multi-Repo Authority Matrix

| Repository | Primary Upstream (`origin`) | Organizational Fork (`kopano-labs`) | Local Metal Working Tree | Authority Classification |
|---|---|---|---|---|
| **Bookit-5s-Arena** | `RobynAwesome/Bookit-5s-Arena` | `Kopano-Labs/Bookit-5s-Arena` | `C:\Users\rkhol\Bookit-5s-Arena` | Active Implementation Surface |
| **lefa-ai** | `RobynAwesome/lefa-ai` | — | `C:\Users\rkhol\lefa-ai` | Active Implementation Surface |
| **Project-Jennifer** | `RobynAwesome/Project-Jennifer` | — | `C:\Users\rkhol\Project-Jennifer` | Active Implementation Surface |
| **Introduction-to-MCP** | `RobynAwesome/Introduction-to-MCP` | `Kopano-Labs/Introduction-to-MCP` | `c:\Users\rkhol\OneDrive\Documents\Anthropic\Introduction to MCP` | **FORENSIC / PRESERVATION SURFACE** |

---

## 3. Windows Metal Git & Credential Rules

### Rule 1: Always Ensure Git's Subshell Environment in PowerShell
On Windows PowerShell, git credential helpers configured via GitHub CLI (`gh auth git-credential`) require `sh.exe` to spawn the subshell. If Git's `bin` directories are missing from `$env:Path`, git will fail with:
`error: cannot spawn sh: No such file or directory`

**Canonical Remediation:**
```powershell
$env:Path = "C:\Program Files\Git\bin;C:\Program Files\Git\usr\bin;" + $env:Path
```

### Rule 2: Verify `gh` Authentication Before Push
Never attempt a push before verifying active authentication:
```powershell
gh auth status
```
If not configured:
```powershell
gh auth setup-git
```

### Rule 3: Dry-Run Before Mutation
Always test remote push targets using `--dry-run` to detect upstream divergence, fast-forward conflicts, or branch protections before pushing:
```powershell
git push --dry-run <remote> <branch>
```

### Rule 4: Zero-Loss Rebase Discipline
If remote contains concurrent work from other estate agents or Master:
1. Fetch remote: `git fetch <remote>`
2. Inspect diffstat: `git show --stat <remote>/<branch>`
3. Rebase locally: `git rebase <remote>/<branch>`
4. Re-run local test suite to confirm zero regressions.
5. Push fast-forward: `git push <remote> <branch>`

---

## 4. Preservation Surface Quarantine Law
The local checkout of `Introduction-to-MCP` on branch `codex/kc-sovereign-gui-full-dev` is an uncommitted **Forensic / Preservation Surface**:
- **NEVER** run `git reset --hard` or `git checkout -f` on this surface.
- **NEVER** push `codex/kc-sovereign-gui-full-dev` to `origin/master`.
- Material governance, protocol updates, and skill admissions on this surface must be updated in `NOW.md` and committed only under direct Master instruction.

---

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
