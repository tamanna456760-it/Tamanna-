# Tamanna AI personal memory

Tamanna's personal memory is explicit, account-scoped storage. It does not silently save every message.

## API

All routes require a valid signed-in session cookie.

- `GET /api/memory?limit=100` — list the current account's saved memories.
- `POST /api/memory` — save a memory:
  ```json
  {
    "content": "The user prefers concise explanations in Bangla.",
    "metadata": {
      "category": "preference",
      "source": "user-approved"
    }
  }
  ```
- `PATCH /api/memory/{id}` — update a memory owned by the current account.
- `DELETE /api/memory/{id}` — delete a memory owned by the current account.

Memory content is limited to 10,000 characters. List limits are bounded by the database layer. A user cannot read, update, or delete another account's records.

## Chat context

For an authenticated chat, Tamanna loads up to eight recent saved memories belonging to that account and adds them as contextual data. The prompt explicitly tells the model to treat saved memory as context, not as system instructions. Recent conversation history is also scoped by both conversation ID and user ID.

## Privacy and deployment notes

- Do not store passwords, API keys, session tokens, payment data, or other secrets as memories.
- Only save durable facts or preferences with the user's approval.
- Memory is stored in the configured SQLAlchemy database. SQLite is suitable for a single persistent server; use a managed persistent database for horizontally scaled production.
- Back up the database securely and restrict database access.
- These endpoints do not automatically extract or save memories from chat. Automatic extraction should be a separate opt-in feature with user review.
