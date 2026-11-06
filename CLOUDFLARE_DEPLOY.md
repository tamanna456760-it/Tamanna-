# Cloudflare Workers Static Site Deployment

Owner: HM INSAN ALI

## Cloudflare Pages / Workers build settings

Use the repository root and the `main` branch.

| Setting | Value |
| --- | --- |
| Production branch | `main` |
| Root directory | `/` (repository root) |
| Build command | `npm run check:cloudflare` |
| Build output directory | `dist` |
| Deploy command (Workers Builds) | `npx wrangler deploy --config wrangler.jsonc` |

If the Cloudflare project is a Workers Builds project, use the Deploy command above. If the project is a Pages project, deploy the `dist/` output with the Pages deployment flow instead; do not mix Pages and Workers deploy commands in one project.

## What the build does

1. `npm run build` creates a clean `dist/` directory.
2. Only the public website files are copied into `dist/`; Python server code, threat-intelligence reports, private datasets, logs, and repository metadata stay outside the published asset directory.
3. `scripts/verify-cloudflare-deploy.js` checks the Wrangler config, required website files, custom domain, forbidden report paths, and the 25 MiB per-file asset limit.
4. Wrangler is explicitly configured by `wrangler.jsonc` to upload `./dist`, never the repository root.

## Local pre-deploy check

Requires Node.js 20 or newer:

```sh
npm run check:cloudflare
```

To deploy from a machine with Wrangler access:

```sh
npx wrangler deploy --config wrangler.jsonc
```

## Required Cloudflare settings

- Connect the GitHub repository and select branch `main`.
- Confirm the build is using the commit that contains `wrangler.jsonc`.
- For Workers Builds, use the build and deploy commands in the table above.
- Keep API keys and other secrets in Cloudflare Secrets / environment variables, never in Git.
- Attach `www.bd-king-r7.com` as the Worker custom domain and verify its DNS records in Cloudflare.
- Confirm the deployment log says the assets directory is `./dist`. If it says `.` or starts scanning the full repository, stop and correct the project settings before retrying.

## Important

This repository preflight validates the local build artifact; it cannot confirm Cloudflare account permissions, domain ownership, DNS propagation, TLS activation, or a successful live deployment. Those require the connected Cloudflare project and a completed deployment.
