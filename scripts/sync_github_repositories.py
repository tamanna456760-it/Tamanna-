#!/usr/bin/env python3
"""Sync public GitHub repository metadata into Tamanna AI's public inventory.

Private repository metadata is deliberately excluded: this file is committed
to the repository and may be publicly readable. Never stores tokens or secrets.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.github.com"
OUT = Path("memory/github_repositories.json")


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


def build_public_inventory(items: list[dict]) -> dict:
    repos: dict[str, dict] = {}
    for item in items:
        if not isinstance(item, dict) or item.get("private") is True:
            continue
        full_name = item.get("full_name")
        if not isinstance(full_name, str) or not full_name.strip():
            continue
        repos[full_name.casefold()] = {
            "id": item.get("id"),
            "full_name": full_name,
            "name": item.get("name"),
            "owner": (item.get("owner") or {}).get("login"),
            "private": False,
            "archived": bool(item.get("archived")),
            "default_branch": item.get("default_branch"),
            "html_url": item.get("html_url"),
            "description": item.get("description"),
            "updated_at": item.get("updated_at"),
        }
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "GitHub REST API /user/repos (public repositories only)",
        "repository_count": len(repos),
        "repositories": sorted(repos.values(), key=lambda x: x["full_name"].casefold()),
    }


def main() -> int:
    token = os.environ.get("TAMANNA_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Missing TAMANNA_GITHUB_TOKEN or GITHUB_TOKEN", file=sys.stderr)
        return 2

    items: list[dict] = []
    page = 1
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

    payload = build_public_inventory(items)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Indexed {payload['repository_count']} public repositories into {OUT}")
    print("Private repositories were excluded from this public, committed inventory.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
