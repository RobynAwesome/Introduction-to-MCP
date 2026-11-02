import assert from "node:assert/strict";
import { spawn, spawnSync } from "node:child_process";
import { once } from "node:events";
import { mkdtemp, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { createInterface } from "node:readline";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

test("the approval CLI refuses a non-interactive caller", () => {
  const result = spawnSync(process.execPath, [fileURLToPath(new URL("./approve.js", import.meta.url)),
    "BRA-00000000-0000-0000-0000-000000000001"], { encoding: "utf8", timeout: 5_000 });
  assert.equal(result.status, 3);
  assert.match(result.stderr, /interactive local terminal \(TTY\)/);
});

test("real stdio discovery survives missing CDP and denies execution without a stage", { timeout: 15_000 }, async () => {
  const directory = await mkdtemp(path.join(os.tmpdir(), "kpgs-mcp-wire-"));
  const child = spawn(process.execPath, [fileURLToPath(new URL("./server.js", import.meta.url))], {
    env: { ...process.env, KPGS_BROWSER_LEDGER_DIR: directory, KPGS_CHROME_DEBUG_URL: "http://127.0.0.1:1" },
    stdio: ["pipe", "pipe", "pipe"],
  });
  const lines = createInterface({ input: child.stdout });
  let nextId = 0;
  const pending = new Map<number, { resolve: (value: any) => void; reject: (error: Error) => void }>();
  let stderr = "";
  child.stderr.on("data", (data) => { stderr += data; });
  lines.on("line", (line) => {
    const message = JSON.parse(line);
    const waiting = pending.get(message.id);
    if (waiting) { pending.delete(message.id); waiting.resolve(message); }
  });
  child.on("exit", () => {
    for (const request of pending.values()) request.reject(new Error(`Server exited: ${stderr}`));
    pending.clear();
  });
  function request(method: string, params: Record<string, unknown> = {}): Promise<any> {
    const id = ++nextId;
    return new Promise((resolve, reject) => {
      pending.set(id, { resolve, reject });
      child.stdin.write(`${JSON.stringify({ jsonrpc: "2.0", id, method, params })}\n`);
    });
  }
  try {
    const initialized = await request("initialize", {
      protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "kpgs-wire-proof", version: "1.0.0" },
    });
    assert.equal(initialized.result.serverInfo.name, "kpgs-browser-mcp");
    child.stdin.write(`${JSON.stringify({ jsonrpc: "2.0", method: "notifications/initialized" })}\n`);
    const tools = await request("tools/list");
    assert.deepEqual(tools.result.tools.map((tool: { name: string }) => tool.name).sort(), [
      "browser_status", "execute_staged_interaction", "list_pages", "navigate_page", "read_page", "stage_interaction", "verify_receipt",
    ]);
    const denied = await request("tools/call", {
      name: "execute_staged_interaction", arguments: { actionId: "BRA-00000000-0000-0000-0000-000000000001" },
    });
    assert.equal(JSON.parse(denied.result.content[0].text).reason, "STAGED_ACTION_NOT_FOUND");
    const unavailable = await request("tools/call", { name: "browser_status", arguments: {} });
    assert.equal(unavailable.result.isError, true, "Missing CDP must not report a successful connection");
    const stillAlive = await request("tools/list");
    assert.equal(stillAlive.result.tools.length, 7);
  } finally {
    if (child.exitCode === null && child.signalCode === null) {
      const exited = once(child, "exit");
      child.kill();
      await exited;
    }
    lines.close();
    await rm(directory, { recursive: true, force: true });
  }
});
