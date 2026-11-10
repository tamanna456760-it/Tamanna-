# Tamanna AI — Script Security Review

Date: 2026-11-10
Branch: main

## Scope and limits

This is a source-code review only. The scripts were not executed. A GitHub code search for the phrase `GitHub Token` returned 30 matches (the search result limit), so this is not yet a complete repository-wide inventory. No credentials were tested and no claim is made that a token-like string is a valid credential.

## Confirmed high-risk patterns

| Path | Observed pattern | Risk |
|---|---|---|
| `runner/shell/check_token.sh` | Hard-coded `TOKEN="tamanna"` sent to GitHub API | Credential-like value embedded in source; remove and use an environment variable or gh auth |
| `runner/shell/tamanna_github_backup.sh` | Reads a token, embeds it in an HTTPS remote URL, removes/replaces origin, then pushes | Token may persist in Git config/logs; can overwrite the configured remote |
| `tamanna_code_editor_runner.sh` | Reads token and embeds it in remote URL; runs user-edited code | Credential exposure and arbitrary code execution |
| `runner/shell/auto_sync_all.sh` | Installs packages, executes discovered Python/Node/Shell/C/Java files, then pushes | Unreviewed code execution and unintended repository writes |
| `runner/shell/bdking_r7_ultra.sh` | Executes discovered source files and all shell scripts; changes permissions and pushes | Broad arbitrary code execution and unintended writes |
| `runner/shell/tamanna_auto_pro.sh` | Changes firewall policy, runs `rsync --delete`, modifies source files, executes code, and pushes | Lockout/data deletion/source mutation and credential exposure |

## Additional search findings

The phrase `GitHub Token` appears in at least 30 indexed search results, including:
- `runner/shell/tamanna_ultra_ai.sh`
- `runner/shell/tamanna_ultra_pro.sh`
- `runner/shell/tamanna_ultra_max.sh`
- `runner/shell/tamanna_autonomous.sh`
- `runner/shell/tamanna_all_in_one.sh`
- `runner/shell/tamanna_multi_user.sh`
- `runner/shell/tamanna_enterprise.sh`
- `runner/shell/tamanna_ultra_24x7.sh`
- `runner/shell/tamanna_full_backup.sh`
- `runner/shell/tamanna_ultra_cloud.sh`
- `runner/shell/tamanna_ultra_secure.sh`
- `runner/shell/tamanna_ultra_pro_cli.sh`
- `runner/shell/tamanna_self_learning.sh`
- `runner/shell/tamanna_ultra_ai_full.sh`
- `runner/shell/tamanna_ultra_extreme.sh`
- `runner/shell/tamanna_ultra_powerhub.sh`
- `runner/shell/tamanna_ultra_fileinfo.sh`
- `runner/shell/tamanna_ultra_advanced.sh`
- `runner/shell/tamanna_ultra_firewall.sh`
- `runner/shell/tamanna_code_auto_comm.sh`
- `runner/shell/tamanna_ultimate_cloud.sh`

Each file needs full-content inspection before any change. Search results alone do not prove that every match embeds credentials in a remote URL.

## Safe remediation standard

1. Preserve original scripts under `trash/security-review/<original-path>` before replacing or disabling anything.
2. Replace embedded-token URL authentication with GitHub CLI (`gh auth login`) or an OS credential helper. Never put tokens in remote URLs, command-line arguments, logs, or source files.
3. Remove hard-coded credential-like values. Read credentials only from a private environment/secret store; do not print them.
4. Do not execute every discovered source file. Run only explicitly allowlisted test/build commands in a sandbox with timeouts and no production credentials.
5. Require explicit confirmation before changing firewall rules, deleting remote files, changing Git remotes, committing, or pushing.
6. Test each replacement with syntax/static checks and a dry run before enabling it.

## Status

- Review report only; no script has been moved, replaced, or executed.
- No credentials have been tested, rotated, or exposed by this review.
- No deployment or production configuration was changed.
- Next safe step: inspect the remaining search hits in batches, then archive originals and propose reviewed replacements with focused tests.


## Follow-up inspection — additional scripts

Five additional files were fetched from `main` and inspected:

| Path | Confirmed findings |
|---|---|
| `runner/shell/tamanna_ultra_ai.sh` | Reads a GitHub token and inserts it in a remote URL; pushes; flushes iptables and sets INPUT/FORWARD default DROP, allowing loopback and TCP 22 only |
| `runner/shell/tamanna_ultra_pro.sh` | Same token-in-remote pattern and firewall reset/default DROP pattern |
| `runner/shell/tamanna_ultra_max.sh` | Token-in-remote pattern and push; no firewall/rsync-delete pattern found in this scan |
| `runner/shell/tamanna_autonomous.sh` | Token-in-remote pattern and push; firewall reset/default DROP; `rsync -avz --delete` |
| `runner/shell/tamanna_all_in_one.sh` | Token-in-remote pattern and push |

The scripts were only fetched and statically inspected; none was executed.

## Invocation / reachability caveat

The five script names also appear in `runner/data/manifest.json`, which is a file inventory and not evidence that the scripts are automatically executed. A search of `Main.py` found a legacy Linux-shell route that calls `tamanna_autonomous.shell(...)`; the surrounding source comments explicitly mark that route as disabled. This does not prove every possible execution path is unreachable. A full call-graph and workflow-invocation audit remains outstanding.

## Newly confirmed references

- `runner/shell/tamanna_ultra_ai.sh` blob: `23ee048509269ba5d9a6dc8340063bbd7e28b010`
- `runner/shell/tamanna_ultra_pro.sh` blob: `8ba78906082cbb9adc4685fbb2cbe13938f67535`
- `runner/shell/tamanna_ultra_max.sh` blob: `fd2e8df3e8a8e5c4ea32251dc764341b1124578c`
- `runner/shell/tamanna_autonomous.sh` blob: `c9388afb0896e9392f57553c2ef2a7002171b752`
- `runner/shell/tamanna_all_in_one.sh` blob: `0855ea1c1601b4351ba8b82bd480c9f5399801fc`


## Further inspection — 15 additional scripts

These files were fetched from `main` and inspected for credential URLs, pushes, firewall edits, and destructive sync:

| Path | Confirmed findings |
|---|---|
| `runner/shell/tamanna_enterprise.sh` | Token-in-remote URL, push, firewall reset/default DROP, `rsync --delete` |
| `runner/shell/tamanna_ultra_24x7.sh` | Token-in-remote URL, push, firewall reset/default DROP |
| `runner/shell/tamanna_full_backup.sh` | Token-in-remote URL and push |
| `runner/shell/tamanna_ultra_cloud.sh` | Token-in-remote URL, push, firewall reset/default DROP |
| `runner/shell/tamanna_ultra_secure.sh` | Malformed Git remote URL containing a documentation URL in the credential segment; push |
| `runner/shell/tamanna_ultra_pro_cli.sh` | Token-in-remote URL, push, firewall reset/default DROP |
| `runner/shell/tamanna_self_learning.sh` | Token-in-remote URL, push, firewall reset/default DROP, `rsync --delete` |
| `runner/shell/tamanna_ultra_ai_full.sh` | Token-in-remote URL, push, firewall reset/default DROP, `rsync --delete` |
| `runner/shell/tamanna_ultra_extreme.sh` | Token-in-remote URL, push, firewall reset/default DROP; Telegram bot token placeholder |
| `runner/shell/tamanna_ultra_powerhub.sh` | Token-in-remote URL and push |
| `runner/shell/tamanna_ultra_fileinfo.sh` | Token-in-remote URL and push |
| `runner/shell/tamanna_ultra_advanced.sh` | Token-in-remote URL, push, firewall reset/default DROP |
| `runner/shell/tamanna_ultra_firewall.sh` | Firewall reset/default DROP; token-in-remote URL and push |
| `runner/shell/tamanna_code_auto_comm.sh` | Token-in-remote URL and push |
| `runner/shell/tamanna_ultimate_cloud.sh` | Token-in-remote URL, push, firewall reset/default DROP, `rsync --delete` |

All 15 were only fetched and statically inspected. None was executed, changed, or moved.

## Current review tally

At least 25 named shell scripts have now been inspected in full or in relevant sections across this report. Common recurring patterns are token-in-remote URLs and automatic pushes; several scripts additionally reset firewall rules and/or use `rsync --delete`. This tally is a scoped review of the identified scripts, not a complete audit of every repository file. Workflow reachability and all callers still require systematic inspection.


## Invocation audit — workflow and Python call sites

### GitHub Actions workflow files

The current repository tree contains 59 `.yml/.yaml` files under `.github/workflows/`. They were inspected in batches for references to the identified risky script names, `runner/shell/`, `git_sync.py`, and direct shell execution. No direct reference to the identified high-risk script paths was found in those workflow YAML files. Some workflows do enumerate tracked `.sh` files for syntax checks (for example, `bash -n`); syntax checking is not execution. A file named `.github/workflows/tamanna_ultra_defense.sh` exists in that directory, but its `.sh` extension means GitHub Actions does not treat it as a workflow YAML file.

### Python call-site findings

- `runner/python/git_sync.py` defines `git_commit_push()` using `os.system` for `git add .`, `git commit`, and `git push`. Repository code search found no caller of that function by name. This is not proof that it is never invoked dynamically.
- `runner/python/synce.py` has its own `git_sync` function that calls `subprocess.run` for add/commit/push. It also has a main/monitor path that calls that function. This is an active code path if the module is launched with a configuration that enables it; it should be treated as an automatic repository-write capability.
- `runner/python/auto_sync_monitor.py` defines a `git_sync()` that runs add/commit/push and calls it from its monitor loop. It is an automatic repository-write capability if that monitor is started.
- `runner/python/tamannna_master.py` contains a subprocess helper using `shell=True` and a Git sync function. It needs a separate command-injection review and confirmation of its launch path.
- `runner/python/powerhub_master.py` reports automatic script execution and automatic Git sync as false in its returned status; this alone does not establish all surrounding system paths.
- `Main.py` includes a legacy Linux shell endpoint whose original implementation calls `tamanna_autonomous.shell(...)`; source comments mark the route disabled. The module path/import and full route registration need further tracing before asserting complete unreachability.

### Conclusion and limits

The inspected workflow YAML files do not show direct calls to the identified risky shell scripts. However, Python monitor modules provide independent automatic Git push paths when launched. This is a static search/review, not runtime tracing; dynamic imports, external launchers, cron jobs, user-triggered routes, and other indirect invocations have not all been ruled out. Do not run the scripts or sync monitors on a production checkout until reviewed and constrained.


## Remediation applied — 2026-11-10

The following changes were committed on `main` after the static invocation audit:

- `runner/python/synce.py`: removed the duplicate entry point and broken bare function reference. Status monitoring is read-only. Git sync now requires the explicit `--sync` command, `allow_git_push: true`, an explicit non-empty `sync_paths` allowlist, and the `main` branch. It stages only allowlisted paths.
- `runner/python/auto_sync_monitor.py`: removed automatic file relocation and automatic Git staging/commit/push from the monitor loop. Normal mode only inventories candidate files; a one-shot push requires `--sync`, `TAMANNA_ENABLE_GIT_PUSH=1`, `TAMANNA_SYNC_PATHS`, and the `main` branch.
- `runner/python/tamannna_master.py`: replaced `shell=True` command strings with argument-list subprocess calls. Backup now uses Python copy/archive operations and no longer invokes `rsync --delete`. Git sync is an explicit CLI action, restricted to `main` and configured `sync_paths`; it no longer stages the entire repository by default or suppresses Git errors.
- `runner/python/git_sync.py`: removed `os.system`; push now requires explicit `allow_push=True`, a non-empty relative-path allowlist, and the `main` branch.
- Added `tests/test_sync_security.py` to cover default-deny behavior, path traversal rejection, shell-free command invocation, and removal of the automatic file mover.

These changes reduce accidental execution and broad staging risk. They do not prove that every possible launcher or dynamic call path in the repository has been eliminated. The new regression tests and repository CI must pass before treating the remediation as verified. Existing configurations that relied on implicit automatic pushes will now need deliberate review and explicit opt-in configuration.


### Follow-up hardening — explicit sync path allowlists

A second review found that the first allowlist implementation still accepted broad pathspecs such as `.` and wildcard patterns, and could accept explicitly named credential files. The sync helpers now reject repository-wide paths, glob/pathspec metacharacters, parent traversal, common secret names (including `.env*`, token files and credential JSON), and private-key/certificate extensions. The master sync helper also validates the configured remote as a simple Git remote name before passing it to Git.

Regression coverage was expanded for repository-wide pathspecs, secret filenames, and wildcard pathspecs. These controls reduce accidental secret staging, but they cannot guarantee that an innocently named file contains no secret; review the actual staged diff before authorizing a push.


## Additional Python automation remediation — PowerHub agent and schedulers

Further repository search identified additional shell-based automation paths:

- `runner/python/agent.py` used `shell=True` for configured fix/build commands and Git operations, defaulted to a non-main automation branch, and included hard reset / broad staging behavior. It is now shell-free, restricted to the checked-out `main` branch, refuses shell operators and shell `-c` command strings, removes hard reset/branch creation, and defaults to no command execution or Git push. Running configured commands requires `allow_commands: true`; pushing additionally requires both `push_changes: true` and `allow_git_push: true`, plus explicit safe `sync_paths`. Marker files are updated only when included in that allowlist.
- `runner/python/auto_sync.py` and `runner/python/cloud_auto_sync.py` no longer use `os.system`; they use argument-list subprocess calls, timeouts, and report missing child scripts. The expected `tamanna_book_sync.py` and `tamanna_drive_sync.py` were not present in the repository tree at review time, so those scheduled jobs will report missing scripts rather than silently succeed.
- `runner/python/git_clone_update.py` now uses the canonical GitHub clone URL, clones only `main`, refuses to overwrite a dirty checkout or update a non-main branch, and uses `git pull --ff-only` without shell commands or changing the process working directory.
- Expanded `tests/test_sync_security.py` to cover shell operator rejection, shell command-string rejection, allowlist secret-path rejection, and verification that the agent launches subprocesses with `shell=False`.

These are code changes, not a production rollout. Agent execution remains disabled unless its external YAML configuration explicitly sets `enabled: true`. Review that external configuration before enabling it. CI must complete successfully before these changes can be considered test-verified.


## Drive and local mirror safeguards — follow-up

Additional sync-related files were reviewed and hardened:

- `runner/python/tamanna_sync.py`: removed import-time credential loading and the unconditional infinite upload loop. Drive sync now requires `TAMANNA_ENABLE_DRIVE_SYNC=1`, an explicit upload folder and credential-file path, stores a local SHA-256 state file outside the upload folder, ignores symlinks and common secret/key files, and uploads changed PDF files only. Google client dependencies are imported only after explicit opt-in.
- `runner/python/tamanna_derive_sync.py`: removed unsafe `pickle.load` / `pickle.dump` credential storage. It now uses Google's JSON authorized-user credential format, keeps token/client files outside the PDF source folder, and requires the same explicit Drive-sync opt-in.
- `runner/python/tamanna_bd-king-r7_sunc.py`: excludes common secret files and symlinks from the local mirror, validates resolved paths remain inside the intended roots, disables mirror deletions unless `TAMANNA_ALLOW_MIRROR_DELETE=1`, and disables build commands unless `TAMANNA_ALLOW_BUILD_COMMANDS=1`. Build commands must be argument arrays and are launched without a shell.
- `runner/python/enable_auto_sync.py`: no longer activates legacy auto-sync at import time. It requires `TAMANNA_ENABLE_LEGACY_MONITOR=1` and explicitly disables Git auto-commit and cloud backup.
- `tests/test_sync_security.py`: consolidated duplicate test definitions and added regression coverage for Drive default-deny behavior, credential exclusions, local mirror symlink/secret filtering, and disabled destructive sync behavior.

Google Drive sync remains an optional external integration and is not enabled by these code changes. Configure credentials only in the user's local environment or a secret store; never commit them. The repository CI result remains the final check for syntax, imports, and test compatibility.


## Drive sync state-file hardening — 2026-11-10

A follow-up review of `runner/python/tamanna_sync.py` found that the configurable local state-file path was not checked against the Google service-account credentials path. A mistaken `TAMANNA_DRIVE_SYNC_STATE` value could therefore overwrite the credentials file after an upload cycle. The state path also lacked an explicit symlink rejection.

- Added `validate_state_file()` to reject symlink state paths, the credentials file itself, paths inside the upload folder, paths that would replace the upload folder, and existing non-regular-file targets.
- `sync_once()` now validates the state path before loading or writing it.
- Added regression tests for a valid external state path, credentials overwrite, symlink, and upload-folder containment.

Commits: `886cc0284cbf3081adedec6d37bb4b2bcea8f636` (code), `8c9aa25b45f52352012199d5dfc9c0b28c120b51` (tests).

This is a targeted static hardening change. The new CI runs are queued; no test-pass claim is made until GitHub Actions reports completion. Drive sync remains disabled unless explicitly opted in.


## Shell-free network diagnostics — 2026-11-10

Two small Python network diagnostic utilities were found constructing ping commands through `os.system`.

- `runner/python/ping.py` now invokes a fixed host with an argument-list subprocess, a five-second timeout, and explicit missing-utility/timeout handling.
- `runner/python/tamanna_system.py` now validates the host string and uses platform-specific argument arrays with `shell=False` (the subprocess default), a five-second timeout, and a boolean result.
- Added tests verifying bounded execution, no shell option, and rejection of whitespace/shell-injection host input.

Commits: `f66d97412cdb2ff510f0ef5707b33703a5da53f1` (ping utility), `6d0b287a1e82c73a4b55004fd960943595c02380` (system diagnostic), `858d28dde9b52dcdf0cbbd0a63c21a69a7f066a7` (tests).

The repository-wide search still reports matches in vendored/editor code and other legacy automation. Search matches are not automatically vulnerabilities; inspect ownership and call paths before editing vendor code. CI for these commits is pending at the time of this update.


## Node.js Git automation hardening — 2026-11-10

A focused review found three additional Node.js sync modules using broad Git operations:

- `runner/node/git.js` previously ran `git add .`, committed, and pushed unconditionally. It now defaults to no push, requires `TAMANNA_ENABLE_GIT_PUSH=1` and an exact `TAMANNA_SYNC_PATHS` allowlist, rejects common secret paths and unsafe path syntax, requires the `main` branch and an `origin` remote, and stages only changed allowlisted files.
- `runner/node/github.js` and `runner/node/github-sync.js` previously staged the entire working tree and pushed directly. Both now delegate to the single hardened `gitPush()` policy.
- `runner/node/ai-sync.js` previously called the OpenAI Chat Completions API every minute and then staged/committed/pushed the entire repository. It is now an API-free, read-only Git status monitor; it does not pull, stage, commit, or push.

Commits: `189cbdd13292791ea868173f53ec0120159996eb` (central Git push policy), `384d1d110c536ae57a7327a4807cb7c0e0dae706` (`github.js`), `a55a2a1896ed60df3a49dbf54a9012ee10ac4d8a` (`github-sync.js`), `4fa66e46b954e85d1e35fafc70f091bb505780c4` (`ai-sync.js`).

The three files were fetched again from `main` and their content SHAs verified. GitHub Actions for the latest commit were queued/pending at review time; no test-pass claim is made. The allowlist is a path-level safeguard, not content inspection: review staged diffs before enabling any push.


## Telegram sync module-format repair — 2026-11-10

The root `package.json` declares CommonJS, but the Telegram sync call path used ES Module syntax. The following three files were converted to CommonJS while preserving the existing safe-push policy:

- `runner/node/git.js`: CommonJS exports; still defaults to no push and requires `TAMANNA_ENABLE_GIT_PUSH=1`, exact `TAMANNA_SYNC_PATHS`, main branch, and origin remote.
- `runner/node/github.js`: CommonJS wrapper that delegates to the hardened `gitPush()`.
- `runner/node/bot.js`: CommonJS imports now point to the existing `./ai.js` local-only adapter and `./github.js`; Telegram `/sync` retains the `TAMANNA_TELEGRAM_ADMIN_IDS` sender allowlist.

Commits:
- `1a273f88a22e25ca99176e617871824c3d4acdcd` — Git module conversion.
- `1777d4bffcc57a7b86b6941934bbed6f20fd12b7` — GitHub wrapper conversion.
- `fd3ba391f05ba054ad1e3bac8813cfe576fd4f2a` — Telegram bot import repair.

The three updated files were fetched again from `main` and their blob SHAs verified. GitHub Actions for the latest commit were queued/pending at the time of this report update; no runtime, dependency-install, or test-pass claim is made.

### Remaining blockers

- The `run.js` and `run..js` orchestrators still import multiple absent nested modules; they have not been changed.
- The repo-level `package.json` currently declares no dependency list in the inspected content. Availability/version compatibility of `simple-git`, `dotenv`, and `node-telegram-bot-api` has not been verified.
- `runner/node/git.js` targets `./project`; confirm that this directory is the intended Git checkout before enabling any push. Keep push disabled until this and the allowlisted file contents are reviewed.
- The local AI adapter intentionally returns an unavailable error until a local model or knowledge database is configured. The Telegram bot must not be described as a functioning AI assistant yet.

No secrets were added. No token, bot, local server, or Git push was executed.
