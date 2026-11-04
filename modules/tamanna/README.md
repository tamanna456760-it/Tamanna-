# Tamanna message modules

## Approved message memory

`message_memory.py` provides a read-only lookup used by the chat bridge in
`Main.py`. It reads only explicitly approved records and never learns from
ordinary chat messages automatically.

Create a private local JSON file at `data/approved_message_memory.json`, or set
`TAMANNA_MESSAGE_MEMORY_PATH` to another local path. Start from
`data/approved_message_memory.example.json`.

Supported format:

```json
{
  "entries": [
    {
      "question": "What is Tamanna AI?",
      "reply": "Tamanna AI is the user's AI assistant project.",
      "category": "identity",
      "approved": true
    }
  ]
}
```

Only records with `approved: true`, a non-empty question, and a non-empty
reply can be returned. Matching uses normalized exact text first, then a
conservative token-overlap threshold. Missing, malformed, oversized, or
unapproved memory data safely returns no match.

Keep private conversation data out of GitHub. The example file contains only
illustrative, non-private content.
