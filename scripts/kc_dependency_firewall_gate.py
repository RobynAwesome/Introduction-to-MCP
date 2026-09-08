#!/usr/bin/env python3
"""Fail closed when npm lockfiles install packages below the dependency firewall floor.

Policy source: docs/swarm-ops/DEPENDENCY_FIREWALL.json
Primary trigger: GHSA-73wf-gq98-2v4g (browserslist <= 4.28.6).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "docs" / "swarm-ops" / "DEPENDENCY_FIREWALL.json"


def parse_version(value: str) -> tuple[int, ...]:
    """Parse a leading numeric semver prefix into comparable ints."""
    core = value.strip().lstrip("vV").split("+", 1)[0].split("-", 1)[0]
    parts: list[int] = []
    for token in core.split("."):
        digits = "".join(ch for ch in token if ch.isdigit())
        if not digits:
            break
        parts.append(int(digits))
    if not parts:
        raise ValueError(f"unparseable version: {value!r}")
    return tuple(parts)


def version_lt(installed: str, minimum: str) -> bool:
    a = parse_version(installed)
    b = parse_version(minimum)
    width = max(len(a), len(b))
    a_pad = a + (0,) * (width - len(a))
    b_pad = b + (0,) * (width - len(b))
    return a_pad < b_pad


def load_policy() -> dict[str, Any]:
    if not POLICY_PATH.is_file():
        raise SystemExit(f"FIREWALL FAIL: missing policy at {POLICY_PATH}")
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def discover_lockfiles(policy: dict[str, Any]) -> list[Path]:
    ignore = policy.get("npm", {}).get("ignore_path_substrings", [])
    found: list[Path] = []
    for path in ROOT.rglob("package-lock.json"):
        rel = path.relative_to(ROOT).as_posix()
        if any(token in rel for token in ignore):
            continue
        found.append(path)
    return sorted(found)


def packages_from_lock(lock: dict[str, Any]) -> dict[str, str]:
    """Map package name -> installed version from npm lockfile v1/v2/v3 shapes."""
    out: dict[str, str] = {}

    packages = lock.get("packages")
    if isinstance(packages, dict):
        for key, meta in packages.items():
            if not isinstance(meta, dict):
                continue
            version = meta.get("version")
            if not isinstance(version, str) or not version:
                continue
            name = meta.get("name")
            if isinstance(name, str) and name:
                out[name] = version
                continue
            # key like "node_modules/browserslist" or "node_modules/foo/node_modules/bar"
            if "node_modules/" in key:
                leaf = key.rsplit("node_modules/", 1)[-1]
                if leaf and not leaf.startswith("."):
                    out[leaf] = version

    def walk_deps(node: dict[str, Any]) -> None:
        deps = node.get("dependencies")
        if not isinstance(deps, dict):
            return
        for name, meta in deps.items():
            if not isinstance(meta, dict):
                continue
            version = meta.get("version")
            if isinstance(version, str) and version:
                out[name] = version
            walk_deps(meta)

    walk_deps(lock)
    return out


def check_lockfile(path: Path, floors: dict[str, str]) -> list[str]:
    violations: list[str] = []
    try:
        lock = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path.relative_to(ROOT).as_posix()}: invalid JSON ({exc})"]

    installed = packages_from_lock(lock)
    rel = path.relative_to(ROOT).as_posix()
    for name, minimum in floors.items():
        version = installed.get(name)
        if version is None:
            continue
        try:
            if version_lt(version, minimum):
                violations.append(
                    f"{rel}: {name}@{version} is below firewall floor {minimum}"
                )
        except ValueError as exc:
            violations.append(f"{rel}: {name}@{version} ({exc})")
    return violations


def main() -> int:
    policy = load_policy()
    floors = policy.get("npm", {}).get("minimum_versions", {})
    if not isinstance(floors, dict) or not floors:
        print("FIREWALL FAIL: npm.minimum_versions missing/empty", file=sys.stderr)
        return 2

    lockfiles = discover_lockfiles(policy)
    if not lockfiles:
        print("FIREWALL FAIL: no package-lock.json files discovered", file=sys.stderr)
        return 2

    violations: list[str] = []
    for lockfile in lockfiles:
        violations.extend(check_lockfile(lockfile, floors))

    print(f"Dependency firewall: scanned {len(lockfiles)} lockfile(s)")
    for name, minimum in sorted(floors.items()):
        print(f"  floor {name} >= {minimum}")

    if violations:
        print("FIREWALL FAIL: blocked packages detected", file=sys.stderr)
        for item in violations:
            print(f"  - {item}", file=sys.stderr)
        print(
            "Remediate with npm overrides + lockfile refresh, then re-run "
            "scripts/kc_dependency_firewall_gate.py",
            file=sys.stderr,
        )
        return 1

    print("FIREWALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
