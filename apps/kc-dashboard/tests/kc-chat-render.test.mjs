import assert from "node:assert/strict";
import test from "node:test";
import { fileURLToPath } from "node:url";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { createServer } from "vite";

test("rendered dashboard starts without fabricated proof and treats returned status as unverified", async () => {
  const vite = await createServer({
    configFile: fileURLToPath(new URL("../vite.config.ts", import.meta.url)),
    server: { middlewareMode: true }, appType: "custom", logLevel: "error",
  });
  try {
    const { KCMyBoyHero } = await vite.ssrLoadModule("/src/components/KCMyBoyHero.tsx");
    const initial = renderToStaticMarkup(React.createElement(KCMyBoyHero));
    assert.match(initial, /aria-label="Message to KC"/);
    assert.doesNotMatch(initial, /AST-8F2B10A4|VERIFIED_ON_LEDGER|Kopano Ledger|ZA-CPT/);
    const { default: EverydayMode } = await vite.ssrLoadModule("/src/EverydayMode.tsx");
    const everyday = renderToStaticMarkup(React.createElement(EverydayMode, {
      attentionItems: [], snapshotLabel: "synthetic snapshot", onOpenOperatorMode: () => {},
    }));
    assert.match(everyday, /Device connection available/);
    assert.match(everyday, /Live service status has not been checked/);
    assert.match(everyday, /Live service status<\/span><strong>Not checked/);
    assert.doesNotMatch(everyday, /Up to date/);
    const { KopanoAssertStamp } = await vite.ssrLoadModule("/src/components/KopanoAssertStamp.tsx");
    const reported = renderToStaticMarkup(React.createElement(KopanoAssertStamp, { receipt: {
      assert_id: "AST-SYNTHETIC", session_id: "fixture", rtc_identity: "GUEST_SEEKER",
      intent_domain: "FIXTURE_ONLY", claim: "Synthetic test claim", residency: "ZA-CPT",
      proof_hash: "a".repeat(64), status: "VERIFIED_ON_LEDGER", timestamp: "2026-10-28T00:00:00Z",
    } }));
    assert.match(reported, /Verification pending/);
    assert.match(reported, /Returned receipt/);
    assert.match(reported, /aria-expanded="false"/);
    assert.doesNotMatch(reported, /Kopano Ledger|VERIFIED_ON_LEDGER|ZA-CPT/);
  } finally {
    await vite.close();
  }
});
