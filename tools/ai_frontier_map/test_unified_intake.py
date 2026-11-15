"""Real offline conformance and negative tests for the unified existing AI Frontier Map."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ingest_discoveries import make_record
from collect_oya_corpus import refresh_seed_records
from validate_corpus import validate

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "tools" / "ai_frontier_map" / "ingest_discoveries.py"
SEEDS = ROOT / "data" / "ai-frontier-map" / "seed.records.jsonl"
MANIFEST = ROOT / "data" / "ai-frontier-map" / "intake-2026-11-10.jsonl"


def example(origin_kind="external_discovery"):
    data = {"repo": "test-engineer/example-skill", "origin_kind": origin_kind,
            "observed_at": "2026-11-11"}
    if origin_kind == "founder_fork":
        data["upstream_repo"] = "upstream-creator/example-skill"
    return data


class UnifiedIntakeTests(unittest.TestCase):
    def test_original_oya_seed_records_still_validate(self):
        rows = [json.loads(x) for x in SEEDS.read_text(encoding="utf-8").splitlines() if x.strip()]
        self.assertGreaterEqual(len(rows), 4)
        for i, row in enumerate(rows, 1):
            self.assertEqual(validate(row, i), [], f"legacy seed {i}")

    def test_historical_oya_seed_recovered_by_identity_not_account_name(self):
        class GhFixture:
            def get(self, path):
                repo_id=int(path.rsplit('/',1)[-1])
                return {"id":repo_id, "full_name":f"new-holder/repo-{repo_id}",
                        "html_url":f"https://github.com/new-holder/repo-{repo_id}"}
        rows=refresh_seed_records(GhFixture(),SEEDS,limit=4)
        self.assertEqual(len(rows),4)
        for old, new in zip((json.loads(x) for x in SEEDS.read_text().splitlines() if x.strip()),rows):
            self.assertEqual(validate(new,1),[])
            self.assertEqual(new["provenance"]["oya_repo"],old["provenance"]["oya_repo"])
            self.assertEqual(new["provenance"]["oya_repo_id"],old["provenance"]["oya_repo_id"])
            self.assertEqual(new["provenance"]["observed_repo_id"],old["provenance"]["oya_repo_id"])
            self.assertNotEqual(new["provenance"]["observed_repo"],old["provenance"]["oya_repo"])
            self.assertEqual(new["convergence"]["decision"],old["convergence"]["decision"])
            self.assertEqual(new["reuse_governance"]["mode"],old["reuse_governance"]["mode"])

    def test_independent_repo_has_no_fabricated_authority(self):
        record = make_record(example())
        self.assertEqual(validate(record, 1), [])
        self.assertNotIn("oya_repo", record["provenance"])
        self.assertEqual(record["provenance"]["origin_kind"], "external_discovery")
        self.assertEqual(record["provenance"]["classification"], "unresolved")
        self.assertIsNone(record["provenance"]["observed_repo_id"])
        self.assertIsNone(record["reuse_governance"]["source_commit"])
        self.assertIsNone(record["reuse_governance"]["license"])
        self.assertIsNone(record["frontier_score"]["total"])
        self.assertEqual(record["convergence"]["decision"], "STUDY")
        self.assertEqual(record["reuse_governance"]["mode"], "research_only")
        self.assertIsNone(record["safeskill"]["scan_score"])

    def test_founder_fork_requires_parent(self):
        self.assertEqual(validate(make_record(example("founder_fork")), 1), [])
        sample = example("founder_fork")
        del sample["upstream_repo"]
        with self.assertRaises(ValueError):
            make_record(sample)

    def test_false_upstream_on_independent_rejected(self):
        sample = example()
        sample["upstream_repo"] = "forged/parent"
        with self.assertRaises(ValueError):
            make_record(sample)

    def test_unsafe_input_and_false_link_rejected(self):
        for repo in ("../../etc/passwd", "foo/bar;rm", "https://github.com/foo/bar", "foo/../bar", "foo/.", ""):
            sample = example()
            sample["repo"] = repo
            with self.subTest(repo=repo), self.assertRaises(ValueError):
                make_record(sample)
        bad_issue = example()
        bad_issue["intake_issue"] = "https://evil.invalid/issues/1"
        with self.assertRaises(ValueError):
            make_record(bad_issue)

    def test_code_reuse_without_license_and_sha_fails(self):
        record = make_record(example())
        record["reuse_governance"]["mode"] = "code_reuse"
        self.assertNotEqual(validate(record, 1), [])
        record["reuse_governance"]["license"] = "MIT"
        record["reuse_governance"]["source_commit"] = "a" * 40
        self.assertEqual(validate(record, 1), [])

    def test_schema_specific_legacy_missing_oya_path_holds(self):
        record = make_record(example())
        record["provenance"].pop("origin_kind")
        self.assertTrue(any("oya_repo" in s for s in validate(record, 1)))

    def test_no_fabricated_safeskill_upgrade(self):
        record = make_record(example())
        record["safeskill"]["scan_score"] = 91
        self.assertEqual(record["convergence"]["decision"], "STUDY")
        self.assertEqual(record["reuse_governance"]["mode"], "research_only")

    def test_real_manifest_ingests_five_into_existing_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "output.jsonl"
            cmd = [sys.executable, str(CLI), "--input", str(MANIFEST), "--output", str(out)]
            run = subprocess.run(cmd, capture_output=True, text=True, check=False)
            self.assertEqual(run.returncode, 0, run.stderr)
            records = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(records), 5)
            self.assertEqual(len({r["provenance"]["observed_repo"] for r in records}), 5)
            self.assertTrue(all(validate(r, i) == [] for i, r in enumerate(records, 1)))
            self.assertTrue(all(r["convergence"]["decision"] == "STUDY" for r in records))

    def test_duplicate_or_invalid_manifest_fails_without_output(self):
        with tempfile.TemporaryDirectory() as temp:
            inp = Path(temp) / "bad.jsonl"
            out = Path(temp) / "never_written.jsonl"
            inp.write_text(json.dumps(example()) + "\n" + json.dumps(example()) + "\n", encoding="utf-8")
            run = subprocess.run([sys.executable, str(CLI), "--input", str(inp), "--output", str(out)],
                                 capture_output=True, text=True, check=False)
            self.assertEqual(run.returncode, 2)
            self.assertFalse(out.exists())
            self.assertIn("HOLD", run.stderr)
            inp.write_text(json.dumps({"repo": "../a", "origin_kind": "external_discovery",
                                        "observed_at": "2026-11-11"}) + "\n", encoding="utf-8")
            run = subprocess.run([sys.executable, str(CLI), "--input", str(inp), "--output", str(out)],
                                 capture_output=True, text=True, check=False)
            self.assertEqual(run.returncode, 2)
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
