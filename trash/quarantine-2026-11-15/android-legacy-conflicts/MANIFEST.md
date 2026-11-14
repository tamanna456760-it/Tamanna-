# Android legacy conflict quarantine

These files are preserved byte-for-byte because their paths/content conflict with canonical files or are not recognized by Android tooling. They are not compiled by the current Gradle source set.

| Original path | Reason | Quarantine path | Blob SHA |
|---|---|---|---|
| `tamanna-ai-app/app/src/main/AndroidManife st.xml` | Malformed duplicate manifest filename; Android Gradle recognizes AndroidManifest.xml only. | `trash/quarantine-2026-11-15/android-legacy-conflicts/tamanna-ai-app__app__src__main__AndroidManife st.xml` | `56d44bc2b4a995e579e14c900e4c19d46f389059` |
| `tamanna-ai-app/app/src/main/AndroidManifes t.xml` | Malformed alternate manifest filename; Android Gradle recognizes AndroidManifest.xml only. | `trash/quarantine-2026-11-15/android-legacy-conflicts/tamanna-ai-app__app__src__main__AndroidManifes t.xml` | `5bc3b9df1db38967ad96cfa1c2390ecd81975126` |
| `tamanna-ai-app/app/src/main/java/com/tamanna/ai/Api Config.kt` | Declares ApiConfig in the same package as ApiConfig.kt, creating a duplicate class if legacy sources are compiled. | `trash/quarantine-2026-11-15/android-legacy-conflicts/tamanna-ai-app__app__src__main__java__com__tamanna__ai__Api Config.kt` | `c3fd815ad68245f70f53682555d92eae9d2b357e` |
| `tamanna-ai-app/app/src/main/java/com/tamanna/ai/Tamanna Chat.kt` | Declares TamannaChat in the same package as TamannaChat.kt, creating a duplicate class if legacy sources are compiled. | `trash/quarantine-2026-11-15/android-legacy-conflicts/tamanna-ai-app__app__src__main__java__com__tamanna__ai__Tamanna Chat.kt` | `90a2ec13ec3bada5b9dfa9be2d208c53da055828` |
