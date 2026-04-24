// lib/db/src/schema/index.ts
// ============================================
// Barrel Exports for Database Schema
// ============================================

// ---------- Tables ----------
export { conversations } from "./conversations";
export { messages } from "./messages";

// ---------- Insert Schemas (Zod) ----------
export { insertConversationSchema } from "./conversations";
export { insertMessageSchema } from "./messages";

// ---------- Select Schemas (Zod) ----------
// If you have them in individual files, uncomment:
// export { selectConversationSchema } from "./conversations";
// export { selectMessageSchema } from "./messages";

// ---------- TypeScript Types ----------
export type {
  Conversation,
  InsertConversation,
} from "./conversations";

export type {
  Message,
  InsertMessage,
  // UpdateMessage,        // if you added update schemas
  // MessageWithConversation,
} from "./messages";

// ---------- Utility Functions (re‑exported from modules) ----------
// If you added helper functions like softDeleteMessage, restoreMessage, etc.
// export { softDeleteMessage, restoreMessage, searchMessagesInConversation } from "./messages";

// ---------- Centralized Validation Helpers ----------
import { insertConversationSchema } from "./conversations";
import { insertMessageSchema } from "./messages";
import type { InsertConversation, InsertMessage } from "./conversations";
import type { InsertMessage as InsertMessageType } from "./messages";

/**
 * Validate and parse conversation input data.
 * Throws a ZodError if validation fails.
 */
export function validateConversation(data: unknown): InsertConversation {
  return insertConversationSchema.parse(data);
}

/**
 * Validate and parse message input data.
 * Throws a ZodError if validation fails.
 */
export function validateMessage(data: unknown): InsertMessageType {
  return insertMessageSchema.parse(data);
}

/**
 * Safely validate conversation data without throwing.
 * Returns { success, data, error }
 */
export function safeValidateConversation(data: unknown) {
  return insertConversationSchema.safeParse(data);
}

/**
 * Safely validate message data without throwing.
 */
export function safeValidateMessage(data: unknown) {
  return insertMessageSchema.safeParse(data);
}

// ---------- Type Guards ----------
import type { Conversation, Message } from "./conversations";
import type { Message as MessageType } from "./messages";

export function isConversation(obj: unknown): obj is Conversation {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "id" in obj &&
    "title" in obj &&
    "createdAt" in obj
  );
}

export function isMessage(obj: unknown): obj is MessageType {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "id" in obj &&
    "conversationId" in obj &&
    "role" in obj &&
    "content" in obj
  );
}

// ---------- Re‑export commonly used Drizzle types (optional) ----------
export type { InferSelectModel, InferInsertModel } from "drizzle-orm";