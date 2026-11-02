# Tamanna AI — Security and Deployment Setup

## Safe CI and deployment policy

The development validation workflow is manual and read-only. It has `contents: read`, disables persisted checkout credentials, does not format or modify source files, does not commit or push, and does not deploy or restart services.

A failed validation must remain failed. Do not add `continue-on-error`, a force-deploy override, or any bypass that allows deployment after failed tests.

## Workflow directory hygiene

GitHub Actions recognizes workflow definitions in `.github/workflows/` with `.yml` or `.yaml` extensions. Other files in that directory are not workflows. Run the read-only inventory with:

```bash
python scripts/audit_workflow_directory.py --root .github/workflows --output workflow-directory-inventory.json
```

Review each source/configuration file and search for imports, references, build inputs, and documentation before relocating it. Do not delete files solely because they are in the wrong directory. Keep workflow definitions in `.github/workflows/`; move application source only after dependency and path checks, preferably in a separate reviewed change.

## Deployment safeguards

1. Keep deployment separate from validation.
2. Require successful CI and an explicit protected-environment approval before deployment.
3. Use least-privilege credentials and store secrets only in GitHub Actions secrets or the private server environment; never commit `.env` or API keys.
4. Pin third-party actions to reviewed immutable commit SHAs for production use.
5. Use a documented health check and tested rollback procedure. A placeholder command is not a deployment.
6. Do not deploy from pull requests originating from forks with secrets available.

## Current scope

This document describes repository-side safeguards. It does not prove that the live website, DNS, TLS, server, or production deployment has been verified.

## Credential exposure response

If a GitHub personal access token, cloud key, session secret, or private key has ever been committed:
1. Revoke the exposed credential immediately in its provider console. Removing it in a later commit does not invalidate it.
2. Create a replacement with the minimum required scopes and store it only in the private server environment or GitHub Actions secrets.
3. Review provider audit logs for unexpected use.
4. Treat the old value as compromised even if the repository is private.
5. Coordinate Git history cleanup separately; history rewriting does not replace revocation.

The repository scanner can be run with:

```bash
python scripts/security_secret_scan.py --root .
```

The scanner reports file paths, line numbers, and rule identifiers only; it does not print matched credential values. It is a pattern-based check and cannot guarantee that every secret format is detected.

## Privileged API safeguards

The access-control middleware protects sensitive write and execution routes. Admin-only routes require the signed session belonging to `TAMANNA_ADMIN_EMAIL`. State-changing requests with a browser Origin header are accepted only from `TAMANNA_CORS_ORIGINS`. Keep this allowlist limited to trusted frontend origins.
The CI validation also rejects tracked private environment files other than the explicitly allowed `.env.example`. The local pattern scanner excludes `.env` files to avoid reading local environment files; check tracked environment-file names separately with `git ls-files` when running the scanner outside CI.

## Audit finding requiring owner action

The audit found a GitHub personal access token embedded in the historical version of `runner/python/ai_backup_network.py`. The active file on this security branch has been replaced with a local, read-only inventory utility, but this commit does not revoke the exposed credential or erase it from existing Git history. The repository owner must revoke that token immediately, review its access logs, and only then create a least-privilege replacement if needed.


## Admin account bootstrap protection

Registration of the email configured in `TAMANNA_ADMIN_EMAIL` requires a separate bootstrap token. This prevents an unauthenticated visitor from registering the known admin email first and gaining the administrator identity.

1. Generate a unique token on the private server (do not paste it into GitHub):

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

2. Put the generated value in the server's untracked `.env` file as `TAMANNA_ADMIN_SIGNUP_TOKEN=...`, alongside `TAMANNA_ADMIN_EMAIL`.
3. During the first registration only, submit the token in the signup JSON field `admin_bootstrap_token`. Never put the token in frontend JavaScript, a public config, GitHub, chat logs, or a URL.
4. After the admin account is successfully created, remove `TAMANNA_ADMIN_SIGNUP_TOKEN` from the server environment and restart the service. Existing admin login continues to work; new registrations using the admin email remain blocked.
5. If the token may have been exposed, replace it before attempting registration.

Example request body shape (use a private HTTPS request; replace every placeholder locally):

```json
{
  "email": "your-admin-email@example.com",
  "name": "Admin",
  "password": "a-long-unique-password",
  "admin_bootstrap_token": "YOUR_PRIVATE_BOOTSTRAP_TOKEN"
}
```

The example file contains only an empty placeholder. Never commit the generated token or a real `.env` file.
