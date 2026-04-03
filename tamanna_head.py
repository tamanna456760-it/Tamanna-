import os
import json
from datetime import datetime

IGNORE_DIRS = {'.git', '.github', '__pycache__', 'node_modules', 'bd-king-r7', 'tamanna-ai-system', 'config', 'ai system', 'api', 'device', 'docs', 'scripts', 'tests', 'orcid-system', 'venv', '.venv'}

def scan_repo(root='.'):
    files = []
    for base, dirs, fs in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in fs:
            path = os.path.join(base, f)
            if path.startswith('./'):
                path = path[2:]
            files.append(path)
    return files

def build_manifest(files):
    manifest = {
        "tamanna_head": True,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_files": len(files),
        "files": []
    }
    for path in files:
        try:
            size = os.path.getsize(path)
        except OSError:
            size = None
        manifest["files"].append({
            "path": path,
            "size": size
        })
    return manifest

def main():
    print("🧠 Tamanna AI HEAD: Scanning repository...")
    files = scan_repo('.')
    manifest = build_manifest(files)

    os.makedirs('tamanna_meta', exist_ok=True)
    manifest_path = os.path.join('tamanna_meta', 'manifest.json')

    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"✅ Tamanna HEAD manifest created: {manifest_path}")
    print(f"📦 Total files indexed: {manifest['total_files']}")

if __name__ == "__main__":
    main()
