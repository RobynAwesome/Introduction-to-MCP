import assert from "node:assert/strict";
import { createServer } from "node:http";
import test from "node:test";
import { requestKcReply, parseKcChatReply } from "../.proof/kc-chat.js";

const identity = "GUEST_SEEKER";
const receipt = {
  assert_id: "AST-SYNTHETIC", session_id: "fixture", rtc_identity: identity,
  intent_domain: "FIXTURE_ONLY", claim: "Synthetic response record; no action executed",
  residency: "UNKNOWN", proof_hash: "a".repeat(64), status: "VERIFIED_ON_LEDGER",
  timestamp: "2026-10-28T00:00:00Z",
};

test("real HTTP request preserves message/persona and accepts a reply without inventing a receipt", async (t) => {
  const server = createServer(async (req, res) => {
    let body = "";
    for await (const chunk of req) body += chunk;
    assert.equal(req.url, "/api/kc/chat");
    assert.equal(req.method, "POST");
    assert.deepEqual(JSON.parse(body), { message: "Synthetic request", rtc_identity: identity });
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify({ reply: "Synthetic reply" }));
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  t.after(() => { server.closeAllConnections(); server.close(); });
  const base = `http://127.0.0.1:${server.address().port}`;
  const reply = await requestKcReply("Synthetic request", identity, (url, init) => fetch(base + url, init));
  assert.equal(reply.reply, "Synthetic reply");
  assert.equal(reply.receipt, null);
  assert.deepEqual(reply.suggestedActions, []);
});

for (const status of [401, 404, 500]) {
  test(`HTTP ${status} is an error, never a canned success`, async () => {
    await assert.rejects(requestKcReply("Keep my draft", identity, async () => new Response("Unavailable", { status })),
      { reason: "unavailable" });
  });
}

test("offline, aborted, HTML and malformed response paths fail explicitly", async () => {
  await assert.rejects(requestKcReply("draft", identity, async () => { throw new TypeError("Network down"); }), { reason: "unavailable" });
  await assert.rejects(requestKcReply("draft", identity, async () => new Response("<html>SPA fallback</html>")), { reason: "invalid-response" });
  for (const value of [null, [], {}, { reply: null }, { reply: 2 }, { reply: "   " }]) {
    assert.throws(() => parseKcChatReply(value, identity), { reason: "invalid-response" });
  }
  await assert.rejects(requestKcReply("draft", identity, async () => { throw new DOMException("aborted", "AbortError"); },
    AbortSignal.abort()), { reason: "timeout" });
});

test("receipt shape is evidence only; missing, malformed or mismatched receipts are not retained", () => {
  const parsed = parseKcChatReply({ reply: "fixture", assert_receipt: receipt, suggested_actions: ["Next", 42, null, ""] }, identity);
  assert.equal(parsed.receipt.status, "VERIFIED_ON_LEDGER", "Backend label stays a reported field, not client verification");
  assert.deepEqual(parsed.suggestedActions, ["Next"]);
  for (const invalid of [null, {}, { ...receipt, proof_hash: "wrong" }, { ...receipt, timestamp: "invalid" },
    { ...receipt, rtc_identity: "OPERATOR_SOVEREIGN" }, { ...receipt, claim: 10 }]) {
    assert.equal(parseKcChatReply({ reply: "still usable", assert_receipt: invalid }, identity).receipt, null);
  }
  assert.equal(parseKcChatReply({ reply: "next response has no receipt" }, identity).receipt, null);
});
