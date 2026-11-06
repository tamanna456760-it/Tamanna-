# Cloudflare Workers Static Site Deployment

Owner: HM INSAN ALI

## Recommended: Cloudflare Workers Builds

Connect the GitHub repository and select branch `main`.

| Setting | Value |
| --- | --- |
| Production branch | `main` |
| Root directory | repository root `/` |
| Build command | `npm run check:cloudflare` |
| Deploy command | `npx wrangler deploy --config wrangler.jsonc` |

Workers Builds uses the `assets.directory` value in `wrangler.jsonc`; there is no separate output-directory setting to point at the repository root. The committed Wrangler config explicitly sets it to `./dist`.

## Alternative: Cloudflare Pages

If the Cloudflare project is a Pages project instead of a Workers Builds project, use:

| Setting | Value |
| --- | --- |
| Production branch | `main` |
| Build command | `npm run check:cloudflare` |
| Build output directory | `dist` |

Deploy the Pages artifact using the Pages deployment flow. Do not run the Workers `wrangler deploy` command in a Pages project. Do not configure both deployment methods for the same project.

## What the build does

1. `npm run build` creates a clean `dist/` directory.
2. Only public website files are copied into `dist/`; Python server code, threat-intelligence reports, private datasets, logs, and repository metadata stay outside the published asset directory.
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

- Confirm the production branch is `main` and the build is using the commit that contains `wrangler.jsonc`.
- For Workers Builds, use the build and deploy commands in the first table.
- Keep API keys and other secrets in Cloudflare Secrets / environment variables, never in Git.
- Attach `www.bd-king-r7.com` as the Worker custom domain and verify its DNS records in Cloudflare.
- Confirm the deployment log says the assets directory is `./dist`. If it says `.` or scans the full repository, stop and correct the project settings before retrying.

## Important

Repository preflight checks validate the local build artifact; they cannot confirm Cloudflare account permissions, domain ownership, DNS propagation, TLS activation, or a successful live deployment. Those require the connected Cloudflare project and a completed deployment.
