"""Tests for the lossless NOW.md weekly continuity pilot (W6-NOW-CONTINUITY)."""

from __future__ import annotations

import json
import unittest

from scripts.now_archive_pilot import (
    ARCHIVE_PATH,
    RECEIPTS_JSONL,
    ROOT_NOW,
    WEEK_MD,
    retrieve_failure_context,
    verify_migration,
)


class NowWeeklyRehydrationTests(unittest.TestCase):
    def test_lossless_archive_and_compact_root_now(self) -> None:
        report = verify_migration()
        self.assertTrue(report["verified"])
        self.assertIn(report["archive_bytes"], (182978, 184580))
        lf_bytes = len(ARCHIVE_PATH.read_text(encoding="utf-8").encode("utf-8"))
        self.assertEqual(lf_bytes, 182978)
        self.assertLess(report["root_now_bytes"], 10240)
        self.assertEqual(report["receipts_verified"], 6)

    def test_fresh_agent_cold_boot_answers_succession_questions(self) -> None:
        now_text = ROOT_NOW.read_text(encoding="utf-8")
        week_text = WEEK_MD.read_text(encoding="utf-8")
        receipts = [
            json.loads(line)
            for line in RECEIPTS_JSONL.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertIn("I_AM_STATELESS_RENTER_NOT_LANDLORD", now_text)
        self.assertIn("NOW/2026-11/2026-W46/WEEK.md", now_text)
        self.assertIn("NOW/2026-11/2026-W46/RECEIPTS.jsonl", now_text)
        self.assertIn("NOW/ARCHIVE/NOW_PRE_W46_2026-11-11.md", now_text)

        workstreams = {r["workstream"] for r in receipts}
        self.assertEqual(
            workstreams,
            {
                "W1-ACCT-REV01",
                "W2-ITMCP-SEC",
                "W3-BOOKIT-COURTS",
                "W4-KASILINK-RECOVERY",
                "W5-WEB-JOURNEY",
                "W6-NOW-CONTINUITY",
            },
        )
        self.assertIn("Cold-Boot Succession & Continuity Key", week_text)
        self.assertIn("resolveMongoConnectOptions", week_text)
        self.assertIn("MONGODB_SRV_UNAVAILABLE", week_text)
        self.assertTrue(ARCHIVE_PATH.is_file())

    def test_fresh_agent_retrieves_all_six_failures_without_founder_intervention(self) -> None:
        queries = [
            ("F1-BLACKMASK", "W1-ACCT-REV01", "commandments_ack"),
            ("F2-SPP-PR366", "W2-ITMCP-SEC", "inventory_parity.py"),
            ("F3-BOOKIT-EMPTY-COURTS", "W3-BOOKIT-COURTS", "bookit"),
            ("F4-KASILINK-SRV", "W4-KASILINK-RECOVERY", "NXDOMAIN"),
            ("F5-WEBSITE-ISSUES", "W5-WEB-JOURNEY", "companion:verify"),
            ("F6-NOW-MD-183KB", "W6-NOW-CONTINUITY", "182,978"),
        ]
        for query, expected_ws, expected_keyword in queries:
            matches = retrieve_failure_context(query)
            self.assertEqual(len(matches), 1, f"Expected 1 match for {query}")
            rec = matches[0]
            self.assertEqual(rec["workstream"], expected_ws)
            self.assertTrue(rec["failed_assumptions"])
            self.assertIn(expected_keyword, json.dumps(rec))


if __name__ == "__main__":
    unittest.main()
