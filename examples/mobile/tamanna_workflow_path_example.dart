import 'package:path/path.dart' as path;
import 'package:path_provider/path_provider.dart';

Future<void> main() async {
  final appDocDir = await getApplicationDocumentsDirectory();
  final repoRoot = path.join(appDocDir.path, 'Tamanna');
  final yamlPath = path.join(
    repoRoot,
    '.github',
    'workflows',
    'build-tamanna-apk.yml',
  );

  print('Workflow file path: $yamlPath');
}
