from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / ".tamanna" / "registry" / "resource_registry.json"
INDEX = ROOT / ".tamanna" / "indexes" / "resource_index.json"

IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    ".env",
}

CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".java", ".kt", ".go", ".rs",
    ".c", ".h", ".cpp", ".hpp",
    ".cs", ".php", ".rb",
    ".swift", ".dart",
    ".html", ".css", ".scss",
    ".json", ".yaml", ".yml",
    ".toml", ".sql", ".sh",
}

def sha256_file(path: Path):
    h = hashlib.sha256()
    try:
        with path.open("rb") as f:
            for block in iter(lambda: f.read(1024 * 1024), b""):
                h.update(block)
        return h.hexdigest()
    except Exception:
        return None

def scan():
    resources = []

    for base in [ROOT / "resources", ROOT / ".tamanna" / "resources"]:
        if not base.exists():
            continue

        for project in sorted(base.iterdir()):
            if not project.is_dir():
                continue

            files = []
            code_count = 0

            for path in project.rglob("*"):
                if not path.is_file():
                    continue

                if any(part in IGNORE_DIRS for part in path.parts):
                    continue

                rel = path.relative_to(project)

                if path.suffix.lower() in CODE_EXTENSIONS:
                    code_count += 1

                files.append({
                    "path": str(rel),
                    "size": path.stat().st_size,
                    "sha256": sha256_file(path)
                })

            resources.append({
                "name": project.name,
                "path": str(project.relative_to(ROOT)),
                "file_count": len(files),
                "code_file_count": code_count,
                "files": files
            })

    INDEX.parent.mkdir(parents=True, exist_ok=True)

    output = {
        "name": "Tamanna AI Resource Index",
        "owner": "HM INSAN ALI",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "resource_count": len(resources),
        "resources": resources
    }

    INDEX.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    if REGISTRY.exists():
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        registry["resources"] = [
            {
                "name": r["name"],
                "path": r["path"],
                "file_count": r["file_count"],
                "code_file_count": r["code_file_count"]
            }
            for r in resources
        ]
        REGISTRY.write_text(
            json.dumps(registry, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    print(f"Tamanna AI indexed {len(resources)} resources.")
    print(f"Index: {INDEX}")

if __name__ == "__main__":
    scan()
