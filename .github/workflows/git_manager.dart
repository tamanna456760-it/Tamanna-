import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;
import 'dart:io';

Future<void> createGithubWorkflow() async {
  // Get app‑owned document directory
  final appDir = await getApplicationDocumentsDirectory();
  
  // Build new safe path (no trailing space after Tamanna!)
  final repoRoot = path.join(appDir.path, 'Tamanna');
  final workflowDir = path.join(repoRoot, '.github', 'workflows');
  final yamlFile = File(path.join(workflowDir, 'build-tamanna-apk.yml'));

  // Create directories if they don't exist
  await yamlFile.create(recursive: true);

  // Write workflow content
  const yamlContent = '''
name: Build Tamanna APK
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - name: Setup Android SDK
        uses: android-actions/setup-android@v3
      - name: Build APK
        run: |
          cd android
          ./gradlew assembleRelease
      - uses: actions/upload-artifact@v4
        with:
          name: tamanna-apk
          path: app/build/outputs/apk/release/*.apk
''';

  await yamlFile.writeAsString(yamlContent);
  print("✅ Workflow saved at: ${yamlFile.path}");
}