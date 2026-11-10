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
