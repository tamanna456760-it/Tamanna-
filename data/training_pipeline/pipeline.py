"""Build cleaned text/code data and a validated image manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .cleaning import clean_text
from .quality import inspect_records

SUPPORTED = {".txt", ".md", ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".jsonl", ".yaml", ".yml", ".html", ".css"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
IMAGE_SIGNATURES = {
    ".jpg": (b"\xff\xd8\xff",), ".jpeg": (b"\xff\xd8\xff",),
    ".png": (b"\x89PNG\r\n\x1a\n",), ".gif": (b"GIF87a", b"GIF89a"),
    ".webp": (b"RIFF",), ".bmp": (b"BM",),
}
DEFAULT_MAX_BYTES = 2 * 1024 * 1024
IMAGE_MAX_BYTES = 20 * 1024 * 1024


def _iter_sources(source: Path):
    if source.is_file():
        yield source
        return
    for path in sorted(source.rglob("*")):
        if path.is_file() and not path.is_symlink() and path.suffix.lower() in SUPPORTED | IMAGE_EXTENSIONS:
            if not any(part.startswith(".") for part in path.relative_to(source).parts):
                yield path


def run_pipeline(source_dir: str | Path, output_dir: str | Path, *, min_chars: int = 20, max_bytes: int = DEFAULT_MAX_BYTES) -> dict:
    """Process local text/code and index image files; never modifies or uploads inputs."""
    source = Path(source_dir).expanduser().resolve()
    output = Path(output_dir).expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(f"Dataset source does not exist: {source}")
    if source.is_dir() and (source == output or source in output.parents):
        raise ValueError("Output directory must not be inside the source directory")
    output.mkdir(parents=True, exist_ok=True)
    records = []
    image_records = []
    skipped = []
    for path in _iter_sources(source):
        suffix = path.suffix.lower()
        if suffix in IMAGE_EXTENSIONS:
            try:
                size = path.stat().st_size
                if size > IMAGE_MAX_BYTES:
                    skipped.append({"file": str(path), "reason": "image_too_large"})
                    continue
                with path.open("rb") as image_file:
                    header = image_file.read(12)
                    valid = any(header.startswith(sig) for sig in IMAGE_SIGNATURES[suffix])
                    if suffix == ".webp":
                        valid = valid and header[8:12] == b"WEBP"
                    image_file.seek(0)
                    digest = hashlib.sha256(image_file.read()).hexdigest()
                if not valid:
                    skipped.append({"file": str(path), "reason": "invalid_image_signature"})
                    continue
                try:
                    image_name = str(path.relative_to(source))
                except ValueError:
                    image_name = path.name
                image_records.append({"file": image_name, "format": suffix.lstrip("."), "bytes": size, "sha256": digest})
            except OSError as exc:
                skipped.append({"file": str(path), "reason": type(exc).__name__})
            continue
        if suffix not in SUPPORTED:
            skipped.append({"file": str(path), "reason": "unsupported_format"})
            continue
        try:
            size = path.stat().st_size
            if size > max_bytes:
                skipped.append({"file": str(path), "reason": "file_too_large"})
                continue
            content = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            skipped.append({"file": str(path), "reason": type(exc).__name__})
            continue
        if suffix == ".json":
            try:
                parsed = json.loads(content)
                candidates = parsed if isinstance(parsed, list) else [parsed]
                source_texts = [str(item.get("text", item.get("content", ""))) for item in candidates if isinstance(item, dict)]
            except json.JSONDecodeError:
                source_texts = [content]
        elif suffix == ".jsonl":
            source_texts = []
            for line in content.splitlines():
                try:
                    item = json.loads(line)
                    if isinstance(item, dict):
                        source_texts.append(str(item.get("text", item.get("content", ""))))
                except json.JSONDecodeError:
                    skipped.append({"file": str(path), "reason": "invalid_jsonl_line"})
        else:
            source_texts = [content]
        for text in source_texts:
            cleaned, flags = clean_text(text)
            records.append({"text": cleaned, "source": path.name, "redactions": flags})

    seen = set()
    accepted = []
    for record in records:
        text = record["text"]
        key = text.casefold()
        if not text or len(text) < min_chars or key in seen:
            continue
        seen.add(key)
        accepted.append(record)

    report = inspect_records([{"text": r["text"]} for r in records], min_chars=min_chars)
    report["accepted"] = len(accepted)
    report["rejected"] = len(records) - len(accepted)
    report["files_skipped"] = len(skipped)
    report["images_indexed"] = len(image_records)
    report["redactions"] = sum(len(r["redactions"]) for r in accepted)

    dataset_path = output / "cleaned.jsonl"
    with dataset_path.open("w", encoding="utf-8") as handle:
        for record in accepted:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    images_path = output / "images_manifest.jsonl"
    with images_path.open("w", encoding="utf-8") as handle:
        for record in image_records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    report_path = output / "quality_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    skipped_path = output / "skipped_files.json"
    skipped_path.write_text(json.dumps(skipped, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"dataset": str(dataset_path), "images_manifest": str(images_path), "report": str(report_path), "skipped": str(skipped_path), **report}
