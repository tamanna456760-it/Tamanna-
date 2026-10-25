
"""Tamanna AI: read-only documentation indexer."""
from __future__ import annotations

import hashlib
from pathlib import Path

SUPPORTED_SUFFIXES = {".md", ".rst", ".txt"}

EXCLUDED_DIRS = {
    ".git", ".venv", "venv", "node_modules",
    "__pycache__", "dist", "build",
    ".pytest_cache", ".mypy_cache",
}


class DocumentationIndexer:
    def __init__(
        self,
        root: str | Path,
        excluded_dirs: set[str] | None = None,
    ):
        self.root = Path(root).resolve()
        self.excluded_dirs = EXCLUDED_DIRS | (excluded_dirs or set())

    def index(self) -> list[dict]:
        if not self.root.is_dir():
            raise NotADirectoryError(str(self.root))

        results = []

        for path in self.root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue

            relative = path.relative_to(self.root)

            if any(part in self.excluded_dirs for part in relative.parts):
                continue

            try:
                content = path.read_text(encoding="utf-8")
                size = path.stat().st_size
            except (OSError, UnicodeDecodeError):
                continue

            first_line = next(
                (line.strip() for line in content.splitlines()
                 if line.strip()),
                path.stem,
            )

            results.append({
                "path": relative.as_posix(),
                "title": first_line.lstrip("#").strip()[:200],
                "size_bytes": size,
                "sha256": hashlib.sha256(
                    content.encode("utf-8")
                ).hexdigest(),
                "content": content,
            })

        return sorted(
            results,
            key=lambda item: item["path"].casefold(),
        )

    def search(self, query: str, limit: int = 20) -> list[dict]:
        query = query.strip().casefold()

        if not query:
            return []
        if limit < 1:
            raise ValueError("limit must be at least 1")

        matches = []

        for document in self.index():
            text = (
                document["title"] + "\n" + document["content"]
            ).casefold()

            if query in text:
                result = dict(document)
                result.pop("content", None)
                matches.append(result)

                if len(matches) >= min(limit, 1000):
                    break

        return matches


def index_documentation(root: str | Path) -> list[dict]:
    return DocumentationIndexer(root).index()
