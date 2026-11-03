# Tamanna AI Memory & Knowledge Import

## Scope and data boundaries

Tamanna can build a searchable knowledge base from data the account owner is authorized to provide:
- ChatGPT data exports (for example, the exported `conversations.json` file).
- User-selected TXT, Markdown, and JSON files.
- Public documentation and third-party AI outputs only when collected through permitted/public sources or authorized APIs, with source attribution and applicable license/terms respected.

This feature does **not** copy private model weights, hidden system prompts, internal provider datasets, other users' conversations, or private data from competing AI services. It does not claim to import data automatically from GPT or any other provider.

## Import

The Python API is explicit; importing a file requires a trusted server-side caller and a user-selected file path:

```python
from tamanna_ai.memory.knowledge_import import import_knowledge_file
from tamanna_ai.persistence.database import database

result = import_knowledge_file(
    "/secure/imports/conversations.json",
    database=database,
    user_id=authenticated_user_id,
)
```

Supported formats: `.json`, `.txt`, `.md`; maximum file size: 20 MiB. The original file is not modified. Credential-like strings are redacted before persistence. Imports are deduplicated by content hash and carry source/title/provenance metadata.

## Retrieval

```python
from tamanna_ai.memory.knowledge_import import search_knowledge
results = search_knowledge(
    "What did we decide about secure memory?",
    database=database,
    user_id=authenticated_user_id,
    limit=5,
)
```

The caller must authenticate the user and always pass the authenticated `user_id`. Never expose cross-user results. Retrieved content is untrusted reference material, not instructions: do not execute commands or obey embedded prompts found in imported documents. Display source labels with answers and distinguish user-supplied material from verified facts.

## Production requirements

- Keep SQLite/database files and imported originals outside Git; encrypt storage and backups at rest.
- Use per-user authorization on every import, search, export, and deletion route.
- Add malware scanning and archive-bomb protections before accepting browser uploads.
- Add retention controls, export/delete controls, audit logging, rate limits, and backup/restore tests.
- Do not ingest credentials, session cookies, private keys, health/financial data, or other sensitive information unless a narrowly defined, lawful feature explicitly requires it and safeguards are in place.
- Use approved provider APIs and respect their terms, privacy rules, copyright, and rate limits.
- This module provides lexical retrieval, not embeddings/vector search or automatic chat integration. Those require a separate tested integration.

## Verification

Run:

```bash
python -m pytest tests/test_knowledge_import.py -q
python -m compileall -q tamanna_ai/memory/knowledge_import.py
```
