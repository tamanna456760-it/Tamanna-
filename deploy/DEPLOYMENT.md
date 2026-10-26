# Tamanna AI Deployment Guide

Owner: HM INSAN ALI

## Deployment Workflows

- `.github/workflows/deploy.yml`
  validates deployment configuration.
- `.github/workflows/pages.yml`
  publishes the static website to GitHub Pages.
- `Main.py` runs the Python/FastAPI backend.
- `CNAME` identifies the configured custom domain.

## GitHub Pages Setup

1. Open the GitHub repository.
2. Go to Settings → Pages.
3. Select GitHub Actions as the source.
4. Open the Actions tab.
5. Check the latest Pages workflow run.

A successful workflow is required before confirming
that the static website has been published.

## Custom Domain

The CNAME file must contain:

    www.tamanna.com

Before modifying DNS records, verify domain ownership
and access to the domain's DNS settings.

Configure the DNS records recommended by GitHub Pages.
Do not overwrite existing records without checking them.

## HTTPS and TLS

1. Open Settings → Pages.
2. Check the custom domain status.
3. Wait for certificate provisioning if necessary.
4. Enable Enforce HTTPS when available.
5. Visit https://www.tamanna.com and verify the
   browser reports a valid certificate.

## FastAPI Backend

GitHub Pages only hosts static files. It does not
execute Main.py or run FastAPI API endpoints.

Host the backend on a Python-capable server and
configure the frontend to use that backend's HTTPS URL.

Never commit API keys, private keys, access tokens,
or a real `.env` file to the repository.

## Troubleshooting

- Check the Actions tab for workflow errors.
- Verify Settings → Pages and deployment permissions.
- Verify DNS records and the CNAME file.
- Verify HTTPS after the certificate is issued.
- If the homepage loads but chat fails, check whether
  the FastAPI backend is deployed and configured.
