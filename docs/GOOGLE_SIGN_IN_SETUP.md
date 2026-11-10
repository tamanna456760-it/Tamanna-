# Tamanna AI Google Sign-In setup

Tamanna AI supports email/password login and signup. Optional one-click Google sign-in uses Google Identity Services and verifies the returned ID token on the FastAPI server before creating a session.

## 1. Create a Google OAuth Web client

1. Open Google Cloud Console: https://console.cloud.google.com/
2. Select or create a project and configure the OAuth consent screen.
3. Create an OAuth Client ID with application type **Web application**.
4. Add these authorized JavaScript origins:
   - `https://www.bd-king-r7.com`
   - `http://localhost:5173` (local frontend development, if used)
5. Copy the **Client ID**. Do not create or commit a client secret for this browser ID-token flow.

## 2. Configure the backend

Set the same Client ID in the private server environment (for example, the untracked `.env` file):

```dotenv
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

Keep `.env` private. Do not commit real credentials.

## 3. Configure the frontend build

Set the same public Client ID in the frontend build environment:

```dotenv
VITE_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

The value is a public OAuth client identifier, not a secret. Rebuild and publish the frontend after setting it.

## 4. Verify

- Open `https://www.bd-king-r7.com/chat`.
- Confirm the Google sign-in button appears.
- Sign in with a Google account whose email is verified.
- Confirm the browser receives the HttpOnly `tamanna_session` cookie and `GET /api/auth/me` returns the signed-in account.
- Confirm a wrong OAuth audience or an unverified email is rejected.

Google sign-in remains hidden until `VITE_GOOGLE_CLIENT_ID` is configured. Email/password login and signup use the existing `/api/auth/login`, `/api/auth/signup`, and `/api/auth/me` routes. Google tokens are verified against Google's token-info endpoint; Google availability is therefore required for Google sign-in, but not for local email/password authentication or the local Ollama model.
