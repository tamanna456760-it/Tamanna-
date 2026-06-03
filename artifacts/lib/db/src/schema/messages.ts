import {
  integer,
  pgTable,
  serial,
  text,
  timestamp,
  index,
  check,
  jsonb,
  real,
} from "drizzle-orm/pg-core";
import { createInsertSchema, createSelectSchema } from "drizzle-zod";
import { z } from "zod/v4";
import { sql } from "drizzle-orm";

import { conversations } from "./conversations";

export const messages = pgTable(
  "messages",
  {
    id: serial("id").primaryKey(),
    conversationId: integer("conversation_id")
      .notNull()
      .references(() => conversations.id, { onDelete: "cascade" }),
    role: text("role").notNull(),
    content: text("content").notNull(),
    
    // Advanced fields
    tokensUsed: integer("tokens_used"),                    // Track token count for billing
    model: text("model"),                                  // Which AI model generated this (e.g., "gpt-4")
    metadata: jsonb("metadata").$type<Record<string, unknown>>(), // Flexible metadata (thinking time, tool calls, etc.)
    
    // Soft delete
    deletedAt: timestamp("deleted_at", { withTimezone: true }),
    
    // Automatic timestamps with update hook
    createdAt: timestamp("created_at", { withTimezone: true })
      .defaultNow()
      .notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .defaultNow()
      .notNull()
      .$onUpdate(() => new Date()),
    
    // Full‑text search vector (English)
    searchVector: text("search_vector").generatedAlwaysAs(
      sql`setweight(to_tsvector('english', coalesce(content, '')), 'A')`,
      { stored: true }
    ),
    
    // Optional: pgvector for semantic search (requires pgvector extension)
    // embedding: vector("embedding", { dimensions: 1536 }), // For OpenAI embeddings
  },
  (table) => ({
    // Indexes
    conversationIdx: index("idx_messages_conversation_id").on(table.conversationId),
    roleIdx: index("idx_messages_role").on(table.role),
    createdAtIdx: index("idx_messages_created_at").on(table.createdAt),
    tokensIdx: index("idx_messages_tokens_used").on(table.tokensUsed),
    deletedAtIdx: index("idx_messages_deleted_at")
      .on(table.deletedAt)
      .where(sql`deleted_at IS NULL`),
    searchIdx: index("idx_messages_search").using("gin", table.searchVector),
    metadataGinIdx: index("idx_messages_metadata").using("gin", table.metadata),
    
    // Check constraints
    roleCheck: check("chk_messages_role", sql`role IN ('user', 'assistant', 'system')`),
    contentNotEmpty: check(
      "chk_messages_content_not_empty",
      sql`length(trim(content)) > 0`
    ),
    tokensPositive: check(
      "chk_messages_tokens_positive",
      sql`tokens_used IS NULL OR tokens_used > 0`
    ),
    
    // Unique constraint: prevent duplicate messages in same conversation? Usually not needed,
    // but you could enforce that a user cannot send identical content within short time.
    // Example: uniqueIndex("uq_messages_conversation_content").on(table.conversationId, table.content),
  })
);

// -------------------- Enhanced Zod Schemas --------------------

// Base insert schema – id and createdAt omitted
export const insertMessageSchema = createInsertSchema(messages, {
  role: z.enum(["user", "assistant", "system"]),
  content: z.string().min(1).max(10000).trim(),
  conversationId: z.number().positive(),
  tokensUsed: z.number().positive().optional(),
  model: z.string().optional(),
  metadata: z.record(z.unknown()).optional(),
  deletedAt: z.date().optional(),
  // updatedAt and searchVector are auto‑generated
}).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  searchVector: true,
});

// Select schema (for API responses)
export const selectMessageSchema = createSelectSchema(messages, {
  createdAt: z.date(),
  updatedAt: z.date(),
  deletedAt: z.date().nullable(),
  metadata: z.record(z.unknown()).nullable(),
});

// Schema for updating a message (e.g., to soft‑delete or adjust metadata)
export const updateMessageSchema = createInsertSchema(messages, {
  content: z.string().min(1).max(10000).trim().optional(),
  tokensUsed: z.number().positive().optional(),
  metadata: z.record(z.unknown()).optional(),
  deletedAt: z.date().nullable().optional(),
}).partial().extend({
  // Only allow updating certain fields
  id: z.number().positive(),
}).omit({
  conversationId: true,
  role: true,
  createdAt: true,
  updatedAt: true,
  searchVector: true,
});

// -------------------- Types --------------------
export type Message = typeof messages.$inferSelect;
export type InsertMessage = z.infer<typeof insertMessageSchema>;
export type UpdateMessage = z.infer<typeof updateMessageSchema>;

// Helper type for messages with their conversation (join)
export type MessageWithConversation = Message & {
  conversation: typeof conversations.$inferSelect;
};

// -------------------- Utility Functions (optional) --------------------

// Soft delete a message
export const softDeleteMessage = (id: number) =>
  sql`UPDATE messages SET deleted_at = NOW() WHERE id = ${id}`;

// Hard delete physically removes the row (use with caution)
export const hardDeleteMessage = (id: number) =>
  sql`DELETE FROM messages WHERE id = ${id}`;

// Restore a soft‑deleted message
export const restoreMessage = (id: number) =>
  sql`UPDATE messages SET deleted_at = NULL WHERE id = ${id}`;

// Full‑text search across messages in a conversation
export const searchMessagesInConversation = (conversationId: number, query: string) =>
  sql`SELECT * FROM messages 
      WHERE conversation_id = ${conversationId} 
        AND deleted_at IS NULL
        AND search_vector @@ to_tsquery('english', ${query})
      ORDER BY created_at ASC`;