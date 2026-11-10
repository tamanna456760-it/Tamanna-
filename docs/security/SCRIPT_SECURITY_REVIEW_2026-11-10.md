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
