# Tamanna AI Ethical Hacking & Defensive Security

## Purpose

This project uses "ethical hacking" to mean authorized defensive review of Tamanna-owned code, servers, deployment configuration, and domains. The default posture is read-only, monitor-only, and fail-closed.

## Implemented safeguards

- 37 legacy shell scripts with unsafe credential handling, broad code execution, automatic Git remote replacement/push, or host-level firewall/account changes were replaced with fail-closed safety guards.
- Original versions remain recoverable from Git history; they were not silently erased.
- `scripts/check_legacy_shell_safety.py` verifies that the guards remain in place.
- `endpoint_security/` provides monitor-only posture checks, SHA-256 file-integrity support, redacted event reporting, and policy validation. Destructive enforcement remains disabled.
- The `Tamanna-server` repository includes a read-only configuration audit and a GitHub Actions workflow for tests and dependency auditing.

## Safe operating rules

1. Test only repositories, hosts, domains, and services owned by Tamanna or covered by explicit written authorization.
2. Start with source/configuration review, dependency auditing, TLS/header review, and authenticated health checks.
3. Do not run unreviewed source files, bulk shell scripts, unknown binaries, or commands discovered by a scanner.
4. Never automatically flush firewall rules, change SSH policy, delete users, remove SSH keys, quarantine/delete files, or change Git remotes.
5. Do not place tokens in command-line arguments, URLs, logs, source files, or Git configuration. Use a private environment file or a secrets manager.
6. Do not store passwords, tokens, full environment variables, or command lines in security telemetry.
7. Require a human approval and a verified backup before any production configuration change.

## Current audit findings and actions

- Several legacy scripts prompted for a GitHub token and embedded it in an HTTPS remote URL. A token-like placeholder was also hard-coded in `runner/shell/check_token.sh`. The value was not tested as a valid credential. If a real token was ever entered into one of these scripts, revoke it and inspect local Git remote configuration and shell history.
- Some legacy scripts ran every discovered Python/Node/Shell/C/Java file, committed and pushed automatically, or reset firewall/SSH/user settings. These scripts are now inert safety guards. The old source remains in Git history for recovery and review, not for execution.
- The server's Nginx Content-Security-Policy currently allows `unsafe-inline` for scripts/styles. This is a medium-priority hardening item; migrate inline code to nonce/hash-based CSP before removing that allowance, otherwise the website may break.
- The planned domain configuration is present in source, but live domain registration, DNS resolution, TLS, origin reachability, and production deployment were not verified in this audit.

## Validation

From the repository root:

```sh
python scripts/check_legacy_shell_safety.py
python -m json.tool endpoint_security/endpoint_config.json >/dev/null
python -m endpoint_security.config_validator
python -m endpoint_security.policy_checker
python -m unittest endpoint_security.tests.test_posture_pipeline endpoint_security.tests.test_posture_integration -v
```

The CI workflow runs these checks on pushes and pull requests to `main`. A passing static audit is not a penetration test and does not certify the live VPS or website.
