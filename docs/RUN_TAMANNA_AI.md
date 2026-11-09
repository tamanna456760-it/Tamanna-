# Run Tamanna AI locally

This guide starts the FastAPI application from the repository root. It does not deploy the public website.

## 1. Requirements

- Python 3.11 or newer (Python 3.12 is used by the Docker image)
- Git
- Internet access for installing Python packages
- Ollama installed locally, with the selected model already pulled (for example, `qwen2.5:7b`)

## 2. Get the current source

```bash
git clone https://github.com/tamanna456760-it/Tamanna-.git
cd Tamanna-
git pull origin main
```

If you already cloned the repository, run `git pull origin main` from its root.

## 3. Create an isolated Python environment

Linux, macOS, or Termux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-server.txt
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`.

If virtual-environment creation is unavailable on Alpine/iSH, install the platform's Python venv/pip packages first. Do not install packages as root unless your environment requires it.

## 4. Configure local development

```bash
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Open `.env` in a text editor. Set these values for local HTTP development (replace the session-secret placeholder with the generated value):

```dotenv
TAMANNA_CORS_ORIGINS=http://127.0.0.1:3000,http://localhost:3000
TAMANNA_MODEL_PROVIDER=ollama
TAMANNA_OLLAMA_URL=http://127.0.0.1:11434
TAMANNA_OLLAMA_MODEL=qwen2.5:7b
TAMANNA_SESSION_SECRET=PASTE_YOUR_GENERATED_RANDOM_VALUE_HERE
TAMANNA_SESSION_SECONDS=604800
TAMANNA_COOKIE_SECURE=0
TAMANNA_AUTH_DB=data/accounts.sqlite3
TAMANNA_ADMIN_EMAIL=your-admin-email@example.com
```

Keep `.env` private. It is ignored by Git. Never paste its contents into GitHub, logs, or chat. If you do not have a frontend running on port 3000, the API can still be tested directly; the CORS origins are for browser-based local frontends.

Chat uses the local Ollama runtime. No Gemini/GPT API key is required or used by the primary FastAPI provider. If Ollama is unavailable, chat should return a service-unavailable response; it must not silently switch to a hosted model.

**Important:** the current signup API does not verify email ownership. Keep this development instance private; do not expose public signup or privileged server/code operations to the internet until email verification and production access controls have been reviewed. The admin email is a privilege selector, not proof that the mailbox belongs to you.

## 5. Start the API

```bash
HOST=127.0.0.1 PORT=8000 RELOAD=1 python run_server.py
```

Keep that terminal open. The API should listen at `http://127.0.0.1:8000`.

## 6. Verify it is running

In a second terminal:

```bash
python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5).read().decode())"
```

Also open:

- API health: http://127.0.0.1:8000/health
- Interactive API docs: http://127.0.0.1:8000/docs
- Root endpoint: http://127.0.0.1:8000/

A successful health response confirms the API process is responding; it does not prove every feature, Gemini access, or the public domain is working.

## 7. Run the automated tests

```bash
python -m compileall -q Main.py run_server.py tamanna_ai data modules tests scripts
python -m pytest -q
```

If pytest is not installed, install it with `python -m pip install pytest`.

## 8. Optional: Docker Compose

After creating and configuring `.env`:

```bash
docker compose config
docker compose up -d --build tamanna-ai
docker compose ps
docker compose logs --tail=100 tamanna-ai
```

The Compose service binds to `127.0.0.1:8000`, not the public internet. Docker must be installed and running. To stop it:

```bash
docker compose down
```

## Production deployment is a separate task

Do not change the local `TAMANNA_COOKIE_SECURE=0` setting on an HTTPS production server. Production needs HTTPS, `TAMANNA_COOKIE_SECURE=1`, a strong unique session secret, correct trusted CORS origins, a private database backup plan, restricted admin access, and a reviewed reverse proxy/firewall. The repository push does not start a server or deploy `www.bd-king-r7.com`.
