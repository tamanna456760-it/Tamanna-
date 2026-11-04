# Tamanna AI Capabilities

This package provides a conversation-aware orchestration layer over the existing Gemini provider and SQLAlchemy conversation store.

- **NLP/chat:** sends language-aware guidance and the current user message to the configured model provider.
- **Reasoning:** asks the model to explain conclusions clearly, distinguish assumptions, and state uncertainty; it does not guarantee correctness.
- **Memory/context:** adds a bounded number of recent conversation pairs and saved memories, scoped by user ID when supplied.
- **Multimodal input:** Gemini provider accepts local JPG/JPEG, PNG, WEBP, GIF, MP3, WAV, OGG, MP4, WEBM and PDF files through inline data, with a combined 15 MiB limit. Call `CapabilityAssistant.chat_with_files(...)`. Upload handling, authentication, malware scanning and temporary-file lifecycle remain the responsibility of the API caller.
- **Tools:** includes a deliberately restricted arithmetic calculator using Python AST (never `eval`); no shell or arbitrary code execution is exposed.
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
