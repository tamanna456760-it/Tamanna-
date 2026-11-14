# Local chat demo

This folder contains a dependency-free, rule-based HTTP demo for checking local chat transport. It is **not** the production Tamanna AI model and does not use an external AI API.

Run from the repository root:

```sh
python runner/python/AI_CHAT/chat_server.py
```

The server binds to `127.0.0.1:5000` by default.

- `GET /health` returns a local health status.
- `POST /chat` accepts JSON such as `{"message":"hello"}`.
- Set `TAMANNA_CHAT_HOST` or `TAMANNA_CHAT_PORT` to override the bind address or port.

The request body is size-limited and malformed or empty messages receive HTTP 400. The default bind address is loopback-only.
