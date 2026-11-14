# Repository Architecture Audit — 2026-11-15

## Scope and evidence

This is a GitHub tree-level audit of the main branch. It does not claim that application code or deployment was executed.

- Main application repository: Tamanna-
- Root contains the Main.py and run_server.py entrypoints, tamanna_ai package, root chat/admin frontend, Android project, scripts, tests, Cloudflare adapter and deployment files.
- The main Python package already has domain directories for API, core, AI, auth, memory, knowledge, security, tools, integrations and workflows.
- The repository has a TRASH.md register. Existing quarantine/runtime configuration/backup candidates must be preserved until reference checks are complete.

## Confirmed structural issues

### GitHub Actions directory

The current .github/workflows directory contains **136 entries**:
- **65** files ending in .yml or .yaml.
- **71** non-YAML files, including Java, Python, shell, batch, JavaScript, HTML, JSON, Dart, text and Markdown files.

Only workflow definitions belong directly in .github/workflows. The other files may be helper code or legacy artifacts; do not move them blindly. Search workflow run/uses references, imports, package scripts and documentation before relocating each item to .github/scripts/, scripts/ or its owning source folder.

### Workflow overlap

docs/CI_WORKFLOWS_REVIEW.md already records overlapping build, auto-run, sync and security workflows. Keep the review inventory. Consolidation must compare triggers, permissions, secrets, jobs and artifacts before disabling anything.

### Legacy and experimental paths

The root contains multiple historical/experimental directories and unusual names. Examples include ai system, .snapshots, .tamanna_backup, ROOT, runner, tamanna_ai_advanced and legacy security/network directories. Their names alone do not prove they are unused. Preserve them pending import/reference and workflow analysis.

### Architecture documentation

The former docs/system_architecture.mmd was a stale plain-text folder sketch. It has been replaced with a Mermaid topology. The canonical written architecture is docs/ARCHITECTURE.md and folder policy is docs/REPOSITORY_STRUCTURE.md.

## Safe work completed in this audit

- Added docs/ARCHITECTURE.md.
- Added docs/REPOSITORY_STRUCTURE.md.
- Replaced docs/system_architecture.mmd with the current client/edge/server/local-AI/data flow.
- Added architecture and repository-structure links to README.md.
- No application source, runtime configuration, credentials, backup archives or production deployment files were moved or deleted.

## Remaining implementation phases

1. Build a machine-readable inventory of all tracked paths and classify source, tests, generated artifacts, backups, runtime data and quarantine candidates.
2. Trace all 71 non-YAML workflow-directory entries to their callers; move only verified helper/source files and preserve original paths in a quarantine manifest.
3. Compare all 65 YAML workflows and retain one canonical shared quality gate plus justified specialist workflows.
4. Audit imports and module duplication under tamanna_ai; add missing package markers only where import semantics require them.
5. Make one tested subsystem refactor at a time; keep Main.py compatibility until all callers and deployment commands are migrated.
6. Audit Android wrapper, manifest, resources and debug/release build independently.
7. Verify backend chat, guest access policy, user isolation, local model connection, database persistence and admin authorization.
8. Verify Docker build, health endpoint, HTTPS routing and backup restore on the actual host.

## Verification status

GitHub tree and documentation writes were inspected. No Python test suite, Node build, Android build, Docker runtime or live server test was executed in this audit. Therefore runtime and deployment status remain unverified.


## Update — workflow directory cleanup

A follow-up cleanup was committed on 2026-11-15.

- Moved all 71 non-YAML files from `.github/workflows/` to `trash/quarantine-2026-11-15/.github/workflows/` without changing their blob contents.
- Confirmed that 65 YAML workflow definitions remain in `.github/workflows/` and zero non-YAML files remain there.
- Updated `scripts/check_legacy_shell_safety.py` to validate the preserved quarantine copies of its five guarded shell files.
- Added a path/SHA inventory at `trash/quarantine-2026-11-15/MANIFEST.md` and updated `TRASH.md`.
- No source file was permanently deleted.

The wider repository still contains legacy/mixed-purpose directories and 102 build/generated-looking tracked paths. These require a separate per-project dependency review; they were not bulk-moved because some may be required by the nested .NET/Android projects or legacy runtime. The next cleanup pass should classify these before moving them.

**Post-change CI:** GitHub Actions runs were created for the cleanup commit, but the observed runs were queued/in progress at the time of this update. Runtime tests and build success are not yet confirmed.


## 2026-11-15 whole-repository inventory update

Fresh recursive GitHub tree inspection (main branches):

| Repository | Tracked paths | Broad generated/runtime pattern matches | Notes |
|---|---:|---:|---|
| `Tamanna-` | 3,314 | 238 | Includes nested .NET/Android build trees, logs, databases, bytecode and other mixed legacy paths; pattern matches include directories and are not a deletion list |
| `Tamanna-server` | 292 | 34 | Root-level .NET binaries/MSBuild outputs, Python bytecode and a tracked report database need dependency review |
| `tamanna-website` | 31 | 0 | Static site structure is already separated into HTML, CSS, JS, assets and tests |

The expected website repository name was corrected from `tamanna-wabside` to the existing `tamanna-website` in the architecture and repository-structure documents. The `Tamanna-server` boundary document now records that `Wabsite/` remains a deployment copy because deployment documentation references it. Do not remove that copy until synchronization and deployment references are verified.

A malformed escaped-newline entry in the main repository `.gitignore` was corrected in commit `54eed4d3156a0bee564928f9bbc44b744d019bdb`; the `data/github-knowledge/` runtime directory now has its own ignore rule.

**Important:** the broad generated/runtime counts are triage signals, not proof that every matched path is disposable. No source tree, .NET/Android build output, database, backup archive, runtime config or production file was bulk-moved in this pass. All existing quarantine content remains preserved. CI for these latest documentation/configuration commits must be checked separately before calling the changes validated.
