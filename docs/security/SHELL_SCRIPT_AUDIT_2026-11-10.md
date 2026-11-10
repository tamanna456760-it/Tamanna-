# Tamanna AI — Legacy Shell Script Audit

Date: 2026-11-10
Branch: main
Scope: Static source review only. No shell script was executed.

## Confirmed findings

| File | Finding | Risk |
|---|---|---|
| `runner/shell/tamanna_github_backup.sh` | Generated backup script runs every root-level Python, Node, and shell file; stages the whole checkout; replaces `origin`; puts a token in the HTTPS remote URL; pushes. | Arbitrary code execution, broad staging, credential persistence, remote replacement. |
| `runner/shell/check_token.sh` | Sends the literal `tamanna` as a GitHub API token. | Credential-like hardcoding and unnecessary outbound request. It is not established to be a valid credential. |
| `runner/shell/auto_sync_all.sh` | Generated script discovers and executes Python/Node/shell/C/Java files, then stages all files, replaces `origin`, and pushes using a tokenized URL. | Unreviewed code execution, unintended repository writes, credential persistence. |
| `runner/shell/bdking_r7_ultra.sh` | Generated script chmods every shell script, runs discovered Python/Node/shell/C/Java files, then broadly stages and pushes. | Broad code execution, permission changes, unintended writes. |
| `runner/shell/tamanna_auto_pro.sh` | Generated script changes all directory/file permissions, rewrites Python source, runs discovered code, flushes firewall rules and sets INPUT/FORWARD DROP, runs `rsync --delete`, replaces Git remote and pushes with token URL; also starts a listener. | Data loss, SSH/network lockout, source corruption, arbitrary code execution, credential exposure, unintended network service. |
| `tamanna_code_editor_runner.sh` | Generated editor runner executes newly edited code immediately, stages all files, replaces `origin`, and pushes using a tokenized URL. | Arbitrary code execution and credential persistence. |

## Important interpretation

Several files begin with a `cat > ... << 'EOF'` heredoc. They are generator scripts: executing the outer file writes an inner script to disk. This review inspected the generated payload; it did not execute either layer.

## Reference / invocation search

Exact-name repository searches found the files in the source tree, the inventory at `runner/data/manifest.json`, and/or security documentation. The search results did not establish a live workflow or application call site for these six files. This is not a complete call-graph proof; dynamic invocation and user-local copies remain possible.

## Safe next steps

1. Preserve originals before changing any generator.
2. Replace dangerous generated payloads with safe, opt-in operations: no source auto-execution, no chmod sweep, no firewall reset, no destructive rsync, no tokenized remote URL, and no implicit push.
3. Use the existing guarded Git sync module and explicit path allowlists for any future sync.
4. Keep the legacy generators disabled until replacement scripts pass syntax and regression tests.
5. Do not run these scripts on a real device or VPS during review.

## Status

- Static review only; no scripts executed.
- No credentials tested; no evidence that the literal placeholder is a valid token.
- No shell script, firewall, Git remote, or deployment configuration modified by this audit.
- Original scripts remain in place pending a non-destructive remediation plan.
