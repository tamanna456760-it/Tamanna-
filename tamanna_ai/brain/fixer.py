"""Safe text replacement helper. Dry-run is the default; code is never executed."""
import hashlib
from pathlib import Path
from typing import Any

def replace_text(path: str | Path, old: str, new: str, *, dry_run: bool = True, expected_sha256: str | None = None) -> dict[str, Any]:
    target = Path(path).expanduser().resolve()
    if not target.is_file():
        raise FileNotFoundError(target)
    if not old:
        raise ValueError("old text must not be empty")
    original = target.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise ValueError("file changed since it was reviewed")
    updated = original.decode("utf-8").replace(old, new)
    count = original.decode("utf-8").count(old)
    if count == 0:
        return {"status": "not_found", "matches": 0, "dry_run": dry_run, "sha256": digest}
    new_digest = hashlib.sha256(updated.encode("utf-8")).hexdigest()
    if not dry_run:
        temporary = target.with_name(target.name + ".tamanna-tmp")
        try:
            temporary.write_text(updated, encoding="utf-8")
            temporary.replace(target)
        finally:
            if temporary.exists():
                temporary.unlink()
    return {"status": "preview" if dry_run else "updated", "matches": count, "dry_run": dry_run,
            "before_sha256": digest, "after_sha256": new_digest}

__all__ = ["replace_text"]
