#!/usr/bin/env bash
# Safe, guarded deployment for the user's own Linux server.
# This script does not change DNS, request certificates, or delete volumes.
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/deploy/docker-compose.yml"
ENV_FILE="$ROOT_DIR/.env"
CERT_DIR="/etc/letsencrypt/live/www.tamanna.com"
cd "$ROOT_DIR"

fail() {
  printf 'ERROR: %s\n' "$1" >&2
  exit 1
}

for command_name in docker curl git grep; do
  command -v "$command_name" >/dev/null 2>&1 || fail "Required command not found: $command_name"
done

docker info >/dev/null 2>&1 || fail "Docker Engine is not running or this user cannot access it."
[[ -f "$COMPOSE_FILE" ]] || fail "Missing Docker Compose file: $COMPOSE_FILE"
[[ -s "$ENV_FILE" ]] || fail "Missing private .env. Run scripts/configure_private_auth.py and add the real Gemini key first."

git check-ignore -q .env || fail ".env is not ignored by Git; stop and fix .gitignore before deployment."
if git ls-files --error-unmatch .env >/dev/null 2>&1; then
  fail ".env is tracked by Git. Do not deploy until it is removed from tracking and any exposed secrets are rotated."
fi

grep -Eq '^TAMANNA_SESSION_SECRET=[^#[:space:]].{31,}$' "$ENV_FILE" || fail "TAMANNA_SESSION_SECRET must be configured with at least 32 characters."
grep -Eq '^TAMANNA_ADMIN_EMAIL=[^#[:space:]]+@[^#[:space:]]+$' "$ENV_FILE" || fail "TAMANNA_ADMIN_EMAIL must contain a valid configured email."
grep -Eq '^GEMINI_API_KEY=[^#[:space:]].+$' "$ENV_FILE" || fail "GEMINI_API_KEY is empty; configure the private Gemini API key."
if grep -Eq '^TAMANNA_SESSION_SECRET=CHANGE_ME' "$ENV_FILE"; then
  fail "The example session-secret placeholder is still configured."
fi

[[ -s "$CERT_DIR/fullchain.pem" ]] || fail "TLS certificate missing: $CERT_DIR/fullchain.pem"
[[ -s "$CERT_DIR/privkey.pem" ]] || fail "TLS private key missing: $CERT_DIR/privkey.pem"
chmod 600 "$ENV_FILE"

printf '%s\n' "==> Validate Docker Compose configuration"
docker compose -f "$COMPOSE_FILE" config --quiet

printf '%s\n' "==> Build the production image"
docker compose -f "$COMPOSE_FILE" build --pull

printf '%s\n' "==> Start or update Tamanna AI and Nginx"
docker compose -f "$COMPOSE_FILE" up -d

printf '%s\n' "==> Wait for backend health"
healthy=0
for attempt in $(seq 1 36); do
  status="$(docker inspect --format '{{.State.Health.Status}}' tamanna-ai 2>/dev/null || true)"
  if [[ "$status" == "healthy" ]]; then
    healthy=1
    break
  fi
  sleep 5
done
[[ "$healthy" -eq 1 ]] || {
  docker compose -f "$COMPOSE_FILE" logs --tail=100 tamanna-ai nginx || true
  fail "Backend did not become healthy within 3 minutes."
}

printf '%s\n' "==> Verify public HTTPS homepage and health endpoint"
curl --fail --silent --show-error --location --max-time 20 https://www.tamanna.com/ >/dev/null
curl --fail --silent --show-error --location --max-time 20 https://www.tamanna.com/health

printf '\n%s\n' "==> Deployment status"
docker compose -f "$COMPOSE_FILE" ps
printf '\n%s\n' "PASS: Tamanna deployment checks completed."
