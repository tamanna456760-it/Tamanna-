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

Email verification and email-based password reset are not enabled; they require a configured mail provider. Existing legacy application routes have not been globally protected by this initial rollout. Do not treat login as an access-control boundary for those routes until each sensitive route is explicitly secured and tested.
