#!/usr/bin/env python3
"""Antigravity SessionStart and PreToolUse enforcement gate for KPGS stateless renters.

Complies with Google Antigravity's documented hooks specification (camelCase stdin/stdout)
and passes scripts/audit_pretooluse_spawn_contract.py (ACTIVE_COUNT 0).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
KOPANO_CORE = REPO_ROOT / "kopano-core"
if str(KOPANO_CORE) not in sys.path:
    sys.path.insert(0, str(KOPANO_CORE))

READ_ONLY_TOOLS = {
    "read_file",
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

DESTRUCTIVE_CMD_RE = re.compile(
    r"\b(git\s+push\s+--force|git\s+reset\s+--hard|Remove-Item\s+.*-Recurse.*OneDrive)\b",
    re.IGNORECASE,
)


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


def handle_session_start(payload: dict[str, Any]) -> dict[str, Any]:
    now_path = REPO_ROOT / "NOW.md"
    now_status = "PRESENT" if now_path.is_file() else "MISSING"
    context = (
        "[KPGS_SESSION_START] I_AM_STATELESS_RENTER_NOT_LANDLORD | "
        f"repo_root={REPO_ROOT} | NOW.md={now_status} | "
        "PreToolUse lease & tamper-evident restriction enforcement active."
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
        return {"decision": "deny", "reason": "HOLD: missing toolCall.name in PreToolUse payload"}

    if tool_name in READ_ONLY_TOOLS:
        return {"decision": "allow", "reason": f"Read-only tool {tool_name!r} permitted"}

    capability = _map_tool_capability(tool_name)
    if capability is None:
        return {
            "decision": "deny",
            "reason": f"HOLD: CX_UNKNOWN unmapped tool {tool_name!r} denied by fail-closed policy",
        }

    # Block destructive shell commands or mutations targeting the dirty OneDrive checkout
    if capability == "command.execute":
        cmd_line = str(tool_args.get("CommandLine") or tool_args.get("command") or "")
        if DESTRUCTIVE_CMD_RE.search(cmd_line):
            return {
                "decision": "deny",
                "reason": f"HOLD: destructive command blocked by PreToolUse gate: {cmd_line[:80]}",
            }
        if "OneDrive\\Documents\\Anthropic\\Introduction to MCP" in cmd_line or "OneDrive/Documents/Anthropic/Introduction to MCP" in cmd_line:
            if any(tok in cmd_line for tok in ("git commit", "git reset", "git checkout", "Set-Content", "Out-File", "Remove-Item")):
                return {
                    "decision": "deny",
                    "reason": "HOLD: mutation of dirty Local OneDrive checkout is prohibited",
                }

    if capability == "repo.file.write":
        target_path = _extract_target_path(tool_args)
        if target_path:
            norm_target = target_path.replace("/", "\\").lower()
            if "onedrive\\documents\\anthropic\\introduction to mcp" in norm_target:
                return {
                    "decision": "deny",
                    "reason": f"HOLD: write tool {tool_name!r} targeting dirty OneDrive checkout is prohibited",
                }

    # Verify lease & tamper-evident restriction ledger when configured via environment or context file
    ctx_file = os.environ.get("KPGS_HOOK_CONTEXT_FILE")
    if ctx_file:
        ctx_path = Path(ctx_file)
        if not ctx_path.is_file():
            return {"decision": "deny", "reason": f"HOLD: KPGS_HOOK_CONTEXT_FILE {ctx_file!r} missing"}
        try:
            ctx = json.loads(ctx_path.read_text(encoding="utf-8"))
            lease_mod = _load_capability_lease_module()
            key_hex = str(ctx["hmac_key_hex"])
            key_id = str(ctx.get("key_id", "k1"))
            key_ring = lease_mod.KeyRing({key_id: bytes.fromhex(key_hex)}, active_key_id=key_id)
            authority = lease_mod.CapabilityLeaseAuthority(
                key_ring,
                restriction_ledger_path=ctx.get("restriction_ledger_path"),
                restriction_hmac_key=bytes.fromhex(key_hex),
            )
            step_idx = payload.get("stepIdx", 0)
            conv_id = str(payload.get("conversationId", "conv_default"))
            op_nonce = f"nonce_{conv_id}_{step_idx}_{tool_name}"
            authority.authorize(
                str(ctx["lease_token"]),
                tenant_id=str(ctx["tenant_id"]),
                domain_id=str(ctx["domain_id"]),
                task_id=str(ctx["task_id"]),
                capability=capability,
                resource_scope=str(ctx["resource_scope"]),
                operation_nonce=op_nonce,
                correlation_id=f"corr:{conv_id}:{step_idx}",
            )
        except Exception as exc:
            return {
                "decision": "deny",
                "reason": f"HOLD: pre-tool lease/restriction gate denied {tool_name!r}: {type(exc).__name__}: {exc}",
            }

    return {
        "decision": "allow",
        "reason": f"Admitted {tool_name!r} for capability {capability!r}",
    }


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
                print(json.dumps({"decision": "deny", "reason": "HOLD: malformed JSON on PreToolUse stdin"}))
                return 0

    if args.event == "session-start":
        out = handle_session_start(payload)
    else:
        out = handle_pre_tool_use(payload)

    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
