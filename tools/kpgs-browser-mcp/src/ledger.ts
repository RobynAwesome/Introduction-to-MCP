import { mkdir, open, readFile, rename, unlink, writeFile } from "node:fs/promises";
import path from "node:path";
import {
  publicActionSummary,
  verifyReceiptIntegrity,
  type BrowserReceipt,
  type HumanApproval,
  type StagedBrowserAction
} from "./governance.js";

const ROOT = path.resolve(process.env.KPGS_BROWSER_LEDGER_DIR ?? ".kpgs-browser-ledger");
const PENDING = path.join(ROOT, "pending");
const APPROVED = path.join(ROOT, "approved");
const APPROVAL_GRANTS = path.join(ROOT, "approval-grants");
const EXECUTING = path.join(ROOT, "executing");
const RECEIPTS = path.join(ROOT, "receipts");
const CONSUMED = path.join(ROOT, "consumed");
const FAILED = path.join(ROOT, "failed");
const ARCHIVED = path.join(ROOT, "archived");
const QUARANTINED = path.join(ROOT, "quarantined");
const RECEIPT_HEAD = path.join(ROOT, "receipt-head.json");
const RECEIPT_WRITER_LOCK = path.join(ROOT, "receipt-writer.lock");

function assertActionId(actionId: string): void {
  if (!/^BRA-[0-9a-f-]+$/i.test(actionId)) throw new Error("Invalid browser action id");
}

function assertReceiptId(receiptId: string): void {
  if (!/^RCP-[0-9a-f-]+$/i.test(receiptId)) throw new Error("Invalid browser receipt id");
}

async function ensureLedger(): Promise<void> {
  await mkdir(ROOT, { recursive: true, mode: 0o700 });
  await Promise.all(
    [PENDING, APPROVED, APPROVAL_GRANTS, EXECUTING, RECEIPTS, CONSUMED, FAILED, ARCHIVED, QUARANTINED].map((dir) =>
      mkdir(dir, { recursive: true, mode: 0o700 })
    )
  );
}

async function readJson<T>(filePath: string): Promise<T | undefined> {
  try {
    return JSON.parse(await readFile(filePath, "utf8")) as T;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return undefined;
    throw error;
  }
}

async function writeNewJson(filePath: string, value: unknown): Promise<void> {
  await writeFile(filePath, JSON.stringify(value, null, 2), { flag: "wx", mode: 0o600 });
}

export function ledgerRoot(): string {
  return ROOT;
}

export async function writeStagedAction(action: StagedBrowserAction): Promise<void> {
  await ensureLedger();
  assertActionId(action.actionId);
  await writeNewJson(path.join(PENDING, `${action.actionId}.json`), action);
}

export async function readStagedAction(actionId: string): Promise<StagedBrowserAction | undefined> {
  await ensureLedger();
  assertActionId(actionId);
  return readJson<StagedBrowserAction>(path.join(PENDING, `${actionId}.json`));
}

export async function archiveStagedAction(actionId: string, disposition: string): Promise<void> {
  await ensureLedger();
  assertActionId(actionId);
  const pendingPath = path.join(PENDING, `${actionId}.json`);
  const staged = await readJson<StagedBrowserAction>(pendingPath);
  if (!staged) return;
  await writeNewJson(path.join(ARCHIVED, `${actionId}.json`), {
    disposition,
    closedAt: new Date().toISOString(),
    action: publicActionSummary(staged)
  });
  await unlink(pendingPath);
}

export async function quarantineStagedAction(actionId: string, reason: string): Promise<void> {
  await ensureLedger();
  assertActionId(actionId);
  const from = path.join(PENDING, `${actionId}.json`);
  const to = path.join(QUARANTINED, `${actionId}.json`);
  try {
    await rename(from, to);
    await writeNewJson(path.join(QUARANTINED, `${actionId}.meta.json`), {
      reason,
      quarantinedAt: new Date().toISOString(),
      replayAllowed: false,
      humanReviewRequired: true
    });
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error;
  }
}

export async function writeHumanApproval(approval: HumanApproval): Promise<void> {
  await ensureLedger();
  assertActionId(approval.actionId);
  // Also reject already-issued grants from ledgers created before grant markers.
  for (const directory of [APPROVED, EXECUTING, CONSUMED, FAILED]) {
    if (await readJson(path.join(directory, `${approval.actionId}.json`))) {
      throw new Error("APPROVAL_ALREADY_ISSUED_RESTAGE_REQUIRED");
    }
  }
  // An immutable grant marker closes the check/write race and survives claiming,
  // consumption, failure or a crash before the approval file is written.
  // A failed grant must be restaged with a new action id; never retry it in place.
  await writeNewJson(path.join(APPROVAL_GRANTS, `${approval.actionId}.json`), {
    actionId: approval.actionId, binding: approval.binding, approvedAt: approval.approvedAt,
  });
  await writeNewJson(path.join(APPROVED, `${approval.actionId}.json`), approval);
}

export async function readHumanApproval(actionId: string): Promise<HumanApproval | undefined> {
  await ensureLedger();
  assertActionId(actionId);
  return readJson<HumanApproval>(path.join(APPROVED, `${actionId}.json`));
}

export async function claimApproval(actionId: string): Promise<HumanApproval | undefined> {
  await ensureLedger();
  assertActionId(actionId);
  const from = path.join(APPROVED, `${actionId}.json`);
  const to = path.join(EXECUTING, `${actionId}.json`);
  try {
    await rename(from, to);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return undefined;
    throw error;
  }
  return readJson<HumanApproval>(to);
}

export async function finalizeApprovalConsumption(actionId: string): Promise<void> {
  await ensureLedger();
  assertActionId(actionId);
  await rename(path.join(EXECUTING, `${actionId}.json`), path.join(CONSUMED, `${actionId}.json`));
}

export async function failClaimedApproval(actionId: string): Promise<void> {
  await ensureLedger();
  assertActionId(actionId);
  try {
    await rename(path.join(EXECUTING, `${actionId}.json`), path.join(FAILED, `${actionId}.json`));
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error;
  }
}

export async function readReceiptHead(): Promise<{ receiptId: string; receiptHash: string } | undefined> {
  await ensureLedger();
  return readJson<{ receiptId: string; receiptHash: string }>(RECEIPT_HEAD);
}

export async function writeReceipt(receipt: BrowserReceipt): Promise<void> {
  await ensureLedger();
  assertReceiptId(receipt.receiptId);
  if (!verifyReceiptIntegrity(receipt)) throw new Error("RECEIPT_INTEGRITY_INVALID_BEFORE_WRITE");
  // Exclusive creation works across local processes. A crash leaves the lock
  // for human inspection; this code never steals a lock or retries a side effect.
  const lock = await open(RECEIPT_WRITER_LOCK, "wx", 0o600);
  try {
    const head = await readReceiptHead();
    if (receipt.previousReceiptHash !== (head?.receiptHash ?? null)) {
      throw new Error("RECEIPT_HEAD_MISMATCH_HUMAN_REVIEW_REQUIRED");
    }
    await writeNewJson(path.join(RECEIPTS, `${receipt.receiptId}.json`), receipt);
    const nextHead = path.join(ROOT, `receipt-head-${receipt.receiptId}.tmp`);
    await writeNewJson(nextHead, { receiptId: receipt.receiptId, receiptHash: receipt.receiptHash });
    await rename(nextHead, RECEIPT_HEAD);
  } finally {
    await lock.close();
    await unlink(RECEIPT_WRITER_LOCK);
  }
}

export async function readReceipt(receiptId: string): Promise<BrowserReceipt | undefined> {
  await ensureLedger();
  assertReceiptId(receiptId);
  return readJson<BrowserReceipt>(path.join(RECEIPTS, `${receiptId}.json`));
}
