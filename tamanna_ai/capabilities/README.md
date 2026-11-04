# Tamanna AI Capabilities

This package provides a usable orchestration layer over the existing Gemini provider and SQLAlchemy conversation store.

- **NLP/chat:** sends a language-aware system guide and the current user message to the configured provider.
- **Reasoning:** instructs the model to explain reasoning clearly and state uncertainty; it does not guarantee correctness.
- **Memory/context:** adds a bounded number of recent conversation pairs and saved memories, scoped by user ID when supplied.
- **Tools:** includes a deliberately restricted arithmetic calculator using Python AST (never `eval`); no shell or arbitrary code execution is exposed.
- **Multimodal:** image/audio/video/file processing is not automatically enabled by this text-chat orchestration. Add a provider-specific multimodal adapter and authenticated upload/size/type validation before exposing it.
- **Web/API tools:** must be explicitly configured and allow-listed; this package does not silently fetch arbitrary URLs or execute external actions.

## Usage

```python
from tamanna_ai.capabilities import CapabilityAssistant

assistant = CapabilityAssistant()
result = await assistant.chat("Explain this problem", conversation_id="chat-123", user_id=42)
```

The caller must authenticate the user and ensure that the conversation ID belongs to that user before calling this service. Do not expose this class through a public unauthenticated route.
