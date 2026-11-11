"""Negative tests for the bounded owner-local Schematics parity probe."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

SRC=Path(__file__).parent/"local_gsmb_parity.py"
SPEC=importlib.util.spec_from_file_location("local_gsmb_parity",SRC)
MOD=importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MOD)


class LocalParityTests(unittest.TestCase):
    def make_roots(self,temp):
        root=Path(temp)
        local=root/"LocalSchematics"
        cloud=root/"checkout"
        local.mkdir()
        (cloud/"Schematics").mkdir(parents=True)
        return local,cloud

    def populate(self,local,cloud,match=True):
        for i,rel in enumerate(MOD.REQUIRED):
            a=local/rel
            b=cloud/"Schematics"/rel
            a.parent.mkdir(parents=True,exist_ok=True)
            b.parent.mkdir(parents=True,exist_ok=True)
            a.write_text("fixture "+str(i),encoding="utf-8")
            b.write_text(("fixture "+str(i)) if match or i else "changed source",encoding="utf-8")

    @patch.object(MOD.subprocess,"run",return_value=SimpleNamespace(stdout="a"*40+"\n"))
    def test_bounded_exact_hash_match_only(self,_):
        with tempfile.TemporaryDirectory() as t:
            local,cloud=self.make_roots(t)
            self.populate(local,cloud)
            r=MOD.audit(local,cloud)
            self.assertEqual(r["verdict"],"MATCHED_BOUNDED_SAMPLE")
            self.assertEqual(len(r["files"]),4)
            self.assertFalse(any("fixture " in str(x) for x in r["files"]))
            self.assertEqual(r["scope"],"Four critical Schematics files only")

    @patch.object(MOD.subprocess,"run",return_value=SimpleNamespace(stdout="a"*40+"\n"))
    def test_drift_holds(self,_):
        with tempfile.TemporaryDirectory() as t:
            local,cloud=self.make_roots(t)
            self.populate(local,cloud,match=False)
            r=MOD.audit(local,cloud)
            self.assertEqual(r["verdict"],"HOLD_PARITY_NOT_PROVEN")
            self.assertFalse(all(x["match"] for x in r["files"]))

    @patch.object(MOD.subprocess,"run",return_value=SimpleNamespace(stdout="a"*40+"\n"))
    def test_missing_local_holds(self,_):
        with tempfile.TemporaryDirectory() as t:
            local,cloud=self.make_roots(t)
            r=MOD.audit(local,cloud)
            self.assertEqual(r["verdict"],"HOLD_PARITY_NOT_PROVEN")
            self.assertFalse(r["local_source_verified"])

    @patch.object(MOD.subprocess,"run",side_effect=OSError("git missing"))
    def test_no_cloud_revision_holds(self,_):
        with tempfile.TemporaryDirectory() as t:
            local,cloud=self.make_roots(t)
            self.populate(local,cloud)
            r=MOD.audit(local,cloud)
            self.assertEqual(r["verdict"],"HOLD_PARITY_NOT_PROVEN")


if __name__=="__main__":
    unittest.main()
