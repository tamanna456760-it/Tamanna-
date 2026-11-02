<p align="center">
  <img src="assets/tamanna-logo.svg"
       alt="TI Tamanna AI Logo"
       width="280">
</p>

# Project Documentation

## Overview
This repository contains code for a variety of features including AI learning capabilities, a chat bot, system automation, and other new functionalities.

## AI Learning Features
This section describes the AI learning aspects of the project.
- **Machine Learning Models**: Details about the models used, training data, and evaluation metrics.
- **Training Process**: Steps on how to train the models from scratch, including preprocessing and hyperparameter tuning.

## Chat Bot
The chat bot is implemented using [Technology/Framework].
- **Core Features**: Highlight key features like natural language understanding, conversation context management, etc.
- **How to Use**: Instructions on how to interact with the chat bot.

## System Automation
This part covers the automation scripts present in the repository.
- **Automation Tools**: List of tools and frameworks used.
- **Setup Instructions**: Steps required to set up the automation environment.

## New Features
Recent updates and features added to the project:
- **Feature 1**: Brief description of the feature.
- **Feature 2**: Brief description of the feature.

## Contribution
Instructions for contributing to the project.

## License
Details about the licensing of the code.

## Contact
For any questions or support, please reach out to the project maintainer.

## Tamanna AI account authentication

The account API is integrated under `/api/auth` and uses SQLite, PBKDF2-HMAC-SHA256 password hashing, signed HttpOnly session cookies, and server-side session revocation.

### Required server configuration

1. Generate a unique session secret on the server: `python -c "import secrets; print(secrets.token_urlsafe(48))"`
2. Put it in the private server `.env` as `TAMANNA_SESSION_SECRET=...`. Never commit the real `.env` or secret.
3. For HTTPS production, set `TAMANNA_COOKIE_SECURE=1`. For local HTTP development, set it to `0` and include the local frontend origin in `TAMANNA_CORS_ORIGINS`.
4. Restart FastAPI. SQLite is created at `data/accounts.sqlite3` by default; back it up securely.

### Authentication endpoints

- `POST /api/auth/signup` — create account (password minimum 12 characters)
- `POST /api/auth/login` — sign in
- `GET /api/auth/me` — current session
- `POST /api/auth/logout` — revoke current session
- `PATCH /api/auth/profile` — update display name
- `POST /api/auth/change-password` — change password and revoke sessions
- `GET/PUT /api/auth/preferences` — read/save account preferences

Email verification and email-based password reset are not enabled; they require a configured mail provider. The access-control middleware currently protects a defined set of state-changing and privileged routes; it does not mean every legacy API route requires login. Review the route allowlist whenever new APIs are added.

### Sensitive API access control

The access-control middleware protects state-changing skill, repair, automation, and code-builder endpoints. Server/code execution endpoints additionally require the signed-in user's email to match `TAMANNA_ADMIN_EMAIL`. If the admin email is not configured, those privileged endpoints return HTTP 503 (fail closed); a non-admin account receives HTTP 403, and an unauthenticated request receives HTTP 401.

Set the following only in the private server `.env` (never commit personal account configuration):

```dotenv
TAMANNA_ADMIN_EMAIL=the-admin-account-email@example.com
```

Use the same email address as the account created through `/api/auth/signup`. Keep `TAMANNA_SESSION_SECRET` unique and private. This middleware is an additional API boundary; it does not replace OS-level isolation, a reverse-proxy firewall, rate limiting, backups, or review of each feature's own file/path validation.
