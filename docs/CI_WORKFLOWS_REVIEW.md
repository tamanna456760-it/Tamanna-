# GitHub Actions workflow review

## Canonical server workflow
- `.github/workflows/Build.yml` — intended canonical server CI: space-safe Python compilation, Bash syntax, JSON parsing, dependency closure, `import Main`, pytest, Docker build, and container HTTP smoke tests.

## Overlapping Python/server validation workflows — review for consolidation
- `.github/workflows/test.yml`
- `.github/workflows/repository-verification.yml`
- `.github/workflows/tamanna-run.yml`
- `.github/workflows/tamanna-main-run.yml`
- `.github/workflows/tamanna-health-check.yml`
- `.github/workflows/auto_fix_build.yml`
- `.github/workflows/auto-lint-and-fix.yml`
- `.github/workflows/Auto.yml`

## Overlapping auto-build, run, and sync workflows — review before disabling
- `.github/workflows/auto-run.yml`
- `.github/workflows/auto_run.yml`
- `.github/workflows/auto_bulde.yml`
- `.github/workflows/auto-upgrade.yml`
- `.github/workflows/auto_upgrade.yml`
- `.github/workflows/running.yml`
- `.github/workflows/run-ai.yml`
- `.github/workflows/real-ai.yml`
- `.github/workflows/tamanna-ai-altimate.yml`
- `.github/workflows/tamanna-auto-run.yml`
- `.github/workflows/tamanna-auto-sync.yml`
- `.github/workflows/tamanna-head-run.yml`
- `.github/workflows/powerhub_ultra-sync.yml`
- `.github/workflows/auto-sync-bd-king-r7.yml`
- `.github/workflows/auto-sync-to-repo.yml`
- `.github/workflows/bd_king_r7-auto-sync.yml`
- `.github/workflows/tamanna_full_system.yml`
- `.github/workflows/platform_backend.yml`

## Security and specialist workflows — retain unless their coverage is proven duplicated
- `.github/workflows/codeql.yml`
- `.github/workflows/security-checks.yml`
- `.github/workflows/tamanna-security-audit.yml`
- `.github/workflows/tamanna-full-defense.yml`
- `.github/workflows/tamanna-full-audit.yml`
- `.github/workflows/tamanna-repair-audit.yml`
- `.github/workflows/tamanna-ids-security.yml`
- `.github/workflows/tamanna-ids-tests.yml`
- `.github/workflows/tamanna-endpoint-security-tests.yml`
- `.github/workflows/tamanna-posture-archive-tests.yml`
- `.github/workflows/tamanna-waf-tests.yml`
- `.github/workflows/tamanna-apk-build.yml`

## Other workflows — review purpose and ownership
- `.github/workflows/ai-debug.yml`
- `.github/workflows/analyzer.yml`
- `.github/workflows/auto-clean.yml`
- `.github/workflows/auto-heal.yml`
- `.github/workflows/auto-heal_v2.yml`
- `.github/workflows/bd-king-r7_powerhub.yml`
- `.github/workflows/deploy.yml`
- `.github/workflows/deploy_dev.yml`
- `.github/workflows/domain-check.yml`
- `.github/workflows/download.yml`
- `.github/workflows/node.js.yml`
- `.github/workflows/pages.yml`
- `.github/workflows/setup.yml`
- `.github/workflows/smart-analyzer.yml`

**No workflow was deleted or disabled in this change.** The list is a review inventory, not a claim that every listed workflow is functionally duplicate.
