"""Explicitly-run example for the legacy REST API helper."""
from __future__ import annotations

import sys
from pathlib import Path

# API.py remains in the legacy runner folder for compatibility.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from API import APIManager, RESTAPIClient, make_api_call  # noqa: E402


def main() -> None:
    """Make public demo requests only when this file is executed."""
    response = make_api_call("https://api.github.com/users/octocat")
    print("GitHub demo:", response)
    client = RESTAPIClient("https://jsonplaceholder.typicode.com")
    posts = client.get("/posts")
    if posts.success:
        for post in posts.data[:5]:
            print(post.get("title", "(untitled)"))
    else:
        print("Demo request failed:", posts.error)
    manager = APIManager()
    print("API manager ready:", manager is not None)


if __name__ == "__main__":
    main()
