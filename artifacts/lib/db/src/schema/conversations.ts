import { 
  pgTable, 
  serial, 
  text, 
  timestamp, 
  integer, 
  index, 
  uniqueIndex,
  foreignKey,
  check,
  pgPolicy,
  type InferSelectModel,
  type InferInsertModel
} from "drizzle-orm/pg-core";
import { createInsertSchema, createSelectSchema } from "drizzle-zod";
import { z } from "zod/v4";
import { sql } from "drizzle-orm";

// -------------------- Conversations Table --------------------
export const conversations = pgTable(
  "conversations",
  {
    id: serial("id").primaryKey(),
    title: text("title").notNull(),
    // Soft delete support
    deletedAt: timestamp("deleted_at", { withTimezone: true }),
    // Timestamps with automatic update on change
    createdAt: timestamp("created_at", { withTimezone: true })
      .defaultNow()
      .notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .defaultNow()
      .notNull()
      .$onUpdate(() => new Date()),
    // Optional: user association
    userId: integer("user_id").references(() => users.id, {
      onDelete: "cascade",
    }),
    // Full‑text search vector (PostgreSQL)
    searchVector: text("search_vector").generatedAlwaysAs(
      sql`setweight(to_tsvector('english', coalesce(title, '')), 'A')`,
      { stored: true }
    ),
  },
  (table) => ({
    // Indexes for performance
    titleIdx: index("idx_conversations_title").on(table.title),
    userIdIdx: index("idx_conversations_user_id").on(table.userId),
    createdAtIdx: index("idx_conversations_created_at").on(table.createdAt),
    deletedAtIdx: index("idx_conversations_deleted_at").on(table.deletedAt).where(sql`deleted_at IS NULL`),
    searchIdx: index("idx_conversations_search").using("gin", table.searchVector),
    // Unique constraint: user cannot have duplicate active conversation titles
    uniqueActiveTitlePerUser: uniqueIndex("uq_conversations_user_active_title")
      .on(table.userId, table.title)
      .where(sql`deleted_at IS NULL`),
    // Check constraint: title not empty
    titleNotEmpty: check(
      "chk_conversations_title_not_empty",
      sql`length(trim(title)) > 0`
    ),
    // Row Level Security policy (example for PostgreSQL)
    // userIsolation: pgPolicy("user_isolation_policy", {
    //   as: "permissive",
    //   for: "all",
    //   to: "authenticated_user",
    //   using: sql`user_id = current_setting('app.current_user_id')::int`,
    // }),
  })
);

// -------------------- Messages Table --------------------
export const messages = pgTable(
  "messages",
  {
    id: serial("id").primaryKey(),
    conversationId: integer("conversation_id")
      .notNull()
      .references(() => conversations.id, { onDelete: "cascade" }),
    role: text("role", { enum: ["user", "assistant", "system"] }).notNull(),
    content: text("content").notNull(),
    // Metadata for AI usage
    tokensUsed: integer("tokens_used"),
    model: text("model"),
    // Soft delete
    deletedAt: timestamp("deleted_at", { withTimezone: true }),
    createdAt: timestamp("created_at", { withTimezone: true })
      .defaultNow()
      .notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .defaultNow()
      .notNull()
      .$onUpdate(() => new Date()),
  },
  (table) => ({
    conversationIdx: index("idx_messages_conversation_id").on(table.conversationId),
    roleIdx: index("idx_messages_role").on(table.role),
    createdAtIdx: index("idx_messages_created_at").on(table.createdAt),
    deletedAtIdx: index("idx_messages_deleted_at").on(table.deletedAt).where(sql`deleted_at IS NULL`),
    contentSearchIdx: index("idx_messages_content_search").using("gin", 
      sql`to_tsvector('english', content)`
    ),
    roleCheck: check("chk_messages_role", sql`role IN ('user', 'assistant', 'system')`),
    contentNotEmpty: check("chk_messages_content_not_empty", sql`length(trim(content)) > 0`),
  })
);

// -------------------- Users Table (minimal for reference) --------------------
export const users = pgTable(
  "users",
  {
    id: serial("id").primaryKey(),
    email: text("email").notNull().unique(),
    name: text("name"),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (table) => ({
    emailIdx: uniqueIndex("idx_users_email").on(table.email),
  })
);

// -------------------- Zod Schemas with Enhanced Validation --------------------

// Conversation schemas
export const insertConversationSchema = createInsertSchema(conversations, {
  title: z.string().min(1).max(200).trim(),
  userId: z.number().optional(),
}).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  deletedAt: true,
  searchVector: true,
});

export const selectConversationSchema = createSelectSchema(conversations, {
  createdAt: z.date(),
  updatedAt: z.date(),
  deletedAt: z.date().nullable(),
});

// Message schemas
export const insertMessageSchema = createInsertSchema(messages, {
  conversationId: z.number().positive(),
  role: z.enum(["user", "assistant", "system"]),
  content: z.string().min(1).max(10000),
  tokensUsed: z.number().positive().optional(),
  model: z.string().optional(),
}).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  deletedAt: true,
});

export const selectMessageSchema = createSelectSchema(messages);

// User schemas
export const insertUserSchema = createInsertSchema(users, {
  email: z.string().email(),
  name: z.string().optional(),
}).omit({
  id: true,
  createdAt: true,
});

// -------------------- Types --------------------
export type Conversation = InferSelectModel<typeof conversations>;
export type InsertConversation = InferInsertModel<typeof conversations>;
export type Message = InferSelectModel<typeof messages>;
export type InsertMessage = InferInsertModel<typeof messages>;
export type User = InferSelectModel<typeof users>;
export type InsertUser = InferInsertModel<typeof users>;

// Helper type for conversations with their messages
export type ConversationWithMessages = Conversation & {
  messages: Message[];
};

// Optional: Soft delete helper
export const softDeleteConversation = (id: number) =>
  sql`UPDATE conversations SET deleted_at = NOW() WHERE id = ${id}`;