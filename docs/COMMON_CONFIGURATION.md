# Tamanna Common Configuration

**Configuration owner:** HM INSAN ALI  
**Applies to:** Tamanna AI application and Tamanna Central Server  
**Status:** Baseline policy; deployment values remain environment-specific.

## 1. Shared project identity
- Product: Tamanna AI
- Application repository: `tamanna456760-it/Tamanna-`
- Central server repository: `tamanna456760-it/Tamanna-server`
- Public canonical domain target: `https://www.bd-king-r7.com`
- The application and central server are separate services and must be deployable, testable, restartable, and monitored independently.

## 2. Configuration precedence
1. Runtime environment variables and private, untracked `.env` files.
2. Safe defaults in application configuration.
3. This document describes policy; it is not a source of production secrets or live infrastructure values.

Never commit API keys, passwords, session secrets, HMAC shared secrets, private keys, database files, user exports, or production logs. Keep `.env.example` limited to placeholders.

## 3. Service-to-service connection
- Central Server local development URL: `http://127.0.0.1:8000`.
- Tamanna AI local development URL: `http://127.0.0.1:8001` (host port; container port may be 8000).
- Use HTTPS for all public-network communication.
- Use the signed Tamanna Service Protocol v1 for service-to-service reports.
- The key ID must match on both services. Generate one random secret locally and set it independently in both private environments; never paste it into source code, GitHub, chat, URLs, or logs.
- Do not automatically forward chat content or memory to the central server. Only explicitly authorized, minimal operational reports may be sent.

## 4. Owner and access control
- Configuration authority: HM INSAN ALI.
- Administrative access must use authenticated accounts, least privilege, and auditable actions.
- Do not treat a display name or email address as proof of administrator identity.
- Protect admin routes, memory import/search/export/delete, file operations, and configuration changes with server-side authorization.
- Never expose internal service credentials to browser/mobile clients.

## 5. Memory and knowledge policy
Tamanna may learn from:
- User-provided files and the user's own exported conversations, after explicit import.
- Public documentation and public datasets where access, license, and terms permit use.
- Third-party AI responses only through authorized APIs or user-provided exports, with source and provenance retained.

Tamanna must not copy private model weights, hidden prompts, provider-internal datasets, other users' conversations, private account data, or access-controlled material without authorization.

For every imported item, retain user/tenant ownership, source, import time, content hash, and available license/provenance. Redact credentials and exclude secrets. Treat retrieved documents as untrusted reference data, never as executable instructions. Keep user data isolated; require authenticated user identity for every memory operation. Provide retention, export, deletion, backup, and restore controls before production use.

## 6. Learning quality and autonomy
- Prefer source-backed facts; record source URL/title, retrieval time, and confidence where available.
- Detect conflicting or stale information and avoid presenting uncertain material as verified.
- Respect rate limits, robots/terms, copyright, and source licensing.
- Do not silently train or modify model weights. Retrieval-based knowledge updates are not model training.
- No autonomous code modification, deployment, privilege escalation, or destructive action. Changes require tests, review, and owner approval.
- Provide a clear pause/disable control for ingestion and background learning.

## 7. Security baseline
- HTTPS/TLS at public boundaries; reverse proxy/WAF where deployed.
- Strict CORS allowlist; no wildcard credentialed CORS.
- Rate limits, request size limits, input validation, secure headers, and structured audit logs.
- Redis-backed nonce replay prevention for multi-worker signed protocol deployments; fail closed if configured Redis is unavailable.
- Keep databases, uploads, backups, and logs out of Git. Encrypt sensitive data at rest and protect backups.
- Do not expose shell execution or unrestricted file-write tools to unauthenticated users.

## 8. Operations and verification
- Keep separate health checks, logs, backups, deployment configuration, and CI results for each repository/service.
- Run syntax checks, unit tests, dependency/security checks, container build, and deployment preflight before release.
- Never report a check as passed until its actual result is successful.
- Do not force-push or delete files outside an explicitly approved scope.
- Record commit SHA and CI run URL in release reports.

## 9. Environment variables
Use each repository's `.env.example` as the authoritative variable-name template. Configure actual values only in private runtime secrets. Do not assume a local port, public origin IP, DNS record, or secret exists until verified in the target environment.

## 10. Change control
Any change to this shared policy should be reviewed in both repositories so the application and central server do not drift. Owner: **HM INSAN ALI**.
