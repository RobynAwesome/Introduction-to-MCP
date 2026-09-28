# 2026-09-29 CodeQL High-Alert Remediation Receipt

## Scope and evidence

The isolated branch `codex/security-high-alert-remediation` is based on `RobynAwesome/Introduction-to-MCP` master at `7245adafe08b31b2e70cae9c10b2e50ba2a0af8e`. The repository alert snapshot showed CodeQL high alert #15 (`py/path-injection`) in `kopano-core/kopano/eco_poc_validate.py` and high alert #25 (`py/polynomial-redos`) in `scripts/kc_bracket_lint.py`. PR #213's CodeQL merge check reported four findings on changed code, including two high and two medium.

## Local changes

- Evidence references are accepted only as repository-relative paths. Absolute paths, drive-qualified paths, parent traversal, and resolved paths escaping the repository root are rejected before a file-existence check.
- The bracket linter now scans bracket tags in one pass instead of applying the previous regular expression to untrusted text.
- Regression tests cover valid repository evidence, preserved JSONL marker behavior, traversal and absolute-path rejection, normal and malformed tags, and long unclosed input.

## Local verification

- `python -m pytest -q tests/test_security_high_alert_remediation.py`: 7 passed.
- `python scripts/kc_bracket_lint.py --self-test`: all 6 self-tests passed.
- `python -m ruff check kopano-core/kopano/eco_poc_validate.py scripts/kc_bracket_lint.py tests/test_security_high_alert_remediation.py`: passed.
- `git diff --cached --check`: passed for the exact five staged files.

## Provider and incident status

No GitHub CodeQL scan has run on this branch yet. The two alert records are not claimed closed until GitHub rescans and confirms that result. Other high CodeQL alerts and Dependabot alert #96 (NLTK 3.10.3 / GHSA-8mgp-746c-j5xp) remain unresolved. The security settings and merge checks are enforcement evidence; they do not establish that exploitation occurred or that none occurred. No breach is confirmed by the evidence reviewed here, and this receipt does not claim an absence of historical exposure.

P0 governance issue #121 remains open. Seat 10 remains suspended and recused. This code change does not implement runtime recusal, seat re-entry enforcement, or incident closure. No production deployment occurred.

## Next admissible action

Publish this branch and open a review PR. Confirm the GitHub CodeQL rescan result and all required checks. Request independent review before merge. Keep unresolved alerts and issue #121 open until their separate evidence and closure criteria are met.