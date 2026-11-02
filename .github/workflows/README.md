# GitHub Actions workflows

This directory is reserved for GitHub Actions workflow definitions only.

## Rules
- Keep only valid `.yml` or `.yaml` workflow files here.
- Do not store application source code, shell scripts, Android files, HTML, JSON, or documentation in this directory.
- Do not run repository scripts automatically unless their behavior has been reviewed and the workflow uses least-privilege permissions.
- Prefer `contents: read`, `persist-credentials: false`, explicit timeouts, pinned action versions, and manual approvals for deployment or repository writes.
- Never use broad `git add -A` plus automatic push for generated fixes.
- A file with a `.yml` extension is not automatically safe; review its triggers, permissions, secrets, shell commands, and third-party actions.

## Legacy files
75 non-workflow files were moved without changing their contents to `.github/legacy-workflow-assets/`. They are preserved for review and are not automatically executed by GitHub Actions. Some are scripts with potentially destructive behavior. Review each script before running or relocating it into an executable tool directory.

## Validation
Run the repository workflow inventory/audit script from the repository root:
`python scripts/audit_workflows.py`

The audit report is an inventory aid, not a security certification.
