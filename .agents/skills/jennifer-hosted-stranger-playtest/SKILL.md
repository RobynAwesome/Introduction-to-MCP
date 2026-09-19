---
name: jennifer-hosted-stranger-playtest
description: Protocol and execution guidelines for Project Jennifer Sprint A2 (Hosted Stranger Honesty). Covers production Vercel hosting setup, cross-origin CORS verification between web and API, live human playtest execution using the LOVE_LOOP_PLAYTEST protocol, and unalterable playtest receipt logging.
---

# Jennifer Hosted Stranger Playtest Protocol

> **Canonical Authority:** GSMB Distribution Trinity & Master Robyn Kholofelo Rababalela  
> **Constitutional Law:** Commandment 15 (Testimony Protocol) & Game Dedication Charter  
> **Constraint:** `I_AM_STATELESS_RENTER_NOT_LANDLORD`  
> **Core Law:** Loved ≠ Proven · Stranger Retention > Creator Affection

---

## 1. When to Activate This Skill
Trigger this skill whenever:
1. Advancing Project Jennifer from local development (Phase 1, Sprints A/B/C) to hosted public availability (Phase 2, Sprint A2).
2. Configuring production deployment parameters (Vercel secrets, `NEXT_PUBLIC_JENNIFER_API_URL`, `JENNIFER_CORS_ORIGINS`).
3. Running a live human playtest session with a non-creator player ("stranger test").
4. Recording the official `LOVE_LOOP_PLAYTEST` receipt to evaluate the "Production Love" gate.

---

## 2. Prerequisites & Pre-Flight Checklist

Before launching a public playtest session, verify on metal:
1. **Local Smoke Tests Passing:**
   ```bash
   pnpm smoke:love-loop
   pnpm smoke:love-loop-reliability
   ```
2. **Environment Variables Configured:**
   - Web: `NEXT_PUBLIC_JENNIFER_API_URL` pointing to the live API URL.
   - API: `JENNIFER_CORS_ORIGINS` includes the production web domain (e.g. `https://project-jennifer.vercel.app`).
   - Public API: `JENNIFER_CORS_ALLOW_MISSING_ORIGIN` left unset or false (disallowing spoofed requests).
3. **Trigger Deployment:**
   - Run GitHub Actions `deploy-web.yml` via `workflow_dispatch` with `deploy_web=true`.
   - Confirm HTTP 200 on both web `/game` and API `/api/health`.

---

## 3. The 4-Step Playtest Execution Loop

```text
[ 1. STRANGER INVITATION ]
  └── Provide clean hosted URL (no developer instructions, no prompts)
        |
        v
[ 2. UNGUIDED PLAYTHROUGH ]
  ├── Player navigates from start screen to first episode
  ├── Chooses dialogue branch (Third Signal episode)
  └── Experiences consequence animation and divergence feedback
        |
        v
[ 3. LIVE OBSERVATION ]
  ├── Measure: Did the player understand the consequence?
  └── Measure: Did the player encounter any visual or state glitch?
        |
        v
[ 4. POST-PLAY DEBRIEF & RECEIPT ]
  ├── Ask the 2 Canonical Questions (see Section 4)
  └── Record immutable receipt in docs/playtesting/
```

---

## 4. The Two Canonical Playtest Questions
Immediately upon completing the play loop, ask the stranger:
1. **Clarity Question:** *"What did your choice just change in the city?"* (Tests Efficacy & Narrative Feedback)
2. **Retention Question:** *"Would you come back tomorrow to see the next episode?"* (Tests Real Retention)

**Passing Bar:**
- Clarity: Player correctly identifies the divergence without prompt.
- Retention: Majority "Yes" without hesitation.

---

## 5. Playtest Receipt Template
Log results in `Project-Jennifer/docs/playtesting/RECEIPT_YYYY-MM-DD_PLAYTEST_[ID].md`:

```markdown
# Live Playtest Receipt — [Session ID]

- Date: YYYY-MM-DD
- Host URL: https://...
- Observer: [Agent / Tester] (I_AM_STATELESS_RENTER_NOT_LANDLORD)
- Player Type: Stranger / External User
- Loop Completed: YES / NO
- Technical Errors: [None | List of glitches]
- Player Response Q1 (Clarity): "[Direct Quote]"
- Player Response Q2 (Retention): "[Direct Quote]"
- Gate Decision: [PASS | HOLD | ITERATE]
```

---

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
