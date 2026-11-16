#!/usr/bin/env python3
"""Sync accessible GitHub repository metadata into Tamanna AI's durable memory index.

Uses only GitHub's REST API and Python standard library. Never stores tokens or secrets.
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


def main() -> int:
    token = os.environ.get("TAMANNA_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Missing TAMANNA_GITHUB_TOKEN or GITHUB_TOKEN", file=sys.stderr)
        return 2

    repos: dict[str, dict] = {}
    page = 1
    while True:
        batch = request_page(
            f"{API}/user/repos?visibility=all&affiliation=owner,collaborator,organization_member"
            f"&per_page=100&page={page}&sort=full_name&direction=asc",
            token,
        )
        for item in batch:
            full_name = item.get("full_name")
            if not full_name:
                continue
            repos[full_name.casefold()] = {
                "id": item.get("id"),
                "full_name": full_name,
                "name": item.get("name"),
                "owner": (item.get("owner") or {}).get("login"),
                "private": bool(item.get("private")),
                "archived": bool(item.get("archived")),
                "default_branch": item.get("default_branch"),
                "html_url": item.get("html_url"),
                "description": item.get("description"),
                "updated_at": item.get("updated_at"),
            }
        if len(batch) < 100:
            break
        page += 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "GitHub REST API /user/repos",
        "repository_count": len(repos),
        "repositories": sorted(repos.values(), key=lambda x: x["full_name"].casefold()),
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Indexed {len(repos)} accessible repositories into {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
