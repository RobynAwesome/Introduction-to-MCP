"""The repaired telemetry hook must fail open without a quoted shell command."""

from __future__ import annotations

import json
import os
import subprocess
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "scripts" / "telemetry_hook_failopen.js"
REWRITER = ROOT / "scripts" / "rewrite_datacloud_hook_command.js"
REPAIR = ROOT / "scripts" / "repair_datacloud_telemetry_hook.ps1"
SAFE_COMMAND = (
    r"node C:\Users\rkhol\.gemini\config\plugins\googlecloudtools.datacloud_telemetry"
    r"\telemetry_hook_failopen.js --agent_name gemini --install_source antigravity-ide"
)
INCIDENT_COMMAND = (
    'node "C:\\Users\\rkhol\\.gemini\\config\\plugins\\'
    'googlecloudtools.datacloud_telemetry\\telemetry_hook_bundle.js" '
    '--agent_name gemini --install_source "Antigravity IDE" ; exit 0'
)


def _run_node(
    args: list[str], cwd: Path, env: dict[str, str] | None = None, stdin: bytes = b""
) -> subprocess.CompletedProcess[bytes]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(
        ["node", *args],
        cwd=cwd,
        env=merged,
        input=stdin,
        capture_output=True,
        check=False,
    )


def _extract_here_string(text: str, marker: str) -> str:
    chunk = text.split(f"# {marker}_BEGIN\n", 1)[1]
    body = chunk.split("@'\n", 1)[1]
    content, _closer = body.split("\n'@", 1)
    return content + "\n"


def test_repair_script_embeds_the_same_javascript() -> None:
    text = REPAIR.read_text(encoding="utf-8")
    assert _extract_here_string(text, "REWRITER_JS") == REWRITER.read_text(encoding="utf-8")
    assert _extract_here_string(text, "WRAPPER_JS") == WRAPPER.read_text(encoding="utf-8")


def test_rewriter_replaces_the_incident_command(tmp_path: Path) -> None:
    hooks = tmp_path / "hooks.json"
    hooks.write_text(
        json.dumps(
            {
                "googlecloudtools.datacloud_telemetry": {
                    "enabled": True,
                    "PreToolUse": [
                        {
                            "matcher": "*",
                            "hooks": [{"type": "command", "command": INCIDENT_COMMAND, "timeout": 30}],
                        }
                    ],
                }
            }
        ),
        encoding="utf-8",
    )

    result = _run_node([str(REWRITER), str(hooks), SAFE_COMMAND], tmp_path)
    document = json.loads(hooks.read_text(encoding="utf-8"))
    command = document["googlecloudtools.datacloud_telemetry"]["PreToolUse"][0]["hooks"][0]["command"]

    assert result.returncode == 0
    assert command == SAFE_COMMAND
    assert "telemetry_hook_bundle.js" not in hooks.read_text(encoding="utf-8")
    assert "; exit" not in command


def test_rewriter_rejects_a_quoted_command(tmp_path: Path) -> None:
    hooks = tmp_path / "hooks.json"
    hooks.write_text('{"command": "node telemetry_hook_bundle.js"}\n', encoding="utf-8")

    result = _run_node([str(REWRITER), str(hooks), 'node "C:\\temp\\hook.js"'], tmp_path)

    assert result.returncode == 2
    assert b"COMMAND_NOT_SPAWN_SAFE" in result.stderr
    assert "telemetry_hook_bundle.js" in hooks.read_text(encoding="utf-8")


def test_wrapper_exits_zero_when_the_bundle_exits_one(tmp_path: Path) -> None:
    (tmp_path / "telemetry_hook_bundle.js").write_text(
        "process.stderr.write('bundle-failed\\n'); process.exit(1);\n",
        encoding="utf-8",
    )
    (tmp_path / "telemetry_hook_failopen.js").write_text(WRAPPER.read_text(encoding="utf-8"), encoding="utf-8")

    result = _run_node(
        ["telemetry_hook_failopen.js"],
        tmp_path,
        env={"DATACLOUD_HOOK_FAIL_OPEN_MS": "5000"},
    )

    assert result.returncode == 0
    assert b"bundle-failed" in result.stderr


def test_wrapper_exits_zero_when_the_bundle_is_missing(tmp_path: Path) -> None:
    (tmp_path / "telemetry_hook_failopen.js").write_text(WRAPPER.read_text(encoding="utf-8"), encoding="utf-8")

    result = _run_node(
        ["telemetry_hook_failopen.js"],
        tmp_path,
        env={"DATACLOUD_HOOK_FAIL_OPEN_MS": "5000"},
    )

    assert result.returncode == 0


def test_wrapper_forwards_stdin_and_hides_the_bundle_exit_code(tmp_path: Path) -> None:
    received = tmp_path / "received.txt"
    (tmp_path / "telemetry_hook_bundle.js").write_text(
        textwrap.dedent(
            """\
            const fs = require('fs');
            let data = '';
            process.stdin.setEncoding('utf8');
            process.stdin.on('data', (chunk) => { data += chunk; });
            process.stdin.on('end', () => {
              fs.writeFileSync(process.argv[2], data);
              process.exit(3);
            });
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "telemetry_hook_failopen.js").write_text(WRAPPER.read_text(encoding="utf-8"), encoding="utf-8")

    result = _run_node(
        ["telemetry_hook_failopen.js", str(received)],
        tmp_path,
        env={"DATACLOUD_HOOK_FAIL_OPEN_MS": "5000"},
        stdin=b'{"tool":"ok"}\n',
    )

    assert result.returncode == 0
    assert received.read_text(encoding="utf-8") == '{"tool":"ok"}\n'


def test_wrapper_exits_zero_when_the_bundle_hangs(tmp_path: Path) -> None:
    (tmp_path / "telemetry_hook_bundle.js").write_text("setInterval(() => {}, 1000);\n", encoding="utf-8")
    (tmp_path / "telemetry_hook_failopen.js").write_text(WRAPPER.read_text(encoding="utf-8"), encoding="utf-8")

    result = _run_node(
        ["telemetry_hook_failopen.js"],
        tmp_path,
        env={"DATACLOUD_HOOK_FAIL_OPEN_MS": "300"},
    )

    assert result.returncode == 0
