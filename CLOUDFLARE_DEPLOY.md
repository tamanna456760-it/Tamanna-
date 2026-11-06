# Cloudflare Workers Static Site Deployment

Owner: HM INSAN ALI

## Production configuration

Use Cloudflare Workers Builds for the production hostname `www.bd-king-r7.com`.

| Setting | Value |
| --- | --- |
| Production branch | `main` |
| Root directory | repository root `/` |
| Build command | `npm run check:cloudflare` |
| Deploy command | `npx wrangler deploy --config wrangler.jsonc` |
| Worker name | `titamanna` |
| Static assets directory | `./dist` |

The committed `wrangler.jsonc` explicitly targets `./dist`; never upload the repository root. The build validator checks required public files, domain CNAME, forbidden security report paths, and the 25 MiB per-file asset limit.

## Domain / DNS checklist

- Cloudflare zone for `bd-king-r7.com` must be Active.
- Registrar nameservers must match the nameservers assigned by Cloudflare.
- Add `www.bd-king-r7.com` as a Worker Custom Domain under Workers & Pages → `titamanna` → Settings → Domains & Routes.
- Optionally redirect apex `bd-king-r7.com` to `https://www.bd-king-r7.com` with a Cloudflare Redirect Rule.
- Do not guess A/AAAA records or publish a competing GitHub Pages origin for the same hostname.
- Verify DNSSEC DS records if DNSSEC is enabled.
- Check TLS and redirect behavior before announcing the domain live.

## Important: API backend is separate

The Worker serves static assets only. It does not run Python/FastAPI or execute `Main.py`. The browser frontend currently requests `/api/chat`; this endpoint requires a separately deployed Python backend and an explicit Cloudflare route/proxy for `/api/*`. Until that is configured and tested, the static website may load while AI chat/API calls fail.

Store API keys and session secrets only in Cloudflare/server secret storage, not Git. Configure exact allowed origin `https://www.bd-king-r7.com`, secure cookies, and backend health checks.

## Build and deploy

```sh
npm run check:cloudflare
npx wrangler deploy --config wrangler.jsonc
```

## Domain audit

Run the read-only audit from the repository root:

```sh
npm run audit:domain
```

It checks apex/www DNS, HTTP/HTTPS status, redirects, TLS verification, and repository CNAME. It does not change DNS or Cloudflare settings.

The GitHub Actions workflow `.github/workflows/pages.yml` is validation-only. It intentionally does not publish to GitHub Pages, avoiding two providers competing for the same custom hostname.

Repository checks cannot confirm registrar ownership, Cloudflare account access, zone activation, DNS propagation, Worker custom-domain attachment, or live API health. Verify those in the relevant dashboards and deployment logs.
