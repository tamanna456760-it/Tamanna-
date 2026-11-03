# Put Tamanna AI online at www.bd-king-r7.com

Owner: HM INSAN ALI

This is the production deployment runbook for the FastAPI application in this
repository. A GitHub commit alone does not publish the website. You need a
Linux server that you control, public DNS pointing to it, and working TLS
certificates.

## Before deployment

1. Confirm that you control the registration and authoritative DNS for
   `www.bd-king-r7.com`.
2. Provision an Ubuntu/Debian server with a public static IPv4 address.
3. Allow inbound TCP ports 80 and 443 in the server firewall and hosting
   firewall. Keep port 8000 private.
4. Install Docker Engine and the Docker Compose plugin.
5. Create DNS records at the authoritative DNS provider:
   - Configure only the `www` hostname: use the hosting provider's required `CNAME` target, or an `A` record to the server IPv4 if required.
   - Publish an `AAAA` record for `www` only if the server has working public IPv6.
   If a CDN/proxy is enabled, configure it so the origin can complete the
   HTTP-01 certificate challenge. DNS changes may take time to propagate.

## Prepare the private server configuration

From the repository root on the server:

```bash
git clone https://github.com/tamanna456760-it/Tamanna-.git
cd Tamanna-
git pull origin main
cp .env.example .env
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Edit `.env` on the server only. Set a newly generated
`TAMANNA_SESSION_SECRET` (at least 32 characters), your administrator email,
your Gemini API key if required, and the production values:

```dotenv
TAMANNA_CORS_ORIGINS=https://www.bd-king-r7.com,https://bd-king-r7.com
TAMANNA_COOKIE_SECURE=1
TAMANNA_SESSION_SECRET=REPLACE_WITH_GENERATED_RANDOM_SECRET
TAMANNA_ADMIN_EMAIL=YOUR_VERIFIED_ADMIN_EMAIL
GEMINI_API_KEY=YOUR_GEMINI_KEY
```

Do not commit or share `.env`. The current signup flow does not verify email
ownership. Do not expose public signup or privileged server/code-management
features until production authentication and authorization have been
independently reviewed.

## Issue the first TLS certificate

The HTTPS Nginx configuration expects certificate files at
`/etc/letsencrypt/live/www.bd-king-r7.com/`. Obtain that certificate before
starting the production Compose stack.

On Ubuntu/Debian, install Certbot using the official package instructions,
then run standalone issuance while ports 80 and 443 are free:

```bash
sudo certbot certonly --standalone \
  --cert-name www.bd-king-r7.com \
  -d www.bd-king-r7.com -d bd-king-r7.com \
  --agree-tos --no-eff-email
```

Certbot will ask for a contact email. The domain must already resolve to this
server and inbound port 80 must be reachable. If issuance fails, stop here and
fix DNS/firewall validation; do not start Nginx with missing certificate files.

## Validate and start

From the repository root:

```bash
python3 deploy/validate_deployment.py
docker compose -f deploy/docker-compose.yml --env-file .env config
docker compose -f deploy/docker-compose.yml --env-file .env up -d --build
docker compose -f deploy/docker-compose.yml --env-file .env ps
docker compose -f deploy/docker-compose.yml --env-file .env logs --tail=100 tamanna-ai nginx
```

The app is bound only to localhost port 8000. Nginx publishes ports 80/443.
Application data is stored in the named Docker volume `tamanna_data`.

## Verify from outside the server

```bash
curl -fsS https://www.bd-king-r7.com/health
curl -I https://www.bd-king-r7.com/
```

Then open `https://www.bd-king-r7.com` in a browser and test the chat and account
flows. A successful `/health` response proves only that the health endpoint
responds; it does not prove Gemini credentials, every feature, or account
security is correct.

## Updates and certificate renewal

Deploy later source updates with:

```bash
git pull origin main
docker compose -f deploy/docker-compose.yml --env-file .env up -d --build
```

Enable and test Certbot renewal on the host. After certificate renewal, reload
Nginx so it reads the renewed files:

```bash
sudo certbot renew --dry-run
docker compose -f deploy/docker-compose.yml --env-file .env exec nginx nginx -s reload
```

Back up the `.env` file and the Docker volume securely. Never delete the
`tamanna_data` volume during routine updates.
