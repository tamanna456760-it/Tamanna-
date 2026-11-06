# Tamanna AI — Domain and Deployment Configuration

Owner: HM INSAN ALI

## Canonical hostname

The only canonical website hostname configured in this repository is:

`https://www.bd-king-r7.com`

The root/apex hostname `bd-king-r7.com` is not the canonical host. If you want it to work, configure a Cloudflare Redirect Rule to send all requests to `https://www.bd-king-r7.com` while preserving the path and query string. Do not create a second origin for the apex hostname.

## Choose one production host

Production static hosting is configured for **Cloudflare Workers Static Assets**:

- Git branch: `main`
- Build command: `npm run check:cloudflare`
- Deploy command: `npx wrangler deploy --config wrangler.jsonc`
- Static assets directory: `./dist`
- Worker name: `titamanna`

Attach `www.bd-king-r7.com` to the Worker as a Custom Domain in Cloudflare. The Cloudflare zone must be Active, and the DNS record must be created/managed by Cloudflare. Do not point the same hostname simultaneously at GitHub Pages and the Worker.

The GitHub Actions workflow `.github/workflows/pages.yml` is now validation-only. It no longer publishes a competing GitHub Pages site.

## DNS checklist in Cloudflare

1. Confirm you own/control the registration for `bd-king-r7.com`.
2. Confirm the registrar delegates the domain to the exact Cloudflare nameservers assigned to your zone.
3. Cloudflare Dashboard → Websites → `bd-king-r7.com`: zone status must be **Active**, not Pending or Finish setup.
4. Workers & Pages → `titamanna` → Settings → Domains & Routes: add `www.bd-king-r7.com` as a Custom Domain.
5. For the apex redirect, create a Redirect Rule from `bd-king-r7.com/*` to `https://www.bd-king-r7.com/$1`, preserving query strings. Verify the rule syntax in the dashboard before enabling.
6. Do not add guessed A/AAAA IP addresses. For a Worker Custom Domain, let Cloudflare create the required DNS mapping.
7. If DNSSEC is enabled at the registrar, ensure the DS record matches Cloudflare's DNSSEC settings. A stale DS record can make the whole domain fail resolution.

## HTTPS

- Use Cloudflare SSL/TLS mode **Full (strict)** when the origin/backend has a valid certificate. A Worker Custom Domain is served by Cloudflare's edge.
- Enable HTTPS redirects and HSTS only after HTTPS is verified.
- Confirm the certificate covers `www.bd-king-r7.com`.
- Do not disable certificate verification to work around TLS errors.

## Backend hosting is not decided yet

The repository intentionally keeps backend hosting provider-neutral until a host,
plan, database, and persistent-storage strategy are selected. Review
[`BACKEND_HOSTING_PLAN.md`](../BACKEND_HOSTING_PLAN.md) before deployment.

The root `Dockerfile` and `run_server.py` are the portable baseline for the
existing FastAPI application. The separate `cloudflare/backend/` Python Worker
is an optional Cloudflare-native API prototype; it does not run the full
`Main.py` application and must not be treated as the production backend until
its runtime, Gemini outbound requests, D1 persistence, and migration behavior
have been tested.

## Important: frontend and backend are separate

The Cloudflare static asset Worker serves the files in `dist/`. It does not execute `Main.py`, FastAPI, or the Python AI backend. The current browser frontend calls the relative endpoint `/api/chat`; this will not work on a static-only Worker unless an API route/backend is separately deployed and routed.

Before announcing the AI chat as live, deploy the Python backend to a supported server/service and configure a secure Cloudflare route or Worker proxy for `/api/*`. Keep API keys and session secrets in server/Cloudflare secrets, never in Git. Set exact allowed CORS origins and secure cookies for `https://www.bd-king-r7.com`.

## Read-only audit

On Termux, iSH, Linux, or macOS with Bash and curl (dig and openssl recommended):

```sh
bash scripts/domain-audit.sh
```

The script checks apex and www DNS, HTTP/HTTPS responses, redirects, TLS verification, and the repository CNAME. It does not change DNS or push code.

A repository check cannot confirm registrar ownership, Cloudflare account zone status, custom-domain attachment, DNS propagation from all resolvers, or live API readiness. Those must be verified in the relevant account and from the deployed service.
