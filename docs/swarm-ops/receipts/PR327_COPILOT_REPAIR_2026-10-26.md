# PR #327 Copilot repair - 2026-10-26 SAST

WHO: Codex Forge, stateless renter under Robyn's PR repair directive; no RTC seat. No new agent/teacher/RTC acknowledgement is claimed.
WHAT: Correct 11 Copilot review findings against original head 1b625b624ba11325da2bc32fbf4ab4380226118a.
WHERE: Cloud GSMB RobynAwesome/Introduction-to-MCP, PR #327; clean managed worktree. Local OneDrive and Google Drive remain separate populations and were not synchronized or audited by this repair.
WHY: Prevent malformed or contradictory caller assertions from receiving synthetic admission and remove runtime/authentication overclaims.

| Copilot finding | Repair / regression evidence |
| --- | --- |
| Resource ceilings ignored | Require finite positive numbers and fixed fixture maxima; missing/null/boolean/negative/zero/nonfinite/oversized cases covered |
| Missing privilege flags admitted | Explicit boolean false required; true BLOCK, absent/malformed HOLD |
| Caller-domain spoofing exemption | Privileged claims always BLOCK regardless of caller_domain |
| Evidence sink optional | Require sink ID and all four explicit boolean assertions |
| Keyword-based receipt authentication | Explicit fixture:// policy documented; external references HOLD, synthetic references never authenticate content |
| Teacher signature accepted by truthiness | Any nonempty claimed signature HOLD pending trusted evidence-bound verifier |
| Standalone PHP version unchecked | Same version policy as containers; unsupported branches/backports/malformed versions HOLD |
| Container version/isolation absent | Require explicit isolation and typed upstream version |
| Oz crossing denylist/type bypass | Check every outbound destination; boolean true admission only; malformed endpoints HOLD |
| Array fields crash direct evaluator | Type guards before membership; direct-call and CLI regressions |
| PHP runtime overclaims | Discovery matrix and Z Code handoff corrected; older clearance explicitly superseded |

Validation: `python -m unittest discover -s tests -p 'test_security_playground*.py' -q` passed 42 tests. `git diff --check` passed. Both suites are now included in `.github/workflows/security-playground-fixture.yml` triggers and execution. The previous N5a malformed-JSON repair was backported into #326 (12 tests pass), then its updated head 8a50a481ca97b7d24b1c644f083ea0f0a88ce491 merged into this branch without force pushing.

Preflight: Home/Legacy/root NOW and entry contract recovered. require_hood_ack returned ACKNOWLEDGED. Bracket lint self-test and BlackMask stress (9/9, 19 synthetic mesh agents) passed; generated diagnostic rows saved outside the PR, not promoted as external agent execution. Primary KPEFS vector V1_PLANT (bounded engineering experiment), secondary V4_DIASPORA (sovereignty). Root NOW's October 7 status was stale and is preserved below the dated repair handoff. C.L.E.A.R. reviewed for source/test scope only; CLEAR_PASS does not establish POC validation.

Limits: This evaluator consumes untrusted assertions, does not discover or contain real assets, and authenticates no Git object, receipt, teacher identity or runtime. DRILL_PASS means synthetic assertion checks only. Local PHP remains PARTIAL_INVENTORY/HOLD; Cloud SOURCE_NO_PHP_OBSERVED/RUNTIME_HOLD; IONOS HOLD. PHP upstream policy corresponds to the fixed releases in the existing candidate contract; vendor provenance requires independent review.

Commit gate: See PR326_BASE_REPAIR_2026-10-26.md for the temporary direct-Python KHELOS launcher. Gate logic was retained and scoped to this worktree; no shared hook/configuration mutation.

Next: Re-read hosted results at the pushed commit; owner reviews #326 first, then retargets #327 to master after #326 merges and rechecks its head. No merge, deployment, incident disposition, credential rotation, production acceptance or issue closure is asserted.

Routing update: #327 was retargeted to master to run every required workflow before owner review. The updated #326 remains an ancestor; review #326 first, then reread the reduced #327 diff and strict checks after any merge. Earlier retarget-after-merge guidance above is superseded. All 11 Copilot threads were resolved after the regression suite and pushed source repair; this is not independent teacher/owner acceptance.
