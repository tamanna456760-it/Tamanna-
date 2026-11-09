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
- Files deleted or moved: **0**.
- Runtime configuration and backup preserved.
- Next safe step: dependency/reference scan, then move only confirmed unused candidates into `trash/` while preserving their original contents and paths in Git history.
