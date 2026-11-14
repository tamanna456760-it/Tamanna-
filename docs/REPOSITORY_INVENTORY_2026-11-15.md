# Tamanna- repository inventory and safe migration plan

**Snapshot:** 2026-11-15  
**Branch:** `main`  
**Baseline commit:** `fad38d195d0e7cf39e913d0916494536a1b8c793`  
**Purpose:** Record actual repository contents and prevent unsafe bulk moves.

## 1. Repository boundaries

- `Tamanna-`: application source, Python AI package, browser client, Android client, tests, docs and CI.
- `Tamanna-server`: central API, server runtime, database integration, Docker and VPS deployment.
- Public website: separate website repository only. Do not copy backend or Android code into it.

## 2. Inventory snapshot

- Tracked files: **2904**.
- Python package `tamanna_ai/`: **221** files across several existing subpackages.
- Android app `tamanna-ai-app/`: **114** files.
- Android `src/main/`: **108** files; active configured Java/Kotlin source directory `src/build/java/`: **1** file(s).
- Legacy `runner/`: **1299** files; extensions: .py=1020, .sh=106, .json=89, .js=54, .html=27, .bak=2, .yml=1.
- Top-level code-heavy folders include `tamanna_ai/`, `runner/`, `bd-king-r7/`, `firewall/`, `endpoint_security/`, `ids/`, `tests/`, and `scripts/`.

The `runner/` and `bd-king-r7/` trees contain mixed source, configuration, documentation, backups and generated output. They must be audited file-by-file; do not move either entire tree into `trash/`.

## 3. Changes completed

- Workflow helper/non-YAML files removed from `.github/workflows/` and preserved in `trash/quarantine-2026-11-15/.github/workflows/`.
- Root workflow moved to `.github/workflows/master_sync.yml`.
- Runtime logs moved to `logs/archive/`; backup archive moved to `data/backups/`.
- 150 tracked .NET `bin/` and `obj/` outputs preserved under `trash/quarantine-2026-11-15/generated-and-unintegrated/build-output/`.
- Three files from an unintegrated `device/` prototype preserved under `trash/quarantine-2026-11-15/generated-and-unintegrated/device-prototype/`. The prototype recursively enumerated device storage and uploaded files to Firebase; it is not part of the supported Android app and must not be enabled without a new security review.
- Six malformed/ambiguous paths preserved in quarantine with a manifest.
- No permanent deletion.

## 4. Canonical module ownership

| Concern | Current canonical location | Notes |
|---|---|---|
| Python application | `tamanna_ai/` | Existing package; migrate legacy modules into it only after import/reference checks |
| Persistence/database | `tamanna_ai/persistence/` | Existing SQLAlchemy layer; do not create a competing database implementation |
| Knowledge retrieval | `tamanna_ai/knowledge/` | Existing local vector store and importers |
| Conversation memory | `tamanna_ai/memory/` | Existing memory modules; inspect JSON files before moving or changing |
| Core lifecycle | `tamanna_ai/core/` and `tamanna_ai/runtime/` | Consolidate only after dependency graph review |
| Security | `tamanna_ai/security/`, `firewall/`, `endpoint_security/`, `ids/`, `waf/` | Keep distinct domains until APIs and ownership are mapped |
| Tools | `tamanna_ai/tools/` | Permission-scoped tool implementations |
| Integrations | `tamanna_ai/integrations/` | Provider and server adapters |
| Android | `tamanna-ai-app/` | Gradle project; do not mix in the unrelated root `device/` prototype |
| Static client | root `index.html`, `admin.html`, `css/`, `js/`, `assets/` | Static UI only |
| CI | `.github/workflows/` | YAML workflows only; helpers belong in `scripts/` or `.github/scripts/` |

## 5. Missing target directories

- `tamanna_ai/database/` is not present. The working persistence implementation is `tamanna_ai/persistence/`; the new directory README documents this mapping and prevents a duplicate database layer.
- `tamanna_ai/observability/` is not present. Existing reporting/runtime/logging code is distributed across `tamanna_ai/reports/`, `tamanna_ai/runtime/` and `logs/`; the new README documents the target boundary without inventing an unimplemented telemetry API.

## 6. Android findings — action required before consolidation

- `app/build.gradle` configures `sourceSets.main.java.srcDirs = ["src/build/java"]`.
- That directory currently contains **1** source file(s), while `src/main/` contains **108** files. Most of the latter are therefore legacy/experimental and are not part of the configured app source set.
- Two additional manifest-like files have whitespace in their names; only `src/main/AndroidManifest.xml` is the recognized manifest.
- Do not enable all legacy Android files by changing source sets wholesale: the tree contains overlapping activity/API names and numbered experimental modules. First build an explicit module map and compile one tested activity at a time.

## 7. Next safe migration order

1. Inspect all references/imports and tests for one subsystem.
2. Identify one canonical implementation and duplicate candidates.
3. Add/adjust tests before moving files.
4. Move only the verified files, update imports/workflow/Docker/docs references in the same commit.
5. Run Python tests, frontend tests, Android debug and release builds, and server CI independently.
6. Quarantine unreferenced files with original path, SHA and reason. Never delete without explicit approval.

## 8. Verification status

The main-repository workflows on the preceding audited commit completed successfully. The current snapshot has a newer commit and must be rechecked independently before claiming green status. The server CI on its latest observed commit failed in the production-container smoke test and .NET build; website tests and the server security audit passed. See each repository's Actions page for live results.

- Main Actions: https://github.com/tamanna456760-it/Tamanna-/actions
- Server Actions: https://github.com/tamanna456760-it/Tamanna-server/actions
