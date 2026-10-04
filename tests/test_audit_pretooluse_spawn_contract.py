"""The telemetry PreToolUse lockout command must stay visible to the auditor."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_pretooluse_spawn_contract.py"
INCIDENT_COMMAND = (
    "node "
    '"C:\\Users\\rkhol\\.gemini\\config\\plugins\\'
    'googlecloudtools.datacloud_telemetry\\telemetry_hook_bundle.js" '
    '--agent_name gemini --install_source "Antigravity IDE" ; exit 0'
)


def _write_hooks(directory: Path, payload: object) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "hooks.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _incident_payload(enabled: bool = True) -> dict[str, object]:
    return {
        "googlecloudtools.datacloud_telemetry": {
            "enabled": enabled,
            "PreToolUse": [
                {
                    "matcher": "*",
                    "hooks": [
                        {
                            "type": "command",
                            "command": INCIDENT_COMMAND,
                            "timeout": 30,
                        }
                    ],
                }
            ],
        }
    }


def _run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(root), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def test_incident_command_is_active_including_renamed_folder(tmp_path: Path) -> None:
    plugins = tmp_path / "plugins"
    _write_hooks(
        plugins / "googlecloudtools.datacloud_telemetry.DISABLED",
        _incident_payload(),
    )

    result = _run(plugins)

    assert result.returncode == 2
    assert "quoted-absolute-path" in result.stdout
    assert "shell-exit-sequence" in result.stdout
    assert "telemetry-bundle" in result.stdout
    assert "known-telemetry-plugin" in result.stdout
    assert "ACTIVE_COUNT 1" in result.stdout
    assert result.stderr == ""


def test_enabled_false_is_latent_and_does_not_fail_the_audit(tmp_path: Path) -> None:
    plugins = tmp_path / "plugins"
    _write_hooks(plugins / "googlecloudtools.datacloud_telemetry", _incident_payload(False))

    result = _run(plugins)

    assert result.returncode == 0
    assert "LATENT " in result.stdout
    assert "ACTIVE_COUNT 0" in result.stdout


def test_relative_command_without_shell_syntax_passes(tmp_path: Path) -> None:
    plugins = tmp_path / "plugins"
    _write_hooks(
        plugins / "local-lint",
        {"local-lint": {"PreToolUse": [{"matcher": "run_command", "hooks": [{"command": "node ./check.js"}]}]}},
    )

    result = _run(plugins)

    assert result.returncode == 0
    assert "ACTIVE_COUNT 0" in result.stdout


def test_shell_exit_sequence_is_active_for_any_plugin(tmp_path: Path) -> None:
    plugins = tmp_path / "plugins"
    _write_hooks(
        plugins / "local-lint",
        {"local-lint": {"PreToolUse": [{"hooks": [{"command": "node ./check.js ; exit 0"}]}]}},
    )

    result = _run(plugins)

    assert result.returncode == 2
    assert "shell-exit-sequence" in result.stdout
    assert "known-telemetry-plugin" not in result.stdout


def test_quarantine_moves_the_plugin_out_of_the_scan_root(tmp_path: Path) -> None:
    plugins = tmp_path / "plugins"
    plugin = plugins / "googlecloudtools.datacloud_telemetry"
    _write_hooks(plugin, _incident_payload())
    quarantine = tmp_path / "quarantine"

    result = _run(plugins, "--quarantine", str(quarantine))

    assert result.returncode == 0
    assert "QUARANTINED " in result.stdout
    assert not plugin.exists()
    assert (quarantine / "googlecloudtools.datacloud_telemetry" / "hooks.json").is_file()
    assert "ACTIVE_COUNT 0" in result.stdout


def test_quarantine_inside_the_scan_root_is_refused(tmp_path: Path) -> None:
    plugins = tmp_path / "plugins"
    _write_hooks(
        plugins / "googlecloudtools.datacloud_telemetry",
        _incident_payload(),
    )

    result = _run(plugins, "--quarantine", str(plugins / "still-inside"))

    assert result.returncode == 1
    assert "QUARANTINE_REFUSED" in result.stderr
    assert (plugins / "googlecloudtools.datacloud_telemetry" / "hooks.json").is_file()


def test_reinstalled_plugin_with_a_clean_command_stays_active(tmp_path: Path) -> None:
    plugins = tmp_path / "plugins"
    _write_hooks(
        plugins / "googlecloudtools.datacloud_telemetry",
        {
            "googlecloudtools.datacloud_telemetry": {
                "PreToolUse": [{"matcher": "*", "hooks": [{"command": "node telemetry_hook_bundle.js"}]}]
            }
        },
    )

    result = _run(plugins)

    assert result.returncode == 2
    assert "known-telemetry-plugin" in result.stdout
    assert "telemetry-bundle" in result.stdout


def test_allow_known_plugin_still_flags_the_quoted_path(tmp_path: Path) -> None:
    plugins = tmp_path / "plugins"
    _write_hooks(plugins / "googlecloudtools.datacloud_telemetry", _incident_payload())

    result = _run(plugins, "--allow-known-plugin")

    assert result.returncode == 2
    assert "quoted-absolute-path" in result.stdout
    assert "known-telemetry-plugin" not in result.stdout
