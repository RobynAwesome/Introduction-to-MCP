"""POC tests for the KPGS callable artifact registry."""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

from kopano.callable_artifact_registry import (
    ArtifactContractError,
    discover_artifacts,
    resolve_artifact,
)


class TestCallableArtifactRegistry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifacts = discover_artifacts(REPO_ROOT)
        cls.artifact = resolve_artifact(cls.artifacts, "fep.depiction-of-nature-and-society")

    def test_first_fep_artifact_is_discoverable_by_id_and_alias(self):
        self.assertEqual(self.artifact.artifact_id, "fep.depiction-of-nature-and-society")
        alias = resolve_artifact(self.artifacts, "depict nature and society")
        self.assertEqual(alias.artifact_id, self.artifact.artifact_id)

    def test_versioned_swfus_semantics_are_not_flattened(self):
        legacy = self.artifact.semantic_binding("SWFUS", "legacy_crud2")
        vnext = self.artifact.semantic_binding("SWFUS", "vnext_sync")
        self.assertEqual(legacy["expansion"], "Sever Watch Fortify Unblock Ship")
        self.assertEqual(vnext["expansion"], "State-Wide Framework Universal Synchronization")
        self.assertNotEqual(legacy["expansion"], vnext["expansion"])

    def test_bmp_drift_is_preserved_as_conflict_evidence(self):
        bmp = self.artifact.semantic_binding("BMP")
        self.assertEqual(bmp["selected"], "Black Mask Protocol")
        self.assertTrue(bmp["conflicts"])
        self.assertEqual(bmp["conflicts"][0]["observed_expansion"], "Black Mass Protocol")

    def test_interface_auto_model_is_resolved_to_concrete_model(self):
        env = {
            "KPGS_IDENTITY": "Forge",
            "KPGS_SEAT": "AUDIT_SCOPE",
            "KPGS_INTERFACE_NAME": "ExampleIDE",
            "KPGS_MODEL_PROVIDER": "ExampleProvider",
            "KPGS_INTERFACE_SELECTED_MODEL": "model-selected-by-interface",
            "KPGS_MODEL_VERSION": "2026-09",
        }
        runtime = self.artifact.resolve_runtime(env)
        self.assertTrue(runtime.auto_selected)
        self.assertEqual(runtime.model, "model-selected-by-interface")
        self.assertEqual(runtime.identity_id, "Forge")
        self.assertEqual(runtime.authority_scope, "task_scoped")

    def test_explicit_model_is_used_when_interface_has_no_auto(self):
        env = {
            "KPGS_EXPLICIT_MODEL": "model-selected-explicitly",
            "KPGS_INTERFACE_NAME": "NoAutoIDE",
        }
        runtime = self.artifact.resolve_runtime(env)
        self.assertFalse(runtime.auto_selected)
        self.assertEqual(runtime.model, "model-selected-explicitly")

    def test_literal_auto_and_missing_model_fail_closed(self):
        with self.assertRaises(ArtifactContractError):
            self.artifact.resolve_runtime({"KPGS_INTERFACE_SELECTED_MODEL": "auto"})
        with self.assertRaises(ArtifactContractError):
            self.artifact.resolve_runtime({})


if __name__ == "__main__":
    unittest.main()
