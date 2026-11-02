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
