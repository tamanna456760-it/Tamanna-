# ✅ Valid Workflows Registry

This repository contains the following **PRODUCTION-READY** workflows:

## 🚀 Core Workflows

### 1. Auto Sync to Repository
- **File**: `auto-sync-to-repo.yml`
- **Purpose**: Mirror code to external repositories
- **Trigger**: Push to main, hourly cron
- **Status**: ✅ ACTIVE

### 2. Auto Sync Tamanna System
- **File**: `auto-sync.yml`
- **Purpose**: Monitor and sync file changes
- **Trigger**: Push to main, schedule
- **Status**: ✅ ACTIVE

### 3. Auto Fix & Build Pipeline
- **File**: `auto_fix_build.yml`
- **Purpose**: Code formatting, linting, building
- **Trigger**: Push, PR, manual dispatch
- **Status**: ✅ ACTIVE

### 4. Node.js Auto Runner
- **File**: `auto_run.yml`
- **Purpose**: Execute JavaScript files with analytics
- **Trigger**: Push, PR, schedule, manual
- **Status**: ✅ ACTIVE

### 5. BD-King-R7 Android Build
- **File**: `bd-king-r7_powerhub.yml`
- **Purpose**: Build Android APK with quality gates
- **Trigger**: Push, PR, schedule, manual
- **Status**: ✅ ACTIVE

### 6. Bot Configuration
- **File**: `bot.yml`
- **Purpose**: Bot setup and verification
- **Trigger**: Push, manual
- **Status**: ✅ ACTIVE

## ⚠️ Deprecated/Invalid Files

The following files should be REMOVED or moved:

- ❌ All `.java` files → Move to `/android/` or `/src/`
- ❌ All `.py` files → Move to `/scripts/` or `/src/python/`
- ❌ All `.sh` files → Move to `/scripts/` or `/tools/`
- ❌ All `.json` files → Move to `/config/` (except workflows)
- ❌ All `.html` files → Move to `/web/` or `/docs/`
- ❌ All `.xml` files → Move to `/android/` or `/config/`

## 📁 Directory Structure

```
.github/
  workflows/
    ✅ auto-sync-to-repo.yml
    ✅ auto-sync.yml
    ✅ auto_fix_build.yml
    ✅ auto_run.yml
    ✅ bd-king-r7_powerhub.yml
    ✅ bot.yml

config/
  ✅ cloudflare.json
  ✅ dependencies.json
  ✅ engine-config.json
  ✅ vscode-settings.json

scripts/
  → Python scripts
  → Shell scripts
  → Batch files

android/
  → Java files
  → Manifests
  → Resources

src/
  → Source code
  → Python packages
  → Node modules
```

## 🔒 Security Guidelines

✅ DO:
- Store credentials in GitHub Secrets
- Use environment variables for sensitive data
- Review all workflow changes
- Enable branch protection rules

❌ DON'T:
- Commit API keys or tokens
- Store passwords in JSON files
- Hardcode credentials in workflows
- Commit private SSH keys

## ✨ Recent Improvements

- ✅ Fixed security vulnerabilities
- ✅ Reorganized configuration files
- ✅ Enhanced error handling
- ✅ Added comprehensive logging
- ✅ Implemented notifications
- ✅ Improved performance
- ✅ Added scheduling support

---

**Last Updated**: 2026-07-02  
**Status**: Production Ready ✅
