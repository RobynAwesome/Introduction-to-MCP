#!/usr/bin/env python3
"""Audit PreToolUse hooks for the Antigravity Windows tool-lockout class.

Antigravity documents ``command`` as a shell command. On the lockout, Node
received the quoted script path as its entry-point argument, so the quote
characters stayed in the path and ``; exit 0`` never ran. Node then resolved
that non-absolute string against the plugin directory and exited 1. A
``PreToolUse`` hook with matcher ``*`` turned that exit into a block of every
tool.

This tool only reads ``hooks.json`` files and, when asked, moves a plugin
directory out of the scan root. It does not execute hook commands.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

QUOTED_ABSOLUTE = re.compile(r'"(?:[A-Za-z]:\\|\/)')
SHELL_EXIT = re.compile(r";\s*exit\b", re.IGNORECASE)
TELEMETRY_BUNDLE = "telemetry_hook_bundle.js"
KNOWN_PLUGIN = "googlecloudtools.datacloud_telemetry"


class QuarantineError(ValueError):
    """The requested quarantine location is not safe to use."""


@dataclass(frozen=True)
class Finding:
    hooks_path: Path
    plugin_dir: Path
    enabled: bool
    command: str
    reasons: tuple[str, ...]

    @property
    def active(self) -> bool:
        return self.enabled and bool(self.reasons)

    @property
    def moveable(self) -> bool:
        if not self.active:
            return False
        if "unreadable-hooks-json" in self.reasons and "known-telemetry-plugin" not in self.reasons:
            return False
        return True


def _is_known_name(name: str) -> bool:
    return name == KNOWN_PLUGIN or name.startswith(KNOWN_PLUGIN + ".")


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _strict_child(path: Path, root: Path) -> bool:
    resolved = path.resolve()
    root_resolved = root.resolve()
    return _inside(resolved, root_resolved) and resolved != root_resolved


def _known_plugin(hooks_path: Path, root: Path) -> bool:
    if any(_is_known_name(part) for part in hooks_path.parts):
        return True
    return _is_known_name(quarantine_unit(hooks_path, root).name)


def quarantine_unit(hooks_path: Path, root: Path) -> Path:
    """Directory removed from the host scan when containment is applied."""
    unit = hooks_path.parent
    if unit.name == "hooks":
        parent = unit.parent
        if _strict_child(parent, root):
            return parent
    return unit


def command_reasons(command: str, *, known: bool, allow_known_plugin: bool) -> tuple[str, ...]:
    reasons: list[str] = []
    if QUOTED_ABSOLUTE.search(command):
        reasons.append("quoted-absolute-path")
    if SHELL_EXIT.search(command):
        reasons.append("shell-exit-sequence")
    if allow_known_plugin:
        return tuple(reasons)
    normalized = command.replace("\\\\", "\\")
    if TELEMETRY_BUNDLE in command or TELEMETRY_BUNDLE in normalized:
        reasons.append("telemetry-bundle")
    if known:
        reasons.append("known-telemetry-plugin")
    return tuple(reasons)


def _enabled(node: dict[str, object]) -> bool:
    return node.get("enabled", True) is not False


def _iter_commands(node: object, enabled: bool) -> list[tuple[str, bool]]:
    found: list[tuple[str, bool]] = []
    if isinstance(node, dict):
        here = enabled and _enabled(node)
        pre_tool = node.get("PreToolUse")
        if pre_tool is not None:
            found.extend(_commands_from_event(pre_tool, here))
        for key, value in node.items():
            if key == "PreToolUse":
                continue
            found.extend(_iter_commands(value, here))
    elif isinstance(node, list):
        for item in node:
            found.extend(_iter_commands(item, enabled))
    return found


def _commands_from_event(event: object, enabled: bool) -> list[tuple[str, bool]]:
    if isinstance(event, list):
        found: list[tuple[str, bool]] = []
        for item in event:
            found.extend(_commands_from_matcher(item, enabled))
        return found
    return _commands_from_matcher(event, enabled)


def _commands_from_matcher(item: object, enabled: bool) -> list[tuple[str, bool]]:
    if isinstance(item, str):
        return [(item, enabled)]
    if not isinstance(item, dict):
        return []
    here = enabled and _enabled(item)
    if "hooks" in item:
        hooks = item["hooks"]
        found: list[tuple[str, bool]] = []
        if isinstance(hooks, list):
            for hook in hooks:
                found.extend(_command_from_hook(hook, here))
        else:
            found.extend(_command_from_hook(hooks, here))
        return found
    return _command_from_hook(item, here)


def _command_from_hook(hook: object, enabled: bool) -> list[tuple[str, bool]]:
    if isinstance(hook, str):
        return [(hook, enabled)]
    if not isinstance(hook, dict) or "command" not in hook:
        return []
    command = hook["command"]
    here = enabled and _enabled(hook)
    if isinstance(command, str):
        return [(command, here)]
    return [(json.dumps(command, sort_keys=True), here)]


def _enabled_pretool(node: object, enabled: bool = True) -> bool:
    if isinstance(node, dict):
        here = enabled and _enabled(node)
        if "PreToolUse" in node and here:
            return True
        return any(_enabled_pretool(value, here) for value in node.values())
    if isinstance(node, list):
        return any(_enabled_pretool(item, enabled) for item in node)
    return False


def audit_document(
    document: object,
    hooks_path: Path,
    root: Path,
    *,
    allow_known_plugin: bool,
) -> list[Finding]:
    known = _known_plugin(hooks_path, root)
    plugin_dir = quarantine_unit(hooks_path, root)
    findings: list[Finding] = []
    for command, enabled in _iter_commands(document, True):
        reasons = command_reasons(command, known=known, allow_known_plugin=allow_known_plugin)
        if not reasons:
            continue
        findings.append(
            Finding(
                hooks_path=hooks_path,
                plugin_dir=plugin_dir,
                enabled=enabled,
                command=command,
                reasons=reasons,
            )
        )
    if known and not allow_known_plugin and _enabled_pretool(document) and not any(item.enabled for item in findings):
        findings.append(
            Finding(
                hooks_path=hooks_path,
                plugin_dir=plugin_dir,
                enabled=True,
                command="",
                reasons=("known-telemetry-plugin", "pretooluse-without-command"),
            )
        )
    return findings


def audit_file(path: Path, root: Path, *, allow_known_plugin: bool) -> list[Finding]:
    known = _known_plugin(path, root)
    plugin_dir = quarantine_unit(path, root)
    try:
        text = path.read_text(encoding="utf-8")
        document = json.loads(text)
    except (OSError, UnicodeError, json.JSONDecodeError):
        reasons = ["unreadable-hooks-json"]
        if known and not allow_known_plugin:
            reasons.append("known-telemetry-plugin")
        return [
            Finding(
                hooks_path=path,
                plugin_dir=plugin_dir,
                enabled=True,
                command="",
                reasons=tuple(reasons),
            )
        ]
    return audit_document(document, path, root, allow_known_plugin=allow_known_plugin)


def audit_tree(root: Path, *, allow_known_plugin: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted(root.rglob("hooks.json")):
        if not path.is_file() or not _inside(path, root):
            continue
        findings.extend(audit_file(path, root, allow_known_plugin=allow_known_plugin))
    return findings


def _unique_dest(dest_root: Path, name: str) -> Path:
    candidate = dest_root / name
    if not candidate.exists():
        return candidate
    for suffix in range(2, 100):
        candidate = dest_root / f"{name}-{suffix}"
        if not candidate.exists():
            return candidate
    raise QuarantineError(f"no free quarantine name for {name}")


def quarantine(root: Path, findings: list[Finding], dest_root: Path) -> list[tuple[Path, Path]]:
    root_resolved = root.resolve()
    dest_resolved = dest_root.resolve()
    if _inside(dest_resolved, root_resolved) or _inside(root_resolved, dest_resolved):
        raise QuarantineError("quarantine directory must be outside the scan root")
    dest_resolved.mkdir(parents=True, exist_ok=True)
    moved: list[tuple[Path, Path]] = []
    seen: set[Path] = set()
    for finding in findings:
        if not finding.moveable:
            continue
        unit = finding.plugin_dir.resolve()
        if unit in seen:
            continue
        seen.add(unit)
        if not _strict_child(unit, root_resolved):
            print(f"QUARANTINE_SKIP {unit}", file=sys.stderr)
            continue
        dest = _unique_dest(dest_resolved, unit.name)
        shutil.move(str(unit), str(dest))
        moved.append((unit, dest))
    return moved


def _format_finding(label: str, finding: Finding) -> str:
    reasons = ",".join(finding.reasons)
    command = finding.command.replace("\n", "\\n")
    return f"{label} {reasons} {finding.hooks_path}\n  command: {command}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Directory to scan for hooks.json")
    parser.add_argument(
        "--quarantine",
        type=Path,
        help="Move active plugin directories here. Must be outside the scan root.",
    )
    parser.add_argument(
        "--allow-known-plugin",
        action="store_true",
        help="Do not flag googlecloudtools.datacloud_telemetry by name. "
        "Quoted paths and shell exit sequences are still flagged.",
    )
    args = parser.parse_args(argv)
    root = args.root
    if not root.is_dir():
        print(f"NOT_A_DIRECTORY {root}", file=sys.stderr)
        return 1
    findings = audit_tree(root, allow_known_plugin=args.allow_known_plugin)
    if args.quarantine is not None:
        try:
            moved = quarantine(root, findings, args.quarantine)
        except QuarantineError as exc:
            print(f"QUARANTINE_REFUSED {exc}", file=sys.stderr)
            return 1
        for src, dest in moved:
            print(f"QUARANTINED {src} -> {dest}")
        findings = audit_tree(root, allow_known_plugin=args.allow_known_plugin)
    active = [item for item in findings if item.active]
    latent = [item for item in findings if not item.active]
    for item in active:
        print(_format_finding("ACTIVE", item))
    for item in latent:
        print(_format_finding("LATENT", item))
    print(f"ACTIVE_COUNT {len(active)}")
    print(f"LATENT_COUNT {len(latent)}")
    return 2 if active else 0


if __name__ == "__main__":
    sys.exit(main())
