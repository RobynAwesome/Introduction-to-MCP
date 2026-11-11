# Frontier Map and Security Release: DEBUGGING
Status: Review candidate. Do not run in production without scope and permission.

## Exact commands, trusted execution surfaces
Historical provenance + candidate intake:
```sh
python tools/ai_frontier_map/validate_corpus.py data/ai-frontier-map/seed.records.jsonl
python tools/ai_frontier_map/ingest_discoveries.py --input data/ai-frontier-map/intake-2026-11-10.jsonl --output /tmp/intake.jsonl
python tools/ai_frontier_map/validate_corpus.py /tmp/intake.jsonl
python -m unittest discover -s tools/ai_frontier_map -p 'test_*.py' -v
```
Existing governance:
```sh
python scripts/kc_kpgs_governance.py entry --renter-id scoped_probe --assert --hood-ack I_AM_STATELESS_RENTER_NOT_LANDLORD
python scripts/kc_blackmask_bracket_stress.py --no-report-file --operator CI_FRONTIER --json
python scripts/kc_main_brain_roadmap.py gate   # MUST HOLD without authenticated live verifier
python -m unittest discover -s tests -p 'test_capability_lease_runtime.py' -v
python scripts/ci/probe_os_isolation.py      # exit 2 => not isolated
```
No commands above are substitutes for serving production probes. The Black Mask stress test's mesh labels describe synthetic exercise, not live external-agent approvals.

## Known failures and diagnostic meaning
- `GET /users/OyaAIProd/repos => 404`: legacy Oya namespace is stale; use original stable repository IDs via `collect_oya_corpus.py --seed-file`, preserving old and current names separately. Do not enumerate another user's account and pretend it is the old corpus.
- `HOLD_UNVERIFIED_RUNTIME ... verified_production=19`: the historical review-log count is not a provider receipt. Do not fabricate, or add hardcoded `true`, to satisfy the gate. Actual live verifier integration requires separate owner/security acceptance.
- `unshare: write failed /proc/self/uid_map: Operation not permitted`: hosted runner does not allow this kernel user-namespace probe; classify actual runner as HOLD and choose an authorized host-specific containment test.
- `No module named pytest`: clean runner lacked test dependency; pin `pytest==8.4.2` before invoking existing pytest suite.
- `fatal: No url found for submodule path 'KasiLink' in .gitmodules`: checkout cleanup warning; verify underlying job status and repo gitlink, do not reinterpret warning as success/failure of unrelated code.
- Invalid input/duplicate repos: adapter exits 2 and must leave output unwritten.
- Protected capability leases: tests validate reference implementation only; do not infer side-effect security or cross-host revocation persistence.

## Triage report fields
Actor; target repo/commit; deployment exact SHA; source and timestamp; command and exit; prior vs observed; expected falsifier; external permissions; unverified scope; next bounded correction. Preserve previous failures. State `HOLD` when a proof path is missing.
