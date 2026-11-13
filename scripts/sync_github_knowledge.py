"""Sync public Markdown knowledge from a GitHub repository into Tamanna's local RAG index.

No GitHub API, hosted AI API, or API key is used. The source repository must be
public; private repositories require an explicitly configured Git credential.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_REPOSITORY = "https://github.com/tamanna456760-it/Tamanna-.git"
DEFAULT_BRANCH = "main"
MAX_FILE_BYTES = 1_000_000
MAX_FILES = 20_000
SUPPORTED_SUFFIXES = {".md", ".rst", ".txt"}
EXCLUDED_PARTS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", "dist",
    "build", ".pytest_cache", ".mypy_cache", "data", "uploads",
    "private", "secrets", "trash",
}


def validate_repository_url(value: str) -> str:
    value = value.strip()
    if not re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?", value):
        raise ValueError("Repository must be a public https://github.com/OWNER/REPO URL")
    return value if value.endswith(".git") else value + ".git"


def run_git(args: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(
        ["git", *args], cwd=str(cwd) if cwd else None,
        check=True, timeout=300, capture_output=True, text=True,
    )


def checkout_repository(repository_url: str, branch: str, destination: Path) -> Path:
    url = validate_repository_url(repository_url)
    if not re.fullmatch(r"[A-Za-z0-9._/-]{1,120}", branch) or branch.startswith("-"):
        raise ValueError("Invalid Git branch name")
    destination = destination.resolve()
    managed_root = (BASE_DIR / "data" / "github-knowledge").resolve()
    if destination != managed_root and managed_root not in destination.parents:
        raise ValueError("Checkout destination must stay inside data/github-knowledge")
    if destination.is_symlink():
        raise ValueError("Checkout destination cannot be a symlink")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if (destination / ".git").is_dir():
        run_git(["fetch", "--depth", "1", "origin", branch], cwd=destination)
        run_git(["checkout", "--detach", "FETCH_HEAD"], cwd=destination)
        run_git(["clean", "-ffd"], cwd=destination)
    else:
        if destination.exists() and any(destination.iterdir()):
            raise ValueError("Refusing to clone into a non-empty unmanaged directory")
        run_git(["clone", "--depth", "1", "--branch", branch, url, str(destination)])
    return destination


def iter_documents(root: Path):
    count = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root)
        if any(part.casefold() in EXCLUDED_PARTS for part in relative.parts):
            continue
        if path.suffix.casefold() not in SUPPORTED_SUFFIXES:
            continue
        try:
            size = path.stat().st_size
            if size <= 0 or size > MAX_FILE_BYTES:
                continue
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        count += 1
        if count > MAX_FILES:
            raise ValueError(f"Repository exceeds the {MAX_FILES:,}-document indexing limit")
        if content.strip():
            yield relative.as_posix(), content


def sync_repository(repository_url: str, branch: str = DEFAULT_BRANCH) -> dict:
    from tamanna_ai.knowledge.vector_store import LocalFeatureEmbedder, VectorKnowledgeStore

    destination = BASE_DIR / "data" / "github-knowledge"
    checkout = checkout_repository(repository_url, branch, destination)
    store = VectorKnowledgeStore(LocalFeatureEmbedder())
    documents = 0
    chunks = 0
    for relative_path, content in iter_documents(checkout):
        source = f"github:{relative_path}"
        chunks += store.index_text(
            content, owner_id="tamanna-public", source=source,
            title=Path(relative_path).stem,
        )
        documents += 1
    return {
        "status": "ok",
        "repository": validate_repository_url(repository_url),
        "branch": branch,
        "documents_indexed": documents,
        "chunks_indexed": chunks,
        "owner_id": "tamanna-public",
        "embedding": "local-feature",
        "hosted_api_used": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync public GitHub knowledge into Tamanna's local index.")
    parser.add_argument("--repository", default=os.getenv("TAMANNA_KNOWLEDGE_GIT_URL", DEFAULT_REPOSITORY))
    parser.add_argument("--branch", default=os.getenv("TAMANNA_KNOWLEDGE_GIT_BRANCH", DEFAULT_BRANCH))
    args = parser.parse_args()
    try:
        result = sync_repository(args.repository, args.branch)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"Knowledge sync failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    for key, value in result.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
