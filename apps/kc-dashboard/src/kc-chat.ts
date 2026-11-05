import type { KopanoAssertReceipt } from "./types/rtc";

export interface KcChatReply {
  reply: string;
  suggestedActions: string[];
  receipt: KopanoAssertReceipt | null;
}

export class KcChatError extends Error {
  constructor(readonly reason: "unavailable" | "invalid-response" | "timeout") {
    super(reason);
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function parseReceipt(value: unknown, identity: string): KopanoAssertReceipt | null {
  if (!isRecord(value)) return null;
  const fields = ["assert_id", "session_id", "rtc_identity", "intent_domain", "claim", "residency", "proof_hash", "status", "timestamp"] as const;
  if (!fields.every((field) => typeof value[field] === "string" && value[field].trim().length > 0)) return null;
  if (value.rtc_identity !== identity || !/^[a-f0-9]{64}$/i.test(value.proof_hash as string)
      || !Number.isFinite(Date.parse(value.timestamp as string))) return null;
  // Shape validation is not ledger verification. The UI must keep that distinction.
  return Object.fromEntries(fields.map((field) => [field, value[field]])) as unknown as KopanoAssertReceipt;
}

export function parseKcChatReply(value: unknown, identity: string): KcChatReply {
  if (!isRecord(value) || typeof value.reply !== "string" || !value.reply.trim()) {
    throw new KcChatError("invalid-response");
  }
  return {
    reply: value.reply,
    suggestedActions: Array.isArray(value.suggested_actions)
      ? value.suggested_actions.filter((action): action is string => typeof action === "string" && action.trim().length > 0)
      : [],
    receipt: parseReceipt(value.assert_receipt, identity),
  };
}

export async function requestKcReply(
  message: string,
  identity: string,
  fetchReply: typeof fetch = fetch,
  signal: AbortSignal = AbortSignal.timeout(15_000),
): Promise<KcChatReply> {
  try {
    const response = await fetchReply("/api/kc/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, rtc_identity: identity }),
      signal,
    });
    if (!response.ok) throw new KcChatError("unavailable");
    return parseKcChatReply(await response.json(), identity);
  } catch (error) {
    if (error instanceof KcChatError) throw error;
    if (signal.aborted) throw new KcChatError("timeout");
    if (error instanceof SyntaxError) throw new KcChatError("invalid-response");
    throw new KcChatError("unavailable");
  }
}
