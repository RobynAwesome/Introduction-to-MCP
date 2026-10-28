import assert from "node:assert/strict";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test, { after } from "node:test";
import {
  POLICY_VERSION,
  buildReceipt,
  sha256Binding,
  stageBrowserAction,
  type BrowserElementContext,
  type BrowserPageContext,
  type HumanApproval
} from "./governance.js";
const temporaryLedger = await mkdtemp(path.join(os.tmpdir(), "kpgs-browser-ledger-test-"));
process.env.KPGS_BROWSER_LEDGER_DIR = temporaryLedger;
const {
  archiveStagedAction,
  claimApproval,
  finalizeApprovalConsumption,
  ledgerRoot,
  quarantineStagedAction,
  readHumanApproval,
  readReceipt,
  readReceiptHead,
  readStagedAction,
  writeHumanApproval,
  writeReceipt,
  writeStagedAction
} = await import("./ledger.js");
after(() => rm(temporaryLedger, { recursive: true, force: true }));

function element(
  selector = "#save",
  overrides: Partial<Omit<BrowserElementContext, "selector" | "fingerprint">> = {}
): BrowserElementContext {
  const basis = {
    selector,
    tagName: "button",
    inputType: null,
    autocomplete: null,
    name: null,
    id: "save",
    role: null,
    formAction: null,
    href: null,
    textDigest: sha256Binding("Save"),
    ...overrides
  };
  return { ...basis, fingerprint: sha256Binding(basis) };
}

function context(overrides: Partial<BrowserPageContext> = {}): BrowserPageContext {
  return {
    pageIndex: 0,
    targetId: "target-ledger-test",
    url: "https://example.com/settings",
    origin: "https://example.com",
    title: "Settings",
    element: element(),
    ...overrides
  };
}

test("approval is atomically claimable only once", async () => {
  await rm(ledgerRoot(), { recursive: true, force: true });
  const now = new Date();
  const staged = stageBrowserAction({ pageIndex: 0, operation: "click", selector: "#save" }, context(), now);
  const approval: HumanApproval = {
    actionId: staged.actionId,
    binding: staged.binding,
    policyVersion: POLICY_VERSION,
    approvedAt: new Date(now.getTime() + 1).toISOString(),
    approvedBy: "LOCAL_HUMAN"
  };

  await writeStagedAction(staged);
  await writeHumanApproval(approval);
  assert.deepEqual(await readHumanApproval(staged.actionId), approval);

  assert.deepEqual(await claimApproval(staged.actionId), approval);
  assert.equal(await claimApproval(staged.actionId), undefined);
  assert.equal(await readHumanApproval(staged.actionId), undefined);

  await finalizeApprovalConsumption(staged.actionId);
  assert.equal(await claimApproval(staged.actionId), undefined);
  await rm(ledgerRoot(), { recursive: true, force: true });
});

test("successful archive scrubs typed plaintext from pending and archived evidence", async () => {
  await rm(ledgerRoot(), { recursive: true, force: true });
  const secret = "local-only typed payload";
  const selector = "#note";
  const staged = stageBrowserAction(
    { pageIndex: 0, operation: "type", selector, value: secret },
    context({
      element: element(selector, {
        tagName: "textarea",
        inputType: null,
        autocomplete: "off",
        id: "note",
        textDigest: null
      })
    })
  );

  await writeStagedAction(staged);
  assert.equal((await readStagedAction(staged.actionId))?.value, secret);
  await archiveStagedAction(staged.actionId, "EXECUTED");
  assert.equal(await readStagedAction(staged.actionId), undefined);

  const archived = await readFile(path.join(ledgerRoot(), "archived", `${staged.actionId}.json`), "utf8");
  assert.equal(archived.includes(secret), false);
  assert.equal(archived.includes(sha256Binding(secret)), true);
  await rm(ledgerRoot(), { recursive: true, force: true });
});

test("indeterminate action is quarantined locally and explicitly non-replayable", async () => {
  await rm(ledgerRoot(), { recursive: true, force: true });
  const secret = "forensic payload retained locally";
  const selector = "#note";
  const staged = stageBrowserAction(
    { pageIndex: 0, operation: "type", selector, value: secret },
    context({
      element: element(selector, {
        tagName: "textarea",
        inputType: null,
        autocomplete: "off",
        id: "note",
        textDigest: null
      })
    })
  );

  await writeStagedAction(staged);
  await quarantineStagedAction(staged.actionId, "EXECUTION_ERROR_AFTER_APPROVAL_CLAIM");
  assert.equal(await readStagedAction(staged.actionId), undefined);

  const quarantined = await readFile(path.join(ledgerRoot(), "quarantined", `${staged.actionId}.json`), "utf8");
  const metadata = JSON.parse(
    await readFile(path.join(ledgerRoot(), "quarantined", `${staged.actionId}.meta.json`), "utf8")
  ) as Record<string, unknown>;
  assert.equal(quarantined.includes(secret), true);
  assert.equal(metadata.replayAllowed, false);
  assert.equal(metadata.humanReviewRequired, true);
  await rm(ledgerRoot(), { recursive: true, force: true });
});

test("receipt hash and chain head persist together", async () => {
  await rm(ledgerRoot(), { recursive: true, force: true });
  const page = context();
  const receipt = buildReceipt({
    receiptId: "RCP-00000000-0000-0000-0000-000000000010",
    actionId: "BRA-00000000-0000-0000-0000-000000000010",
    binding: "b".repeat(64),
    policyVersion: POLICY_VERSION,
    operation: "click",
    pageIndex: 0,
    executedAt: "2026-09-03T16:30:00.000Z",
    pageBefore: page,
    pageAfter: { ...page, element: null },
    result: { operation: "click", selector: "#save" },
    previousReceiptHash: null
  });

  await writeReceipt(receipt);
  assert.deepEqual(await readReceipt(receipt.receiptId), receipt);
  assert.deepEqual(await readReceiptHead(), { receiptId: receipt.receiptId, receiptHash: receipt.receiptHash });
  await rm(ledgerRoot(), { recursive: true, force: true });
});

test("claimed and consumed actions cannot be re-approved under the same action id", async () => {
  await rm(ledgerRoot(), { recursive: true, force: true });
  const staged = stageBrowserAction({ pageIndex: 0, operation: "click", selector: "#save" }, context());
  const approval: HumanApproval = {
    actionId: staged.actionId, binding: staged.binding, policyVersion: POLICY_VERSION,
    approvedAt: new Date().toISOString(), approvedBy: "LOCAL_HUMAN",
  };
  await writeStagedAction(staged);
  await writeHumanApproval(approval);
  assert.ok(await claimApproval(staged.actionId));
  await assert.rejects(writeHumanApproval(approval));
  await finalizeApprovalConsumption(staged.actionId);
  await assert.rejects(writeHumanApproval(approval));
  assert.equal(await claimApproval(staged.actionId), undefined);
});

function sampleReceipt(suffix: string, previousReceiptHash: string | null = null) {
  const page = context();
  return buildReceipt({
    receiptId: `RCP-00000000-0000-0000-0000-${suffix}`,
    actionId: `BRA-00000000-0000-0000-0000-${suffix}`,
    binding: "b".repeat(64), policyVersion: POLICY_VERSION, operation: "click", pageIndex: 0,
    executedAt: "2026-10-28T00:00:00.000Z", pageBefore: page, pageAfter: { ...page, element: null },
    result: { operation: "click", selector: "#save" }, previousReceiptHash,
  });
}

test("concurrent receipt writers cannot silently fork the chain", async () => {
  await rm(ledgerRoot(), { recursive: true, force: true });
  const candidates = [sampleReceipt("000000000020"), sampleReceipt("000000000021")];
  const outcomes = await Promise.allSettled(candidates.map(writeReceipt));
  assert.equal(outcomes.filter((result) => result.status === "fulfilled").length, 1);
  const winner = candidates[outcomes.findIndex((result) => result.status === "fulfilled")];
  const loser = candidates[outcomes.findIndex((result) => result.status === "rejected")];
  assert.equal((await readReceiptHead())?.receiptHash, winner.receiptHash);
  assert.equal(await readReceipt(loser.receiptId), undefined);
});

test("a stale receipt cannot replace the head; a correctly linked successor can", async () => {
  await rm(ledgerRoot(), { recursive: true, force: true });
  const first = sampleReceipt("000000000030");
  await writeReceipt(first);
  await assert.rejects(writeReceipt(sampleReceipt("000000000031")), /RECEIPT_HEAD_MISMATCH/);
  assert.equal((await readReceiptHead())?.receiptHash, first.receiptHash);
  const next = sampleReceipt("000000000032", first.receiptHash);
  await writeReceipt(next);
  assert.equal((await readReceiptHead())?.receiptHash, next.receiptHash);
});

test("a leftover writer lock blocks publication and is preserved for human recovery", async () => {
  await rm(ledgerRoot(), { recursive: true, force: true });
  await readReceiptHead(); // Create the test ledger directories.
  const lockPath = path.join(ledgerRoot(), "receipt-writer.lock");
  await writeFile(lockPath, "SYNTHETIC_CRASH_LOCK");
  await assert.rejects(writeReceipt(sampleReceipt("000000000040")), { code: "EEXIST" });
  assert.equal(await readFile(lockPath, "utf8"), "SYNTHETIC_CRASH_LOCK");
  assert.equal(await readReceiptHead(), undefined);
});
