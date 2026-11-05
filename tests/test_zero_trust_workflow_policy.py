import importlib.util
import json
import os
import shutil
import subprocess
import textwrap
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


    @unittest.skipUnless(shutil.which("git") and shutil.which("bash"), "git and bash required")
    def test_checkout_uses_event_commit_when_pull_ref_is_stale(self):
        workflow = Path(__file__).parents[1] / ".github/workflows/kpgs-zero-trust-gate.yml"
        checkout = workflow.read_text(encoding="utf-8").split("        run: |\n", 1)[1]
        script = textwrap.dedent(checkout.split("\n      - name:", 1)[0])
        script = script.replace("${{ github.repository }}", "owner/repo")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            origin = root / "origin"
            origin.mkdir()
            work = root / "checkout"
            work.mkdir()
            env = os.environ.copy()
            env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")

            def git(*arguments, cwd=origin):
                return subprocess.check_output(
                    ["git", *arguments], cwd=cwd, env=env,
                    text=True, stderr=subprocess.DEVNULL,
                ).strip()

            git("init", "--quiet")
            for message in ("old", "event"):
                git("-c", "user.name=Checkout Test", "-c", "user.email=checkout@example.invalid",
                    "commit", "--quiet", "--allow-empty", "-m", message)
                if message == "old":
                    stale = git("rev-parse", "HEAD")
            expected = git("rev-parse", "HEAD")
            git("update-ref", "refs/pull/317/head", stale)
            env.update({
                "EVENT_NAME": "pull_request", "PR_NUMBER": "317",
                "PR_HEAD_SHA": expected, "EXPECTED_SHA": stale, "GH_TOKEN": "local-test",
                "GIT_CONFIG_COUNT": "2",
                "GIT_CONFIG_KEY_0": f"url.{origin.as_uri()}.insteadOf",
                "GIT_CONFIG_VALUE_0": "https://x-access-token:local-test@github.com/owner/repo.git",
                "GIT_CONFIG_KEY_1": "protocol.file.allow", "GIT_CONFIG_VALUE_1": "always",
            })
            result = subprocess.run(
                ["bash", "-c", script], cwd=work, env=env,
                text=True, capture_output=True, timeout=20,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(git("rev-parse", "HEAD", cwd=work), expected)
            self.assertEqual(git("remote", cwd=work), "")

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
