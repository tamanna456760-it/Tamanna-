# Tamanna AI — Self-Hosted Production Deployment

Owner: HM INSAN ALI  
Primary website: https://www.tamanna.com  
Backend: FastAPI + Docker Compose + Nginx

## Hosting model

The production target is the user's own server. GitHub Pages is not part of the
production deployment path; the self-hosted Nginx server owns the website domain.

The FastAPI application serves the chat UI and API from the same origin.
Nginx is the public entry point on ports 80 and 443. The application port 8000
is bound to localhost only.

## 1. Server prerequisites

Use a Linux server with:
- Docker Engine and the Docker Compose v2 plugin
- DNS records for both `tamanna.com` and `www.tamanna.com` pointing to this server
- Inbound TCP ports 80 and 443 allowed by the host firewall and provider firewall
- A valid TLS certificate covering both domain names

Do not replace existing DNS records until the domain owner has checked the
current DNS zone and confirmed the intended origin server.

## 2. Private environment configuration

From the repository root on the server:

```bash
python3 scripts/configure_private_auth.py
```

The helper creates/updates the ignored `.env` file, sets the admin account email,
generates a session secret when needed, and applies restrictive file permissions.

Then edit the server-only `.env` file and set the real Gemini key:

```dotenv
GEMINI_API_KEY=YOUR_REAL_GEMINI_API_KEY
TAMANNA_CORS_ORIGINS=https://www.tamanna.com,https://tamanna.com
TAMANNA_COOKIE_SECURE=1
```

Replace the placeholder with the real key only on the server. Never put the
real `.env`, Gemini key, session secret, bootstrap token, or TLS private key
in GitHub, the Docker image, logs, or this documentation.

Verify the file is ignored and private:

```bash
git check-ignore .env
chmod 600 .env
```

## 3. TLS certificate

The Nginx configuration expects these files on the host:

- `/etc/letsencrypt/live/www.tamanna.com/fullchain.pem`
- `/etc/letsencrypt/live/www.tamanna.com/privkey.pem`

Obtain a certificate covering both `tamanna.com` and `www.tamanna.com`
before starting the Nginx container. For HTTP-01 validation, port 80 must be
reachable and any existing web server using that port may need a planned,
temporary stop. If DNS is proxied or port 80 cannot be exposed, use the
DNS-01 challenge supported by your DNS provider instead.

Do not start the production Nginx container until the certificate files exist.

## 4. Validate and start

From the repository root:

```bash
docker compose -f deploy/docker-compose.yml config
docker compose -f deploy/docker-compose.yml build
docker compose -f deploy/docker-compose.yml up -d
docker compose -f deploy/docker-compose.yml ps
docker compose -f deploy/docker-compose.yml logs --tail=100 tamanna-ai nginx
```

The app container has a health check against `/health`. Nginx waits until the
app reports healthy before starting. The named Docker volume `tamanna-ai-data`
persists user accounts, chat history and app data across container recreation.
The app is not exposed publicly on port 8000; only Nginx publishes ports 80 and
443. Never remove this volume during a routine update.

## 5. Run the guarded deployment

After the private `.env` and TLS certificate are ready, run this on the Linux
server from the repository checkout:

```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

The script refuses to continue if Docker is unavailable, `.env` is tracked or
not ignored, required private settings are missing, or the TLS certificate is
missing. It validates Compose, builds the image, starts services, waits for
the backend health check, and performs HTTPS homepage/health requests. It does
not change DNS, request certificates, or remove persistent volumes.

## 6. Verify the live website

Run from a machine outside the server network:

```bash
python3 deploy/https_smoke_test.py --url https://www.tamanna.com/
curl -fsS https://www.tamanna.com/health
curl -I https://www.tamanna.com/
```

Also verify that:
- The browser shows a valid TLS certificate.
- `https://tamanna.com/` redirects to `https://www.tamanna.com/`.
- The homepage, login/signup, chat, static CSS and JavaScript load.
- Chat requests reach the FastAPI backend and Gemini responds when the key is set.

A successful static preflight or Docker build is not proof that DNS, TLS,
the server firewall, or the public website is working.

## 7. Renewal and rollback

Test certificate renewal using the certificate tool's dry-run mode. After a
successful certificate renewal, reload/restart Nginx:

```bash
docker compose -f deploy/docker-compose.yml restart nginx
```

Before updating production, keep a known-good image/revision and a protected
backup of the persistent Docker volume and private `.env`. The named volume
`tamanna-ai-data` stores `/app/data` (including the account database and chat
history) across container recreation. Back it up before migrations or release
changes; do not run `docker compose down -v` because that deletes the volume.

Example backup (run on the server):

```bash
docker run --rm \
  -v tamanna-ai-data:/source:ro \
  -v "$PWD:/backup" \
  alpine:3.20 \
  tar -czf /backup/tamanna-ai-data-backup.tgz -C /source .
```

Protect the backup as private user data and store it outside the public web root.

## 8. GitHub Actions

`.github/workflows/deploy.yml` performs read-only preflight validation,
Docker Compose configuration validation, and a local image build. It does not
publish an image, connect to the server, restart services, or deploy changes.

GitHub Pages is intentionally not required or deployed by this self-hosted
workflow. Keep the production domain routed to the user's own Nginx server.

## Troubleshooting

- Container unhealthy: inspect `docker compose ... logs tamanna-ai`.
- Nginx fails to start: verify the certificate and key paths exist and match.
- Homepage works but chat fails: check backend health, `GEMINI_API_KEY`,
  browser network errors, and the backend logs.
- TLS/DNS failure: verify authoritative DNS, origin IP, provider firewall,
  certificate SANs, and certificate expiry.
- Do not expose port 8000 publicly to work around an Nginx issue.
