# Tamanna AI Capabilities

This package provides a conversation-aware orchestration layer over the existing Gemini provider and SQLAlchemy conversation store.

- **NLP/chat:** sends language-aware guidance and the current user message to the configured model provider.
- **Reasoning:** asks the model to explain conclusions clearly, distinguish assumptions, and state uncertainty; it does not guarantee correctness.
- **Short-term memory:** retrieves only a bounded number of recent complete user/assistant pairs for the active conversation, scoped by the authenticated user (or anonymous conversations) and capped by character budgets.\n- **Long-term memory:** stores persistent user memories in SQL storage; reads are isolated by user ID. Memory update/delete operations require an owner user ID and only affect that user's records. The application must authenticate users and pass the verified user ID; never trust a user ID supplied by the browser.
- **Multimodal input:** Gemini provider accepts local JPG/JPEG, PNG, WEBP, GIF, MP3, WAV, OGG, MP4, WEBM and PDF files through inline data, with a combined 15 MiB limit. Call `CapabilityAssistant.chat_with_files(...)`. Upload handling, authentication, malware scanning and temporary-file lifecycle remain the responsibility of the API caller.

- **Coding and software development:** supports code generation, explanation, review, debugging, refactoring, optimization, import/dependency investigation, focused test suggestions, and README/API documentation across common programming languages. The model proposes code; this capability layer does not execute arbitrary generated code or shell commands.
- **Debugging discipline:** distinguishes inspected facts from assumptions and never reports a test as passed unless a real test runner returned a passing result. File modifications and repository writes must go through a separately authorized, constrained application workflow.
- **Writing and content creation:** drafts original articles, research-based explainers, blog posts, professional emails, proposals, business plans, reports, and strategy summaries; translates between requested languages; and edits spelling, grammar, clarity, tone, and structure. Research claims and citations must be grounded in supplied or actually checked sources—never fabricated.
- **Translation and editing discipline:** preserves meaning, context, and tone; flags ambiguous wording; and avoids silently changing the author's intent.
- **Tools:** includes a deliberately restricted arithmetic calculator using Python AST (never `eval`) and an internal indexed project-code search; no shell or arbitrary code execution is exposed.
- **Web/API tools:** must be explicitly configured and allow-listed. This package does not silently fetch arbitrary URLs or execute external actions.

## Usage

```python
from tamanna_ai.capabilities import CapabilityAssistant

assistant = CapabilityAssistant()
result = await assistant.chat("Explain this problem", conversation_id="chat-123", user_id=42)
# For a caller-validated list of temporary upload paths:
result = await assistant.chat_with_files("Describe these files", ["/secure/tmp/upload.png"], conversation_id="chat-123", user_id=42)
```

The caller must authenticate the user and ensure that the conversation ID belongs to that user before calling this service. Validate file size/type, scan uploads, store them outside the web root, and delete temporary uploads after processing. Do not expose this class through a public unauthenticated route.

## Important limitations

This is runtime orchestration, not a new foundation model. It does not increase Gemini's native context window, guarantee factual answers, execute a hidden chain-of-thought, train model weights, or provide automatic web browsing. Long documents should be chunked/retrieved under a token budget. Audio/video/PDF availability and accepted formats depend on the selected Gemini model and API support.

## Memory behavior

- Short-term history is persisted as chat messages and only recent pairs are loaded into each prompt.
- Long-term memories persist across conversations in the SQL database and are isolated by user ID.
- The persistence layer exposes `add_memory`, `list_memories`, `update_memory` and `delete_memory`.
- The model does not autonomously save arbitrary personal facts. A trusted application flow should ask for consent or apply an explicit memory policy before calling `add_memory`.
- Provide users with a privacy/settings screen to inspect and delete their stored memories. Database backups and retention policies must also cover memory records.
