# .github/workflows Directory Audit

**Audited ref:** `security/full-system-hardening`  
**Audit mode:** read-only inventory; no source files moved or deleted.

## Inventory snapshot

The GitHub Contents API returned 142 direct entries in `.github/workflows/` on the audited branch.

| Classification by filename | Count |
|---|---:|
| Valid `.yml` extension | 66 |
| Valid `.yaml` extension | 1 |
| Non-workflow or malformed extension | 75 |
| **Total** | **142** |

The 75 non-workflow entries include source files and assets with these extensions:

| Extension | Count |
|---|---:|
| `.java` | 9 |
| `.sh` | 16 |
| `.js` | 13 |
| `.py` | 10 |
| `.bat` | 7 |
| `.xml` | 3 |
| `.json` | 4 |
| `.html` | 4 |
| `.md` | 2 |
| `.dart` | 1 |
| `.bad` | 1 |
| `.text` | 1 |
| no extension | 2 |
| malformed `.yml`-like names | 2 |
| **Total** | **75** |

GitHub Actions only discovers workflow definitions with a `.yml` or `.yaml` extension directly in this directory. A valid extension alone does not prove that a file is a valid or safe workflow.

## Quarantined automations

The following workflows were changed on this security branch to manual-only quarantine stubs. They no longer check out or execute repository source, modify files, commit, push, or deploy:

- `tamanna_ai_scan.yml` — formatted files in place and pushed changes.
- `tamanna-run.yml` — executed the app and pushed log files.
- `tamanna-head-run.yml` — executed a repository script and pushed a manifest.
- `bd_king_r7-auto-sync.yml` — auto-fixed code and pushed to the repository.
- `auto_upgrade.yml` — automatically upgraded dependencies and ran server/test commands with a failure bypass.
- `auto_fix_build.yml` — created and executed a formatting/build script that could rewrite source files.
- `job.yml` — had a force-commit input and staged all repository changes.
- `tamanna-auto-heal.yml` — replaced empty/corrupt files with generic placeholders and pushed to main.
- `auto-run.yml` — executed repository Python files selected by a user-provided pattern.
- `auto_run.yml` — executed repository JavaScript files after dependency installation.
- `ai-system.yml` — created dummy scripts and executed repository code on a frequent schedule.
- `real-ai.yml` — sent repository scan/debug inputs to an external AI service using a secret key; keep disabled until data-sharing approval and redaction controls exist.

Quarantine is temporary. Reintroduce any capability only after a reviewed design with least-privilege permissions, explicit approval for mutations, bounded execution, and tests.

## Remaining remediation

1. Review all 67 YAML candidates for syntax, trigger safety, action pinning, permissions, secret exposure, and deployment behavior.
2. Review all 75 non-workflow files for imports, path references, build references, and runtime use before moving them.
3. Move source files to suitable directories in small, testable commits. Do not delete files based on extension alone.
4. Keep production deployment separate from validation and require protected-environment approval.
5. Run the workflow inventory and credential scanner in the read-only validation workflow; inspect the uploaded JSON artifact before cleanup.

## Tools

Run locally:

```bash
python scripts/audit_workflow_directory.py --root .github/workflows --output workflow-directory-inventory.json
python scripts/security_secret_scan.py --root .
python -m pytest -q tests/test_access_control.py
```

The credential scanner is pattern-based and does not inspect Git history. A detected credential must be revoked at its provider even after the file is changed or removed. A clean scan is not proof that no secret exists.
