# Tamanna AI security setup

## 1. Rotate the exposed Gemini credential

A credential-like value was found in the tracked `.ven` file. Treat it as compromised even though the file is removed in the security-fix branch.

1. Open Google AI Studio and revoke the exposed Gemini API key.
2. Create a replacement key.
3. Store the replacement only in the server's private `.env` file or a secret manager.
4. Never paste the key into source files, issue comments, chat logs, or GitHub commits.
5. Removing a file from the latest commit does not remove it from Git history. After rotation, arrange a coordinated history cleanup before force-pushing rewritten history.

## 2. Configure the private server environment

Copy `.env.example` to `.env` on the server. Keep `.env` outside version control and restrict its permissions (for example, `chmod 600 .env`). Set at least:

- `GEMINI_API_KEY`: the newly rotated Gemini key.
- `TAMANNA_ADMIN_API_KEY`: a new, long random secret generated on the server.
- `TAMANNA_CORS_ORIGINS`: only trusted Tamanna frontend origins.

Generate a random admin key locally on the server with:

```sh
python3 -c 'import secrets; print(secrets.token_urlsafe(48))'
```

Do not commit the generated value. Restart the application after changing environment variables.

## 3. Privileged API routes

The following operations now require the `X-API-KEY` request header and a matching `TAMANNA_ADMIN_API_KEY` environment value:

- `POST /api/code-builder/apply`
- `POST /api/linux/run`
- `POST /api/linux/shell`
- `POST /api/self-healing/cycle`
- `POST /api/autonomous/build`
- `POST /api/autonomous/repair`
- `POST /api/command`

If the server key is not configured, these endpoints return HTTP 503 (disabled). Missing and incorrect request keys return HTTP 401 and HTTP 403 respectively. The CORS allow-list includes the `X-API-KEY` header; it does not make the key public or configure it in the browser automatically.

## 4. Docker exposure

The root Compose file binds the application port to `127.0.0.1:8000`, not every network interface. Put a trusted reverse proxy in front of it and expose only the required public HTTP/HTTPS ports.

## 5. Remaining security work

This change is a targeted hardening pass, not a complete security certification. Review chat-driven action routing, all shell bridge implementations, token history, workflow permissions, dependency advisories, and the deployment origin before production use.
