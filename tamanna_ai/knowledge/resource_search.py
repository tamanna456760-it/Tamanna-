from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / ".tamanna" / "indexes" / "resource_index.json"

TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".java", ".kt", ".go", ".rs",
    ".c", ".h", ".cpp", ".hpp",
    ".cs", ".php", ".rb",
    ".swift", ".dart",
    ".html", ".css", ".scss",
    ".json", ".yaml", ".yml",
    ".toml", ".sql", ".sh",
    ".md", ".txt"
}

def load_index():
    if not INDEX.exists():
        return {"resources": []}

    try:
        return json.loads(INDEX.read_text(encoding="utf-8"))
    except Exception:
        return {"resources": []}


def search_resources(query, limit=20):
    query = query.lower().strip()

    if not query:
        return []

    data = load_index()
    results = []

    for resource in data.get("resources", []):
        resource_name = resource.get("name", "")
        resource_path = resource.get("path", "")

        for item in resource.get("files", []):
            path = item.get("path", "")

            haystack = (
                f"{resource_name} "
                f"{resource_path} "
                f"{path}"
            ).lower()

            if query in haystack:
                results.append({
                    "resource": resource_name,
                    "resource_path": resource_path,
                    "file": path,
                    "size": item.get("size"),
                    "sha256": item.get("sha256")
                })

                if len(results) >= limit:
                    return results

    return results


def search_code(query, limit=20):
    results = search_resources(query, limit)

    return [
        r for r in results
        if Path(r["file"]).suffix.lower() in TEXT_EXTENSIONS
    ]


if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]).strip()

    if not query:
        print("Usage: python3 resource_search.py <search>")
        raise SystemExit(1)

    results = search_code(query)

    print(f"Found: {len(results)}")

    for r in results:
        print(
            f"[{r['resource']}] "
            f"{r['resource_path']}/{r['file']}"
        )
