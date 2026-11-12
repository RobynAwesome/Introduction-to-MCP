#!/usr/bin/env python3
"""Antigravity SessionStart and PreToolUse enforcement gate for KPGS stateless renters.

Complies with Google Antigravity's documented hooks specification (camelCase stdin/stdout,
``decision: "deny"`` with exit code 0) and passes ``scripts/audit_pretooluse_spawn_contract.py``
(``ACTIVE_COUNT 0``).

Security invariants enforced fail-closed before any mutating tool executes:
1. Cross-platform path classification (Windows drive, drive-relative, UNC, NT device,
   POSIX absolute, relative traversal, symlinks, and strict workspace boundaries).
2. Missing or untrusted capability lease context denies all mutating operations.
3. Renter-modifiable hook context cannot store reusable signing authority (Ed25519
   public verifying keys only; context/keys/ledger must sit outside writable roots).
4. ``run_command`` and equivalent execution tools cannot circumvent filesystem or
   capability restrictions via shell redirection, inline code, encoding, or outside paths.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import importlib.util
import json
import os
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
import re
import shlex
import sys
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
KOPANO_CORE = REPO_ROOT / "kopano-core"
if str(KOPANO_CORE) not in sys.path:
    sys.path.insert(0, str(KOPANO_CORE))

READ_ONLY_TOOLS = {
    "read_file",
    "view_file",
    "view_file_outline",
    "view_code_item",
    "list_dir",
    "find_by_name",
    "grep_search",
    "search_web",
    "search_marketplace",
    "list_resources",
    "read_resource",
    "list_plugin_accounts",
    "ask_question",
    "command_status",
    "read_terminal",
}

TOOL_TO_CAPABILITY: dict[str, str] = {
    "run_command": "command.execute",
    "send_command_input": "command.execute",
    "manage_task": "command.execute",
    "schedule": "command.execute",
    "write_to_file": "repo.file.write",
    "write_file": "repo.file.write",
    "replace_file_content": "repo.file.write",
    "multi_replace_file_content": "repo.file.write",
    "edit_file": "repo.file.write",
    "apply_patch": "repo.file.write",
    "delete_file": "repo.file.write",
    "invoke_subagent": "agent.spawn",
    "define_subagent": "agent.spawn",
    "manage_subagents": "agent.spawn",
    "send_message": "agent.spawn",
    "swarm": "agent.spawn",
    "call_mcp_tool": "mcp.invoke",
}

FORBIDDEN_SIGNING_CONTEXT_KEYS = frozenset(
    {
        "hmac_key",
        "hmac_key_hex",
        "restriction_hmac_key",
        "restriction_hmac_key_hex",
        "private_key",
        "private_key_hex",
        "private_key_pem",
        "private_seed",
        "private_seed_hex",
        "signing_key",
        "signing_key_hex",
        "signing_seed",
        "signing_seed_hex",
        "secret_key",
    }
)

FORBIDDEN_SIGNING_ENV_VARS = (
    "KPGS_LEASE_HMAC_KEY",
    "KPGS_PRIVATE_KEY",
    "KPGS_SIGNING_SEED",
)

DESTRUCTIVE_CMD_RE = re.compile(
    r"(?:git\s+push\s+[^\n]*--force|git\s+push\s+-f\b|git\s+reset\s+--hard|"
    r"rm\s+-[^\n]*r[^\n]*f|Remove-Item\s+[^\n]*-Recurse|del\s+/[^\n]*s|"
    r"\b(?:format|mklink)\b)",
    re.IGNORECASE,
)

OBFUSCATED_EXEC_RE = re.compile(
    r"(?:\bpowershell(?:\.exe)?\b|\bpwsh(?:\.exe)?\b)[^\n]*\s-(?:enc|encodedcommand|ec)\b|"
    r"\bInvoke-Expression\b|\biex\b|\bbase64\s+(?:-d|--decode)\b|"
    r"\$\([^)]+\)|`[^`]+`",
    re.IGNORECASE,
)

INLINE_INTERPRETER_RE = re.compile(
    r"(?:^|[;&|]\s*|\s)(?:python3?(?:\.\d+)?|py|node|nodejs|perl|ruby|php|bash|sh|zsh|pwsh|powershell)(?:\.exe)?\s+(?:-[A-Za-z]*[ce]\b|-Command\b)|"
    r"\bcmd(?:\.exe)?\s+/[ck]\b",
    re.IGNORECASE,
)

SHELL_FILE_MUTATION_RE = re.compile(
    r"(?:>>?|\b(?:tee|sed\s+-i|Set-Content|Add-Content|Out-File|New-Item|Remove-Item|"
    r"Copy-Item|Move-Item|Rename-Item|Clear-Content|rm|mv|cp|del|erase|ren|rename|"
    r"mkdir|rmdir|rd|touch|chmod|chown|ln)\b|"
    r"\bgit\s+(?:commit|reset|checkout|clean|rm|apply|mv|restore|am|push|tag)\b)",
    re.IGNORECASE,
)

EXTERNAL_ENV_PATH_RE = re.compile(
    r"(?:%(?:USERPROFILE|HOMEPATH|APPDATA|LOCALAPPDATA|TEMP|TMP|WINDIR|SYSTEMROOT|PROGRAMDATA)%|"
    r"\$env:(?:USERPROFILE|HOMEPATH|APPDATA|LOCALAPPDATA|TEMP|TMP|WINDIR|SYSTEMROOT)\b|"
    r"\$\{?(?:HOME|TMPDIR)\}?)",
    re.IGNORECASE,
)

WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")
POSIX_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")
DIRTY_ONEDRIVE_FRAGMENT = "onedrive\\documents\\anthropic\\introduction to mcp"


@dataclass(frozen=True)
class PathClassification:
    raw: str
    host_os: str
    syntax: str
    kind: str
    allowed: bool
    resolved: str | None
    reason: str


def _reject_dup_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    record: dict[str, Any] = {}
    for k, v in pairs:
        if k in record:
            raise ValueError(f"duplicate JSON key {k!r}")
        record[k] = v
    return record


def _load_capability_lease_module():
    lease_path = REPO_ROOT / "governance" / "kpgs-vnext" / "security" / "capability_lease.py"
    spec = importlib.util.spec_from_file_location("kpgs_capability_lease", lease_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load capability_lease.py from {lease_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _map_tool_capability(tool_name: str) -> str | None:
    if tool_name in TOOL_TO_CAPABILITY:
        return TOOL_TO_CAPABILITY[tool_name]
    if tool_name.startswith("mcp_"):
        return "mcp.invoke"
    if tool_name.startswith("browser_"):
        return "browser.interact"
    return None


def _extract_target_path(args: dict[str, Any]) -> str | None:
    for key in ("TargetFile", "Path", "file_path", "path", "Target"):
        val = args.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


def _is_dirty_onedrive(text: str) -> bool:
    return DIRTY_ONEDRIVE_FRAGMENT in text.replace("/", "\\").lower()


def _is_relative_posix(candidate: PurePosixPath, root: PurePosixPath) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def _is_relative_native(candidate: Path, root: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def _posix_norm(path_str: str) -> PurePosixPath:
    parts: list[str] = []
    for seg in PurePosixPath(path_str).parts:
        if seg in {"", "."}:
            continue
        if seg == "/":
            parts = ["/"]
            continue
        if seg == "..":
            if parts and parts[-1] != "/":
                parts.pop()
            continue
        parts.append(seg)
    if not parts:
        return PurePosixPath(".")
    if parts[0] == "/":
        return PurePosixPath("/" + "/".join(parts[1:]))
    return PurePosixPath("/".join(parts))


def _lexical_traversal_escapes(rel_text: str) -> bool:
    depth = 0
    for seg in re.split(r"[\\/]+", rel_text):
        if not seg or seg == ".":
            continue
        if seg == "..":
            depth -= 1
            if depth < 0:
                return True
        else:
            depth += 1
    return False


def _coerce_native_path(r: Path | PurePath | str) -> Path:
    return r if isinstance(r, Path) else Path(str(r))


def _is_pure_simulation(effective_os: str, paths: Sequence[Path | PurePath | str | None]) -> bool:
    return effective_os != os.name or any(
        isinstance(p, PurePath) and not isinstance(p, Path) for p in paths if p is not None
    )


def _win_norm(path_str: str) -> PureWindowsPath:
    p = PureWindowsPath(path_str.replace("/", "\\"))
    parts = list(p.parts)
    anchor = p.anchor
    body = parts[1:] if anchor and parts and parts[0] == anchor else parts
    stack: list[str] = []
    for seg in body:
        if seg in {"", "."}:
            continue
        if seg == "..":
            if stack:
                stack.pop()
            continue
        stack.append(seg)
    return PureWindowsPath(anchor, *stack) if anchor else (PureWindowsPath(*stack) if stack else PureWindowsPath("."))


def _is_relative_win(candidate: PureWindowsPath, root: PureWindowsPath) -> bool:
    try:
        c_low = PureWindowsPath(*(part.lower() for part in candidate.parts))
        r_low = PureWindowsPath(*(part.lower() for part in root.parts))
        c_low.relative_to(r_low)
        return True
    except ValueError:
        return False


def _detect_symlink_escape(candidate: Path, allowed_roots: Sequence[Path | PurePath | str]) -> str | None:
    """Return reason if any existing component along ``candidate`` is a symlink exiting roots."""
    resolved_roots = [_coerce_native_path(r).resolve() for r in allowed_roots]
    # Walk from top prefix down to candidate so intermediate directory symlinks are caught
    parts = candidate.parts
    for end in range(1, len(parts) + 1):
        prefix = Path(*parts[:end])
        try:
            if not os.path.lexists(prefix):
                break
            is_junction = hasattr(os.path, "isjunction") and os.path.isjunction(prefix)
            if os.path.islink(prefix) or prefix.is_symlink() or is_junction:
                link_resolved = prefix.resolve(strict=False)
                if not any(_is_relative_native(link_resolved, root) for root in resolved_roots):
                    return f"symlink component {prefix} resolves outside allowed roots -> {link_resolved}"
        except OSError as exc:
            return f"symlink inspection failed on {prefix}: {exc}"
    return None


def _default_allowed_roots(
    *,
    ctx: dict[str, Any] | None = None,
    repo_root: Path = REPO_ROOT,
) -> list[Path]:
    roots: list[Path] = [repo_root.resolve()]
    extra = os.environ.get("KPGS_ALLOWED_PATHS", "")
    ctx_paths = [
        str(p)
        for p in (ctx.get("allowed_paths", []) if isinstance(ctx, dict) else [])
        if isinstance(p, str) and p.strip()
    ]
    for raw in [p for p in extra.split(os.pathsep) if p.strip()] + ctx_paths:
        roots.append(Path(raw).resolve())
    return roots


def classify_target_path(
    raw_target: str,
    *,
    allowed_roots: Sequence[Path | PurePath | str],
    repo_root: Path | PurePath | str = REPO_ROOT,
    host_os: str | None = None,
    cwd: Path | PurePath | str | None = None,
) -> PathClassification:
    """Classify a target path under explicit Windows and POSIX semantics."""
    effective_os = host_os if host_os is not None else os.name
    target = raw_target.strip() if isinstance(raw_target, str) else ""
    pure_sim = _is_pure_simulation(effective_os, [*allowed_roots, repo_root, cwd])

    def _to_posix_root(r: Path | PurePath | str) -> PurePosixPath:
        if isinstance(r, PurePosixPath):
            return r
        if isinstance(r, str):
            return PurePosixPath(r.replace("\\", "/"))
        return PurePosixPath(r.as_posix())

    def _to_win_root(r: Path | PurePath | str) -> PureWindowsPath:
        if isinstance(r, PureWindowsPath):
            return r
        return _win_norm(str(r))

    if not target:
        return PathClassification(raw_target, effective_os, "empty", "invalid", False, None, "empty target path")
    if any(ord(ch) < 32 for ch in target):
        return PathClassification(raw_target, effective_os, "control", "invalid", False, None, "control character in path")
    if POSIX_SCHEME_RE.match(target):
        return PathClassification(raw_target, effective_os, "uri", "uri_denied", False, None, f"URI schemes prohibited: {target[:80]}")
    if _is_dirty_onedrive(target):
        return PathClassification(raw_target, effective_os, "onedrive", "dirty_onedrive", False, None, "dirty OneDrive checkout is prohibited")

    # 1. Extended / NT device paths (\\?\, \\.\, //?/, //./)
    if target.startswith(("\\\\?\\", "\\\\.\\", "//?/", "//./")):
        return PathClassification(
            raw_target,
            effective_os,
            "windows_device",
            "windows_device_namespace",
            False,
            None,
            "NT device and extended-length namespaces are prohibited",
        )

    # 2. UNC network paths (\\server\share or //server/share)
    if target.startswith(("\\\\", "//")):
        return PathClassification(
            raw_target,
            effective_os,
            "windows_unc",
            "windows_unc",
            False,
            None,
            "UNC network paths are prohibited",
        )

    # 3. Windows drive prefix (C:\..., C:/..., or drive-relative C:foo)
    if WINDOWS_DRIVE_RE.match(target):
        if effective_os != "nt":
            return PathClassification(
                raw_target,
                effective_os,
                "windows_drive",
                "windows_drive_on_posix",
                False,
                None,
                "Windows drive-letter paths are prohibited on POSIX hosts",
            )
        if len(target) < 3 or target[2] not in ("\\", "/"):
            return PathClassification(
                raw_target,
                effective_os,
                "windows_drive_relative",
                "windows_drive_relative",
                False,
                None,
                "ambiguous drive-relative Windows path is prohibited",
            )
        syntax = "windows_drive_absolute"
        if pure_sim:
            cand_win = _win_norm(target)
            if _is_dirty_onedrive(str(cand_win)):
                return PathClassification(raw_target, effective_os, syntax, "dirty_onedrive", False, str(cand_win), "dirty OneDrive checkout is prohibited")
            win_roots = [_to_win_root(r) for r in allowed_roots]
            allowed = any(_is_relative_win(cand_win, root) for root in win_roots)
            return PathClassification(
                raw_target,
                effective_os,
                syntax,
                syntax if allowed else "outside_allowed_roots",
                allowed,
                str(cand_win),
                "within allowed Windows roots" if allowed else f"outside allowed workspace roots: {cand_win}",
            )
        candidate = Path(PureWindowsPath(target))
    elif target.startswith("/"):
        if effective_os != "nt":
            syntax = "posix_absolute"
            if _lexical_traversal_escapes(target):
                # Still normalize from root; relative_to allowed_roots enforces boundary
                pass
            candidate_posix = _posix_norm(target)
            if _is_dirty_onedrive(str(candidate_posix)):
                return PathClassification(raw_target, effective_os, syntax, "dirty_onedrive", False, str(candidate_posix), "dirty OneDrive checkout is prohibited")
            if pure_sim:
                # Explicit/simulated POSIX evaluation (never mix PurePosixPath with Path.resolve())
                posix_roots = [_to_posix_root(r) for r in allowed_roots]
                allowed = any(_is_relative_posix(candidate_posix, root) for root in posix_roots)
                return PathClassification(
                    raw_target,
                    effective_os,
                    syntax,
                    "posix_absolute",
                    allowed,
                    str(candidate_posix),
                    "within allowed POSIX roots" if allowed else f"outside allowed workspace roots: {candidate_posix}",
                )
            candidate = Path(candidate_posix.as_posix())
        else:
            # Single leading '/' on Windows is current-drive-root relative (\foo) -> treat strictly
            syntax = "windows_root_relative_slash"
            candidate = Path(os.path.abspath(target))
    elif target.startswith("\\"):
        if effective_os != "nt":
            return PathClassification(
                raw_target,
                effective_os,
                "windows_backslash",
                "windows_root_on_posix",
                False,
                None,
                "leading backslash path is prohibited on POSIX hosts",
            )
        return PathClassification(
            raw_target,
            effective_os,
            "windows_root_relative",
            "windows_root_relative",
            False,
            None,
            "drive-ambiguous root-relative backslash path is prohibited",
        )
    else:
        # Relative path: check home expansion and lexical '..' escapes
        if target == "~" or target.startswith(("~/", "~\\")):
            return PathClassification(raw_target, effective_os, "home_relative", "home_escape", False, None, "home-directory paths are prohibited")
        syntax = "relative"
        norm_rel = target.replace("\\", "/")
        if effective_os != "nt" and pure_sim:
            anchor_posix = _to_posix_root(cwd if cwd is not None else repo_root)
            posix_roots = [_to_posix_root(r) for r in allowed_roots]
            if _lexical_traversal_escapes(norm_rel):
                joined = _posix_norm((anchor_posix / norm_rel).as_posix())
                if not any(_is_relative_posix(joined, root) for root in posix_roots):
                    return PathClassification(raw_target, effective_os, syntax, "relative_traversal", False, str(joined), f"relative traversal escapes workspace: {target}")
            joined = _posix_norm((anchor_posix / norm_rel).as_posix())
            allowed = any(_is_relative_posix(joined, root) for root in posix_roots)
            return PathClassification(
                raw_target,
                effective_os,
                syntax,
                "relative_inside" if allowed else "outside_allowed_roots",
                allowed,
                str(joined),
                "within allowed POSIX roots" if allowed else f"outside allowed workspace roots: {joined}",
            )
        if effective_os == "nt" and pure_sim:
            anchor_win = _to_win_root(cwd if cwd is not None else repo_root)
            win_roots = [_to_win_root(r) for r in allowed_roots]
            joined_win = _win_norm(str(anchor_win / target.replace("/", "\\")))
            if _is_dirty_onedrive(str(joined_win)):
                return PathClassification(raw_target, effective_os, syntax, "dirty_onedrive", False, str(joined_win), "dirty OneDrive checkout is prohibited")
            if _lexical_traversal_escapes(target) and not any(_is_relative_win(joined_win, root) for root in win_roots):
                return PathClassification(raw_target, effective_os, syntax, "relative_traversal", False, str(joined_win), f"relative traversal escapes workspace: {target}")
            allowed = any(_is_relative_win(joined_win, root) for root in win_roots)
            return PathClassification(
                raw_target,
                effective_os,
                syntax,
                "relative_inside" if allowed else "outside_allowed_roots",
                allowed,
                str(joined_win),
                "within allowed Windows roots" if allowed else f"outside allowed workspace roots: {joined_win}",
            )
        anchor = (_coerce_native_path(cwd).resolve() if cwd is not None else _coerce_native_path(repo_root).resolve())
        candidate = Path(os.path.abspath(anchor / norm_rel))

    # Native filesystem checks (symlink escape, realpath, dirty OneDrive, allowed_roots)
    symlink_err = _detect_symlink_escape(candidate, allowed_roots)
    if symlink_err:
        return PathClassification(raw_target, effective_os, syntax, "symlink_escape", False, None, symlink_err)

    try:
        resolved = candidate.resolve(strict=False)
    except (OSError, ValueError) as exc:
        return PathClassification(raw_target, effective_os, syntax, "unresolvable", False, None, f"path resolution failed: {exc}")

    if _is_dirty_onedrive(str(resolved)):
        return PathClassification(raw_target, effective_os, syntax, "dirty_onedrive", False, str(resolved), "resolved path hits dirty OneDrive checkout")

    resolved_roots = [_coerce_native_path(r).resolve() for r in allowed_roots]
    if not any(_is_relative_native(resolved, root) for root in resolved_roots):
        kind = "relative_traversal" if (syntax == "relative" and _lexical_traversal_escapes(target)) else "outside_allowed_roots"
        return PathClassification(raw_target, effective_os, syntax, kind, False, str(resolved), f"target resolves outside allowed roots: {resolved}")

    return PathClassification(raw_target, effective_os, syntax, syntax, True, str(resolved), "within allowed workspace boundaries")


def _extract_command_paths(command_text: str) -> list[str]:
    """Extract candidate filesystem paths and redirection targets from shell commands."""
    candidates: list[str] = []
    # Redirection targets: > file or >> file
    for match in re.finditer(r"(?:^|[^0-9A-Za-z_])(?:\d*>>?|<)\s*(\"[^\"]+\"|'[^']+'|[^\s;|&]+)", command_text):
        candidates.append(match.group(1).strip("\"'"))

    # Tokenize safely (posix=False preserves Windows backslashes across platforms)
    try:
        tokens = shlex.split(command_text, posix=False)
    except ValueError:
        tokens = command_text.split()

    for raw_tok in tokens:
        tok = raw_tok.strip().strip("\"'")
        if not tok:
            continue
        if tok.startswith(("http://", "https://")):
            continue
        # Strip --flag=value prefix
        if tok.startswith("-") and "=" in tok:
            _, val = tok.split("=", 1)
            tok = val.strip().strip("\"'")
            if not tok:
                continue
        # Skip single-token CLI options (-q, --event, /s on Windows unless multi-segment /etc/passwd)
        if tok.startswith("-"):
            continue
        if POSIX_SCHEME_RE.match(tok):
            candidates.append(tok)
            continue
        if WINDOWS_DRIVE_RE.match(tok) or tok.startswith(("\\\\", "//", "/", "\\", "~", "../", "..\\")):
            # Ignore short MS-DOS switches like /c, /f, /q, /s when only 2 chars
            if len(tok) <= 3 and tok.startswith("/") and "/" not in tok[1:]:
                continue
            candidates.append(tok)
            continue
        if tok == ".." or "/.." in tok or "\\.." in tok or tok.endswith(("/..", "\\..")):
            candidates.append(tok)
            continue
        if "/" in tok or "\\" in tok:
            candidates.append(tok)

    # Also catch unseparated Windows drive/UNC/POSIX patterns embedded inside code or args
    for pat in (
        r"[A-Za-z]:[\\/][^\s\"'`;|&)]+",
        r"\\\\[^\s\"'`;|&)]+",
        r"//[^\s\"'`;|&)]+",
    ):
        for match in re.finditer(pat, command_text):
            candidates.append(match.group(0))

    # Deduplicate preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for item in candidates:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def _paths_overlap_writable(protected_path: Path, writable_roots: Sequence[Path]) -> bool:
    """Return True if protected_path resides inside any renter-writable root or symlink-aliases it."""
    if os.path.islink(protected_path) or protected_path.is_symlink():
        return True
    try:
        resolved = protected_path.resolve()
    except (OSError, ValueError):
        return True
    for root in writable_roots:
        r = root.resolve()
        if _is_relative_native(resolved, r) or _is_relative_native(r, resolved):
            return True
    return False


def _load_trusted_context(repo_root: Path = REPO_ROOT) -> tuple[dict[str, Any] | None, str | None]:
    """Load and validate non-renter-modifiable hook context with Ed25519 public keys ONLY."""
    if any(os.environ.get(var_name) for var_name in FORBIDDEN_SIGNING_ENV_VARS):
        return None, "HOLD: reusable signing authority env var is prohibited"

    ctx_file = os.environ.get("KPGS_HOOK_CONTEXT_FILE", "").strip()
    if not ctx_file:
        return None, "HOLD: missing trusted lease context (KPGS_HOOK_CONTEXT_FILE unset)"

    ctx_path = Path(ctx_file)
    if os.path.islink(ctx_path) or ctx_path.is_symlink():
        return None, "HOLD: symlinked hook context file is prohibited"
    if not ctx_path.is_file():
        return None, "HOLD: trusted lease context file missing"

    try:
        raw_text = ctx_path.read_text(encoding="utf-8")
        ctx = json.loads(raw_text, object_pairs_hook=_reject_dup_keys)
    except Exception:
        return None, "HOLD: invalid hook context JSON"

    if not isinstance(ctx, dict):
        return None, "HOLD: hook context must be a JSON object"

    # Reject any reusable signing authority in context
    if any(field_name in ctx and ctx[field_name] for field_name in FORBIDDEN_SIGNING_CONTEXT_KEYS):
        return None, "HOLD: reusable signing authority must not be stored in hook context"

    writable_roots = _default_allowed_roots(ctx=ctx, repo_root=repo_root)
    if _paths_overlap_writable(ctx_path, writable_roots):
        return None, "HOLD: hook context file must not reside inside renter-modifiable workspace"

    pub_keys_hex: dict[str, str] | None = None
    pub_keys_file = os.environ.get("KPGS_TRUSTED_PUBLIC_KEYS_FILE", "").strip() or str(ctx.get("public_keys_file", "")).strip()
    if pub_keys_file:
        pk_path = Path(pub_keys_file)
        if os.path.islink(pk_path) or pk_path.is_symlink() or not pk_path.is_file():
            return None, "HOLD: trusted public keys file missing or symlinked"
        if _paths_overlap_writable(pk_path, writable_roots):
            return None, "HOLD: trusted public keys file must not reside inside renter-modifiable workspace"
        try:
            pk_obj = json.loads(pk_path.read_text(encoding="utf-8"), object_pairs_hook=_reject_dup_keys)
        except Exception:
            return None, "HOLD: invalid trusted public keys file"
        if not isinstance(pk_obj, dict) or not pk_obj:
            return None, "HOLD: trusted public keys file must map kid -> hex key"
        pub_keys_hex = {str(k): str(v) for k, v in pk_obj.items()}
    elif isinstance(ctx.get("public_keys_hex"), dict) and ctx["public_keys_hex"]:
        pub_keys_hex = {str(k): str(v) for k, v in ctx["public_keys_hex"].items()}

    if not pub_keys_hex:
        return None, "HOLD: hook context missing Ed25519 verifying keys (public_keys_hex/public_keys_file)"

    ledger_raw = os.environ.get("KPGS_RESTRICTION_LEDGER", "").strip() or str(ctx.get("restriction_ledger_path", "")).strip()
    if ledger_raw:
        ledger_path = Path(ledger_raw)
        if os.path.islink(ledger_path) or ledger_path.is_symlink():
            return None, "HOLD: symlinked restriction ledger path is prohibited"
        if _paths_overlap_writable(ledger_path, writable_roots):
            return None, "HOLD: restriction ledger must not reside inside renter-modifiable workspace"

    return {
        "ctx": ctx,
        "ctx_path": ctx_path,
        "pub_keys_hex": pub_keys_hex,
        "ledger_path": ledger_raw or None,
        "writable_roots": writable_roots,
    }, None


def _authorize_capabilities(
    loaded_ctx: dict[str, Any],
    capabilities: Sequence[str],
    payload: dict[str, Any],
    tool_name: str,
) -> str | None:
    """Verify EdDSA lease and restriction ledger using public keys ONLY (returns deny reason or None)."""
    ctx = loaded_ctx["ctx"]
    pub_keys_hex: dict[str, str] = loaded_ctx["pub_keys_hex"]
    ledger_path = loaded_ctx["ledger_path"]
    try:
        lease_mod = _load_capability_lease_module()
        public_keys = {kid: bytes.fromhex(val) for kid, val in pub_keys_hex.items()}
        ring = lease_mod.Ed25519PublicKeyRing(public_keys)
        authority = lease_mod.CapabilityLeaseAuthority(
            ring,
            restriction_ledger_path=ledger_path,
            restriction_public_keys=public_keys if ledger_path else None,
        )
        step_idx = payload.get("stepIdx", 0)
        conv_id = str(payload.get("conversationId", "conv_default"))
        for cap in capabilities:
            op_nonce = f"nonce_{conv_id}_{step_idx}_{tool_name}_{cap}"
            authority.authorize(
                str(ctx["lease_token"]),
                tenant_id=str(ctx["tenant_id"]),
                domain_id=str(ctx["domain_id"]),
                task_id=str(ctx["task_id"]),
                capability=cap,
                resource_scope=str(ctx["resource_scope"]),
                operation_nonce=op_nonce,
                correlation_id=f"corr:{conv_id}:{step_idx}",
            )
        return None
    except Exception:
        return f"HOLD: pre-tool lease/restriction gate denied {tool_name!r}"


def _deny(reason: str) -> dict[str, Any]:
    return {
        "decision": "deny",
        "permissionDecision": "deny",
        "reason": reason,
    }


def _allow(reason: str) -> dict[str, Any]:
    return {
        "decision": "allow",
        "permissionDecision": "allow",
        "reason": reason,
    }


def handle_session_start(payload: dict[str, Any]) -> dict[str, Any]:
    now_path = REPO_ROOT / "NOW.md"
    now_status = "PRESENT" if now_path.is_file() else "MISSING"
    _, ctx_err = _load_trusted_context()
    lease_status = "VALIDATED_CONTEXT" if ctx_err is None else "UNADMITTED"
    context = (
        "[KPGS_SESSION_START] I_AM_STATELESS_RENTER_NOT_LANDLORD | "
        f"repo_root={REPO_ROOT} | NOW.md={now_status} | "
        f"lease_context={lease_status} | "
        "PreToolUse cross-platform boundary & Ed25519 verifier gate active."
    )
    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }


def handle_pre_tool_use(payload: dict[str, Any]) -> dict[str, Any]:
    tool_call = payload.get("toolCall") if isinstance(payload.get("toolCall"), dict) else {}
    tool_name = str(tool_call.get("name", "")).strip()
    tool_args = tool_call.get("args") if isinstance(tool_call.get("args"), dict) else {}

    if not tool_name:
        return _deny("HOLD: missing toolCall.name in PreToolUse payload")

    if tool_name in READ_ONLY_TOOLS:
        return _allow(f"Read-only tool {tool_name!r} permitted")

    capability = _map_tool_capability(tool_name)
    if capability is None:
        return _deny(f"HOLD: CX_UNKNOWN unmapped tool {tool_name!r} denied by fail-closed policy")

    # Fail-closed: missing or untrusted lease context MUST deny all mutating operations
    loaded_ctx, ctx_err = _load_trusted_context()
    if ctx_err or loaded_ctx is None:
        return _deny(ctx_err or "HOLD: missing trusted lease context")

    allowed_roots: list[Path] = loaded_ctx["writable_roots"]
    required_capabilities: list[str] = [capability]

    # Enforce filesystem boundary on write/edit/delete tools
    if capability == "repo.file.write":
        target_path = _extract_target_path(tool_args)
        if not target_path:
            return _deny(f"HOLD: write tool {tool_name!r} has no resolvable target path (fail-closed)")
        classification = classify_target_path(target_path, allowed_roots=allowed_roots, repo_root=REPO_ROOT)
        if not classification.allowed:
            return _deny(
                f"HOLD: write tool {tool_name!r} blocked ({classification.kind}): {classification.reason}"
            )

    # Prevent run_command & equivalent execution tools from circumventing filesystem/capability bounds
    if capability == "command.execute":
        raw_cwd = tool_args.get("Cwd") or tool_args.get("cwd") or tool_args.get("WorkingDirectory")
        cmd_cwd: Path | None = None
        if isinstance(raw_cwd, str) and raw_cwd.strip():
            cwd_check = classify_target_path(raw_cwd.strip(), allowed_roots=allowed_roots, repo_root=REPO_ROOT)
            if not cwd_check.allowed or not cwd_check.resolved:
                return _deny(f"HOLD: execution Cwd blocked ({cwd_check.kind}): {cwd_check.reason}")
            cmd_cwd = Path(cwd_check.resolved)

        if tool_name == "schedule" and tool_args.get("IsDaemon"):
            required_capabilities.append("schedule.daemon")

        cmd_text = str(
            tool_args.get("CommandLine")
            or tool_args.get("command")
            or tool_args.get("Input")
            or (tool_args.get("Prompt") if tool_name == "schedule" else "")
            or ""
        )
        if DESTRUCTIVE_CMD_RE.search(cmd_text):
            return _deny(f"HOLD: destructive command blocked by PreToolUse gate: {cmd_text[:80]}")
        if OBFUSCATED_EXEC_RE.search(cmd_text):
            return _deny(f"HOLD: obfuscated or subshell command blocked by PreToolUse gate: {cmd_text[:80]}")
        if INLINE_INTERPRETER_RE.search(cmd_text):
            return _deny(f"HOLD: inline interpreter/subshell blocked from bypassing path & capability checks: {cmd_text[:80]}")
        if EXTERNAL_ENV_PATH_RE.search(cmd_text):
            return _deny("HOLD: external environment path reference blocked by PreToolUse gate")
        if _is_dirty_onedrive(cmd_text):
            return _deny("HOLD: command referencing dirty OneDrive checkout is prohibited")
        if str(loaded_ctx["ctx_path"].name) in cmd_text or (
            loaded_ctx["ledger_path"] and str(Path(loaded_ctx["ledger_path"]).name) in cmd_text
        ):
            return _deny("HOLD: command referencing hook context or restriction ledger is prohibited")

        for extracted in _extract_command_paths(cmd_text):
            pcheck = classify_target_path(
                extracted,
                allowed_roots=allowed_roots,
                repo_root=REPO_ROOT,
                cwd=cmd_cwd,
            )
            if not pcheck.allowed:
                return _deny(
                    f"HOLD: command path {extracted!r} blocked ({pcheck.kind}): {pcheck.reason}"
                )

        if SHELL_FILE_MUTATION_RE.search(cmd_text):
            required_capabilities.append("repo.file.write")

    deny_reason = _authorize_capabilities(loaded_ctx, required_capabilities, payload, tool_name)
    if deny_reason:
        return _deny(deny_reason)

    return _allow(f"Admitted {tool_name!r} for capabilities {required_capabilities!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", required=True, choices=("session-start", "pre-tool-use"))
    args = parser.parse_args()

    raw = sys.stdin.read().strip()
    payload: dict[str, Any] = {}
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                payload = parsed
        except json.JSONDecodeError:
            if args.event == "pre-tool-use":
                print(json.dumps(_deny("HOLD: malformed JSON on PreToolUse stdin")))
                return 0

    if args.event == "session-start":
        out = handle_session_start(payload)
    else:
        out = handle_pre_tool_use(payload)

    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
