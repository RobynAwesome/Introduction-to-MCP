# Z Code Defect Repair & Retest Receipt

**Date:** 2026-10-22T17:48:00+02:00  
**Executing Lead:** Lead Dev AG (AntiGravity)  
**Independent Verifier:** Z Code  
**Human Authority:** Founder / RTC  
**Target File:** `scripts/security_playground_inventory_gate.py`  
**Base Revision:** `d724844d66614619c0d5a47bba52648d6ef582c5` (PR #326 Head)  
**Repaired Commit SHA:** `aee85e37ee0f20a6dd7580d96b820fa40b609ffb`  
**Branch:** `ag/security-playground-v1-candidate`  
**Status:** Defect Repaired · 12/12 Regression Tests Passing · 17/17 Z Code Adversarial Tests Matching (`WITNESS_TEST_SUITE_REPLAYED_BY_AG`)

---

## 1. Defect Identification & Root Cause

During independent Phase 2 negative testing of PR #326 by Z Code, case `N5a: malformed JSON (trailing comma)` resulted in a process crash with exit code 1 and a traceback, instead of the documented exit code 4 and BLOCK JSON.

### Root Cause
In `scripts/security_playground_inventory_gate.py` (line 123), `sort_keys=True` was erroneously passed to the `print()` function rather than `json.dumps()`:
```python
# DEFECTIVE CODE:
except (OSError, ValueError) as exc:
    print(json.dumps({"verdict": "BLOCK", "error": type(exc).__name__,
                      "runtime_verified": False}), sort_keys=True)
    return 4
```
When `json.loads()` encountered malformed JSON (such as a trailing comma), it raised `json.decoder.JSONDecodeError`. Inside the exception handler, Python raised `TypeError: 'sort_keys' is an invalid keyword argument for print()`, terminating the process with unhandled exit code 1.

Furthermore, non-object JSON inputs (e.g. `evaluate([])`) and the exception handler omitted `"production_authority": False`.

---

## 2. Applied Repair Diff

```diff
--- a/scripts/security_playground_inventory_gate.py
+++ b/scripts/security_playground_inventory_gate.py
@@ -31,3 +31,3 @@ def evaluate(record: object) -> dict:
     if not isinstance(record, dict):
-        return {"verdict": "BLOCK", "reasons": ["input must be a JSON object"],
-                "runtime_verified": False}
+        return {"verdict": "BLOCK", "reasons": ["input must be a JSON object"],
+                "runtime_verified": False, "production_authority": False}
@@ -120,7 +120,12 @@ def main() -> int:
     try:
         record = json.loads(args.input.read_text(encoding="utf-8"))
     except (OSError, ValueError) as exc:
-        print(json.dumps({"verdict": "BLOCK", "error": type(exc).__name__,
-                          "runtime_verified": False}), sort_keys=True)
+        print(json.dumps({
+            "verdict": "BLOCK",
+            "error": type(exc).__name__,
+            "reasons": [f"failed to parse JSON input: {exc}"],
+            "runtime_verified": False,
+            "production_authority": False,
+        }, sort_keys=True))
         return 4
```

---

## 3. Verified Runtime Evidence

### 3.1 Direct Subprocess Verification of Malformed Input
- **Input Payload:** `'{"bad": json,,}'`
- **Captured Exit Code:** **`4`**
- **Captured Stderr:** `""` (Zero traceback emitted)
- **Captured Stdout:**
  ```json
  {"error": "JSONDecodeError", "production_authority": false, "reasons": ["failed to parse JSON input: Expecting value: line 1 column 9 (char 8)"], "runtime_verified": false, "verdict": "BLOCK"}
  ```

### 3.2 Non-Dict Input Verification (`evaluate([])`)
- Input: `[]`, `'test'`, `123`, `None`, `True`
- Result: Consistently returns `verdict: "BLOCK"`, `runtime_verified: false`, `production_authority: false`.

### 3.3 Regression Suite Execution (12 Tests)
```text
test_clean_fixture_is_drill_pass_not_production ... ok
test_cli_exit_codes ... ok
test_cli_malformed_json_exits_4_and_blocks ... ok
test_invalid_receipts_and_revision_hold ... ok
test_isolation_failure_blocks ... ok
test_malformed_fields_fail_closed_without_exception ... ok
test_missing_php_inventory_holds ... ok
test_protected_state_mutation_blocks ... ok
test_real_environment_never_graduates_from_claims ... ok
test_unknown_php_exposure_holds ... ok
test_unverified_isolation_holds ... ok
test_vulnerable_dependency_blocks ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.184s
OK (Regression rc=0)
```

### 3.4 Z Code 17-Case Negative Runner Output (AG Replay)
```text
==============================================================================
Z CODE | Phase 2 Negative-Test Runner
Gate source: scripts/security_playground_inventory_gate.py
Test source: tests/test_security_playground_inventory_gate.py
Python: 3.12.3
==============================================================================

#   Case                                                                   Exp         Act         Rc    St       
--------------------------------------------------------------------------------------------------------------------
1   N1: well-formed fixture with fabricated evidence references            DRILL_PASS  DRILL_PASS  0/0   MATCH    
2   N2: claimed isolation without independent attestation                  DRILL_PASS  DRILL_PASS  0/0   MATCH    
3   N3a: missing PHP runtime inventory record                              HOLD        HOLD        2/2   MATCH    
4   N3b: false not_present declaration (PHP claimed absent, fabricated ev  DRILL_PASS  DRILL_PASS  0/0   MATCH    
5   N4: forged receipt reference                                           DRILL_PASS  DRILL_PASS  0/0   MATCH    
6   N5a: malformed JSON (trailing comma)                                   BLOCK       BLOCK       4/4   MATCH    
7   N5b: missing schema field                                              HOLD        HOLD        2/2   MATCH    
8   N5c: wrong-typed mode (array, not string)                              HOLD        HOLD        2/2   MATCH    
9   N6: protected-state mutation attempted                                 BLOCK       BLOCK       3/3   MATCH    
10  N7: syntactically valid but nonexistent source_revision                DRILL_PASS  DRILL_PASS  0/0   MATCH    
11  N8: DRILL_PASS output must not carry production authority              DRILL_PASS  DRILL_PASS  0/0   MATCH    
12  N9: cloud-mode claim must NOT graduate from fixture DRILL_PASS         HOLD        HOLD        2/2   MATCH    
13  N10: local-mode claim must NOT graduate from fixture DRILL_PASS        HOLD        HOLD        2/2   MATCH    
14  N11: vulnerable dependency must BLOCK                                  BLOCK       BLOCK       3/3   MATCH    
15  N12: unknown PHP status must HOLD                                      HOLD        HOLD        2/2   MATCH    
16  N13: explicit isolation failure (deny_production_network=false) must   BLOCK       BLOCK       3/3   MATCH    
17  N14: unverified isolation control (key absent) must HOLD               HOLD        HOLD        2/2   MATCH    

Overall: regression_rc=0  negative_tests_ok=True
WITNESS_OVERALL_RC=0
STATUS: WITNESS_TEST_SUITE_REPLAYED_BY_AG
```

---

## 4. Preservation of Governance Boundaries

1. **Witness Status Attribution:** This replay establishes Lead Dev AG's verification. Only Z Code may independently certify that the retest has passed following its own execution against the published revision.
2. **Local Sovereignty:** Local GSMB master (`de019c65`) and working branch `codex/kc-sovereign-gui-full-dev` remain unmodified. No rebase or remote overwrite occurred.
3. **PHP Exposure Verdicts:** Preserved under strict founder mandates (`LOCAL: PARTIAL_INVENTORY / HOLD`, `CLOUD: SOURCE_NO_PHP_OBSERVED / RUNTIME_HOLD`, `PRODUCTION: HOLD`).
4. **Approval Boundary:** No merge, branch protection change, or production deployment authorized.

`[LEAD_DEV_AG | Z_CODE_DEFECT_REPAIRED | WITNESS_TEST_SUITE_REPLAYED_BY_AG | INDEPENDENT_RETEST_PENDING]`
