import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "ci" / "validate_zero_trust_workflows.py"
spec = importlib.util.spec_from_file_location("zero_trust_policy", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


POLICY = {
    "schema": "kpgs.zero-trust-policy.v1",
    "authority": "governance/kpgs-vnext/security",
    "source_of_truth": {
        "repository": "RobynAwesome/Introduction-to-MCP",
        "default_branch": "master",
        "canonical_files": ["NOW.md"],
    },
    "controls": [
        {"id": "ZT-1", "enforcement": "enforced", "requirements": ["deny"]}
    ],
    "production_admission": {
        "required_manifest_states": ["validated", "approved"],
        "required_license_status": "verified-compatible",
        "require_capability_lease": True,
        "require_provenance": True,
        "require_exact_head_ci": True,
        "require_preview_or_production_evidence": True,
        "require_human_review": True,
    },
    "known_holds": [],
    "unknowns": [],
}


class ZeroTrustWorkflowPolicyTests(unittest.TestCase):
    def write(self, directory: Path, name: str, content: str) -> Path:
        path = directory / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_pinned_read_only_workflow_passes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            policy = root / "policy.json"
            policy.write_text(json.dumps(POLICY), encoding="utf-8")
            workflow = self.write(
                root,
                "safe.yml",
                """on:
  pull_request:
permissions:
  contents: read
jobs:
  check:
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
""",
            )
            module.validate_policy(policy)
            module.validate_workflow(workflow, require_pinned_actions=True)

    def test_privileged_trigger_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            workflow = self.write(
                Path(temporary),
                "unsafe.yml",
                """on:
  pull_request_target:
permissions:
  contents: read
""",
            )
            with self.assertRaises(module.ZeroTrustValidationError):
                module.validate_workflow(workflow)

    def test_pull_request_cannot_use_secrets_or_oidc(self):
        with tempfile.TemporaryDirectory() as temporary:
            workflow = self.write(
                Path(temporary),
                "unsafe.yml",
                """on:
  pull_request:
permissions:
  contents: read
jobs:
  check:
    permissions:
      id-token: write
    steps:
      - run: echo ${{ secrets.TOKEN }}
""",
            )
            with self.assertRaises(module.ZeroTrustValidationError):
                module.validate_workflow(workflow)


if __name__ == "__main__":
    unittest.main()
