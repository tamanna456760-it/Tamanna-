#!/usr/bin/env python3
"""Sync GitHub repository metadata into public or private Tamanna inventories.

The default output is committed to this repository and therefore excludes
private repositories. Private mode requires an explicit absolute output path
outside the Git checkout and writes it with owner-only filesystem permissions.
Never stores the GitHub token in either inventory.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.github.com"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "memory" / "github_repositories.json"


def request_page(url: str, token: str) -> list[dict]:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Tamanna-AI-GitHub-Memory",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API returned HTTP {exc.code}: {detail}") from exc
    if not isinstance(payload, list):
        raise RuntimeError("Unexpected GitHub API response; expected a repository list")
    return payload


def build_inventory(items: list[dict], *, include_private: bool = False) -> dict:
    repos: dict[str, dict] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        is_private = item.get("private") is True
        if is_private and not include_private:
            continue
        full_name = item.get("full_name")
        if not isinstance(full_name, str) or not full_name.strip():
            continue
        repos[full_name.casefold()] = {
            "id": item.get("id"),
            "full_name": full_name,
            "name": item.get("name"),
            "owner": (item.get("owner") or {}).get("login"),
            "private": is_private,
            "archived": bool(item.get("archived")),
            "default_branch": item.get("default_branch"),
            "html_url": item.get("html_url"),
            "description": item.get("description"),
            "updated_at": item.get("updated_at"),
        }
    scope = "all accessible repositories" if include_private else "public repositories only"
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": f"GitHub REST API /user/repos ({scope})",
        "repository_count": len(repos),
        "repositories": sorted(repos.values(), key=lambda x: x["full_name"].casefold()),
    }


def build_public_inventory(items: list[dict]) -> dict:
    """Backward-compatible public-only inventory builder."""
    return build_inventory(items, include_private=False)


def write_inventory(
    payload: dict, output: str | Path, *, private: bool = False,
    repo_root: str | Path = ROOT,
) -> Path:
    destination = Path(output)
    if private and not destination.is_absolute():
        raise ValueError("Private inventory output must be an absolute path outside the repository")
    if destination.is_symlink():
        raise ValueError("Inventory output cannot be a symlink")
    destination = destination.resolve()
    root = Path(repo_root).resolve()
    if private and (destination == root or root in destination.parents):
        raise ValueError("Private inventory must be stored outside the Git repository")
    destination.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    if private:
        flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(destination, flags, 0o600 if private else 0o666)
    with os.fdopen(descriptor, "w", encoding="utf-8") as output_file:
        if private:
            os.fchmod(output_file.fileno(), 0o600)
        output_file.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\\n")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(OUT))
    parser.add_argument(
        "--include-private", action="store_true",
        help="Include private repositories; requires an absolute output outside the Git checkout",
    )
    args = parser.parse_args()
    token = os.environ.get("TAMANNA_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Missing TAMANNA_GITHUB_TOKEN or GITHUB_TOKEN", file=sys.stderr)
        return 2

    items: list[dict] = []
    page = 1
    try:
        while True:
            batch = request_page(
                f"{API}/user/repos?visibility=all&affiliation=owner,collaborator,organization_member"
                f"&per_page=100&page={page}&sort=full_name&direction=asc",
                token,
            )
            items.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        payload = build_inventory(items, include_private=args.include_private)
        destination = write_inventory(
            payload, args.output, private=args.include_private
        )
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Repository inventory sync failed: {exc}", file=sys.stderr)
        return 1

    visibility = "all accessible" if args.include_private else "public"
    print(f"Indexed {payload['repository_count']} {visibility} repositories into {destination}")
    if not args.include_private:
        print("Private repositories were excluded from the public, committed inventory.")
    else:
        print("Private inventory saved with mode 0600 outside the Git checkout.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
