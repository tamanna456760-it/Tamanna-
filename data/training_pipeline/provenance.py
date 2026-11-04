"""Validate dataset provenance and training-use permissions before ingestion."""
from __future__ import annotations

import json
from pathlib import Path

CATEGORIES = {"website", "article", "book", "code", "technical_documentation", "research_paper", "other"}


def load_provenance(path: str | Path) -> dict[str, dict[str, object]]:
    """Load a JSON manifest keyed by relative filename; fail closed on unclear rights."""
    manifest_path = Path(path)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Provenance manifest must be a JSON array")
    result: dict[str, dict[str, object]] = {}
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"Manifest entry {index} must be an object")
        filename = item.get("file")
        category = item.get("category")
        license_name = item.get("license")
        source_url = item.get("source_url")
        usage_allowed = item.get("training_use_allowed")
        if not isinstance(filename, str) or not filename.strip():
            raise ValueError(f"Manifest entry {index} is missing file")
        if filename in result:
            raise ValueError(f"Duplicate provenance entry: {filename}")
        if category not in CATEGORIES:
            raise ValueError(f"Unsupported or missing category for {filename}")
        if not isinstance(license_name, str) or not license_name.strip():
            raise ValueError(f"Missing license for {filename}")
        if not isinstance(source_url, str) or not source_url.startswith("https://"):
            raise ValueError(f"An HTTPS source_url is required for {filename}")
        if usage_allowed is not True:
            raise ValueError(f"Training use is not explicitly allowed for {filename}")
        result[filename] = {
            "category": category,
            "license": license_name.strip(),
            "source_url": source_url.strip(),
            "license_url": str(item.get("license_url", "")).strip(),
            "training_use_allowed": True,
            "reviewed_by": str(item.get("reviewed_by", "")).strip(),
        }
    return result


__all__ = ["CATEGORIES", "load_provenance"]
