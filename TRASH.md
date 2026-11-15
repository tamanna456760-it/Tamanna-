# Tamanna AI Repository — Trash Review Register

**Repository:** `tamanna456760-it/Tamanna-`  
**Branch:** `main`  
**Reviewed commit:** `e96dc0505690cbc21a06ab534a0fec2d5a996001`

এই ফাইলটি সম্ভাব্য অপ্রয়োজনীয়, পুরোনো, ভুল নামে সংরক্ষিত বা GitHub Actions-এর বাইরে থাকা ফাইলগুলোর নিরাপদ তালিকা। এখানে তালিকাভুক্ত করা মানেই ফাইলগুলো মুছে ফেলা বা কার্যকর repository থেকে সরিয়ে ফেলা নয়। প্রয়োজনীয়তা ও dependency যাচাই না করে কোনো কার্যকর কোড, workflow, backup বা configuration সরানো হবে না।

## 1. Quarantine candidates

| বর্তমান path | প্রাথমিক পর্যবেক্ষণ | প্রস্তাবিত ব্যবস্থা |
|---|---|---|
| `.github/workflows/bash script.bad` | Bitbucket Pipelines-ধাঁচের YAML; GitHub Actions workflow নয় এবং extension-ও অস্বাভাবিক | ব্যবহৃত না হলে `trash/`-এ সংরক্ষণ |
| `.github/workflows/build-tamanna-apk.yml\nYAML` | ফাইলনামে newline ও অতিরিক্ত `YAML`; একই নামে সঠিক workflow আছে কি না যাচাই প্রয়োজন | duplicate/অকার্যকর নিশ্চিত হলে quarantine |
| `.github/workflows/build-tamanna-apk.yml';` | ফাইলের নামে shell quote/semicolon; ভেতরে Dart snippet, YAML workflow নয় | quarantine candidate |
| `bd-king-r7/IT/bd-king-r7/powerhub/powerhub_helper/auto_install.bad` | `.bad` extension; auto-install script এবং package installation logic আছে | নিরাপত্তা ও dependency review শেষে quarantine |
| `bd-king-r7/IT/bd-king-r7/powerhub/powerhub_helper/auto_sync.bad` | `.bad` extension; auto-sync/build/fix script | duplicate ও ব্যবহার যাচাই শেষে quarantine |
| `bd-king-r7/IT/bd-king-r7/powerhub/powerhub_helper/bd-king-r7_powerhub_helper.bad` | `.bad` extension; Powerhub helper script | duplicate ও ব্যবহার যাচাই শেষে quarantine |
| `bd-king-r7/IT/bd-king-r7/powerhub/powerhub_helper/bd-king-r7_ultra_synce.bad` | `.bad` extension; auto Git pull/add/commit/push করে—অনুমতি ছাড়া চালানো উচিত নয় | নিরাপত্তা review শেষে quarantine |
| `bd-king-r7/IT/bd-king-r7/powerhub/powerhub_helper/warking_helper.bad` | `.bad` extension; helper/auto-install script | duplicate ও ব্যবহার যাচাই শেষে quarantine |

## 2. Do not move these without further verification

- `.ven` — নামটি অস্বাভাবিক হলেও এতে Tamanna model provider, Ollama URL/model এবং environment configuration রয়েছে; এটি runtime configuration হতে পারে।
- `tamanna_domain_backup.tar.gz` — backup archive; backup যাচাই ও বিকল্প কপি নিশ্চিত না করে সরানো যাবে না।
- `~tamanna_code_editor_runner.sh` — নাম অস্বাভাবিক, কিন্তু এটি code-editor/runner script; ব্যবহারকারী চালান কি না যাচাই প্রয়োজন।
- `.github/workflows/`-এর Java, shell, batch ও Python ফাইল — workflow directory-তে থাকলেও সব ফাইল GitHub Actions workflow নয়; তবে সেগুলো helper/source file হতে পারে।

## 3. Review rules

1. কোনো candidate-এর import, reference, workflow call, script invocation বা documentation link আছে কি না খুঁজতে হবে।
2. একই কাজের কার্যকর বিকল্প আছে কি না এবং CI/build-এ সেটি ব্যবহৃত হয় কি না পরীক্ষা করতে হবে।
3. সরানোর আগে original path, blob SHA ও content সংরক্ষণ করতে হবে।
4. সরানোর পরে Python tests, repository validation, website validation এবং প্রাসঙ্গিক Android build চালাতে হবে।
5. কোনো secret, credential, backup বা production configuration এই তালিকা থেকে অনুমান করে মুছে ফেলা যাবে না।

## 4. Current status

- Repository tree inspected: **2,847 files** at the reviewed commit.
- Quarantine candidates recorded: **8**.
- Files quarantined under `trash/quarantine-2026-11-13/`: **3** (misplaced Bitbucket pipeline, newline-suffixed legacy APK workflow, and Dart snippet stored as a workflow-like file). Original contents and source paths are preserved in the quarantine copies and Git history.
- The five `.bad` PowerHub scripts were **not** moved because repository configuration and legacy helper scripts reference them; inspect and replace those references before quarantine.
- Runtime configuration and backup preserved.
- Remaining work: continue dependency/reference audit before moving any other candidates.


## 5. Quarantine update — 2026-11-15

- Moved **71 non-YAML files** out of `.github/workflows/` into `trash/quarantine-2026-11-15/.github/workflows/`, preserving their original relative paths and blob contents.
- Left **65 YAML workflow definitions** in `.github/workflows/`.
- Updated `scripts/check_legacy_shell_safety.py` to validate the preserved quarantine copies of five guarded legacy scripts.
- Full path and blob-SHA inventory: [quarantine manifest](trash/quarantine-2026-11-15/MANIFEST.md).
- No permanent deletion was performed. Do not restore archived scripts to active execution without review.


## 6. Quarantine update — 2026-11-16

- Original path: `bd-king-r7/IT/main py`
- Quarantine path: `trash/quarantine-2026-11-16/bd-king-r7/IT/main py`
- Original and quarantine blob SHA: `2d09068ff181bd5cd9e602af25387fa197660406` (content verified identical).
- Reason: the file had a Python parse error at the import `from utils.logger setup_logger`; repository code search found no matching `utils.logger` module or `setup_logger` definition, and the imported TI-PULS modules `core.ai_engine`, `modules.analytics`, `modules.automation`, and `modules.monitoring` were not found as independent implementations. The file is a standalone, incomplete legacy entrypoint, not the active Tamanna application entrypoint.
- Action: preserved the complete original under `trash/` and removed the malformed source path from the active tree. No file content was permanently deleted.
- Commits: quarantine copy `31138d07075db93f9524afe816398794f14bdf17`; source-path removal `f5bb6f6aba5584bb44af71fa78c5f114a0b920f1`.
- Validation status: content equality verified through GitHub fetch. Full CI/build has not yet been run for this move; do not treat it as fully tested until the new Actions runs complete.
