"""Run browser-surface DOM-safety regressions with Node's built-in test runner."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")


@pytest.mark.skipif(NODE is None, reason="Node.js is required for the static-page DOM contract tests")
def test_frontend_untrusted_payloads_are_rendered_as_text():
    result = subprocess.run(
        [NODE, "--test", str(REPO / "tests" / "xss_frontend_regressions.cjs")],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"Node DOM regression tests failed:\n{result.stdout}\n{result.stderr}"
