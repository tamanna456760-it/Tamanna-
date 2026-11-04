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
- **Multimodal analysis:** the Gemini integration accepts supported local image, audio, video, and PDF inputs through `CapabilityAssistant.chat_with_files(...)`, subject to provider/model support and the documented combined upload limit. This is input analysis, not an image, voice, or music generation engine.
- **Media generation status:** image generation, text-to-speech/voiceover synthesis, voice cloning, and music generation are not implemented by the current provider interface. The assistant may help draft prompts, scripts, lyrics, and production plans, but must not claim to have generated media files. A separately configured generation provider, authenticated API routes, upload/output validation, consent controls, and storage lifecycle are required.
- **Media safety:** voice cloning requires explicit authorization from the voice owner; deceptive impersonation is disallowed. Music output should be original and must not reproduce protected songs or lyrics.
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

## Prompt engineering

`tamanna_ai.capabilities.prompt_engineering.build_structured_prompt()`
builds a consistent prompt from a goal, optional untrusted reference context,
constraints, output format, language, and measurable success criteria. It
validates required fields and size limits. This is a deterministic prompt
builder, not an automatic guarantee of model accuracy or task completion.

 
## Core code generation

`build_code_generation_prompt()` turns a feature description into a
structured software task with language/framework, project context, complete
file deliverables, dependency/setup instructions, tests, and verification
requirements. `supported_language_examples()` lists more than 50 language
and syntax examples; this is an illustrative list, not a benchmark or a
guarantee that every provider supports every language equally. The helper
prepares prompts; actual code generation still requires the configured model
provider, and execution/testing requires a separate approved runtime.


## Debugging, security review, and performance analysis

The assistant guidance covers pasted terminal errors, tracebacks, browser
console messages, API/build/CI logs, root-cause hypotheses, minimal fixes,
regression tests, common application security risks, and performance bottlenecks.
`build_debugging_prompt()` structures an error report plus optional source
code/runtime/expected-vs-actual context. It does not execute supplied commands,
run a scanner, or prove a fix; confirmed results require an actual test,
profiler, scanner, or runtime reproduction.


## Code refactoring and optimization

`build_refactoring_prompt()` structures a request around source code, language,
framework/runtime version, user priorities, behavior preservation, deprecated
API migration, performance analysis, regression tests, and verification.
Performance improvements and compatibility claims require actual profiling
or test results; the prompt helper itself does not modify or execute project files.


## Documentation and inline comments

`build_documentation_prompt()` prepares source-grounded inline comments,
docstrings, README, and API reference requests. It supports audience and
documentation-style settings, and avoids comments that merely restate code.
Generated documentation must be checked against the actual implementation;
the helper does not itself edit repository files.


## Whole-project README and API documentation

`build_project_documentation_prompt()` accepts a repository tree and optional
verified source/configuration excerpts. It can request a root README, API
reference, and architecture overview. Accurate output depends on supplying the
actual relevant files; a tree alone is not sufficient evidence for endpoint
behavior or setup commands.

## Database and backend service development

`build_database_backend_prompt()` prepares tasks for parameterized SQL,
MongoDB collection schemas, REST endpoints, and GraphQL schemas/resolvers.
It emphasizes authorization, owner isolation, validation, migrations,
pagination, error handling, and tests. It generates a structured task prompt;
it does not connect to or mutate a live database.


## Context window and memory layers

The assistant assembles system instructions, owner-scoped profile settings,
saved memories, recent conversation history, retrieved RAG excerpts, and the
current message within a configurable context budget
(`context_window_tokens`, default 24,000). Lower-priority context is trimmed
before the current request and system instructions. `estimate_tokens()` uses a
conservative UTF-8 byte estimate, not the provider's exact tokenizer.

The SQLite conversation/memory persistence and optional `VectorKnowledgeStore`
provide external long-term memory and RAG. The vector store must be explicitly
supplied to `CapabilityAssistant`; it is not silently enabled or populated.
Parametric memory belongs to the model provider's trained weights and cannot
be directly edited through ordinary provider API calls.
