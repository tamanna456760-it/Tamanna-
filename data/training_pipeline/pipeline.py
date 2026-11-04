"""Build cleaned text/code datasets and validated media manifests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .cleaning import clean_text
from .quality import inspect_records

SUPPORTED = {
    ".txt", ".md", ".rst", ".py", ".js", ".jsx", ".ts", ".tsx",
    ".java", ".kt", ".go", ".rs", ".c", ".h", ".cpp", ".hpp",
    ".cs", ".php", ".rb", ".swift", ".dart", ".json", ".jsonl",
    ".yaml", ".yml", ".html", ".css", ".scss", ".toml", ".sql", ".sh",
}
MEDIA_TYPES = {
    ".jpg": ("image", "image/jpeg"), ".jpeg": ("image", "image/jpeg"),
    ".png": ("image", "image/png"), ".webp": ("image", "image/webp"),
    ".gif": ("image", "image/gif"), ".bmp": ("image", "image/bmp"),
    ".mp3": ("audio", "audio/mpeg"), ".wav": ("audio", "audio/wav"),
    ".ogg": ("audio", "audio/ogg"), ".flac": ("audio", "audio/flac"),
    ".m4a": ("audio", "audio/mp4"), ".aac": ("audio", "audio/aac"),
    ".mp4": ("video", "video/mp4"), ".webm": ("video", "video/webm"),
    ".mov": ("video", "video/quicktime"), ".mkv": ("video", "video/x-matroska"),
    ".pdf": ("document", "application/pdf"),
}
MEDIA_MAX_BYTES = 20 * 1024 * 1024
DEFAULT_MAX_BYTES = 2 * 1024 * 1024


def _valid_media_header(suffix: str, header: bytes) -> bool:
    """Conservative container signature checks; this does not decode media."""
    signatures = {
        ".jpg": header.startswith(b"\xff\xd8\xff"),
        ".jpeg": header.startswith(b"\xff\xd8\xff"),
        ".png": header.startswith(b"\x89PNG\r\n\x1a\n"),
        ".gif": header.startswith((b"GIF87a", b"GIF89a")),
        ".webp": header.startswith(b"RIFF") and header[8:12] == b"WEBP",
        ".bmp": header.startswith(b"BM"),
        ".wav": header.startswith(b"RIFF") and header[8:12] == b"WAVE",
        ".ogg": header.startswith(b"OggS"),
        ".flac": header.startswith(b"fLaC"),
        ".mp3": header.startswith(b"ID3") or (len(header) >= 2 and header[0] == 0xFF and (header[1] & 0xE0) == 0xE0),
        ".mp4": len(header) >= 8 and header[4:8] == b"ftyp",
        ".m4a": len(header) >= 8 and header[4:8] == b"ftyp",
        ".mov": len(header) >= 8 and header[4:8] == b"ftyp",
        ".webm": header.startswith(b"\x1a\x45\xdf\xa3"),
        ".mkv": header.startswith(b"\x1a\x45\xdf\xa3"),
        ".pdf": header.startswith(b"%PDF-"),
        ".aac": len(header) >= 2 and header[0] == 0xFF and (header[1] & 0xF6) == 0xF0,
    }
    return signatures.get(suffix, False)


def _iter_sources(source: Path):
    if source.is_file():
        yield source
        return
    for path in sorted(source.rglob("*")):
        if path.is_file() and not path.is_symlink() and path.suffix.lower() in SUPPORTED | set(MEDIA_TYPES):
            if not any(part.startswith(".") for part in path.relative_to(source).parts):
                yield path


def run_pipeline(source_dir: str | Path, output_dir: str | Path, *, min_chars: int = 20, max_bytes: int = DEFAULT_MAX_BYTES) -> dict:
    """Process local text/code and index media metadata; never modifies or uploads inputs."""
    source = Path(source_dir).expanduser().resolve()
    output = Path(output_dir).expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(f"Dataset source does not exist: {source}")
    if source.is_dir() and (source == output or source in output.parents):
        raise ValueError("Output directory must not be inside the source directory")
    output.mkdir(parents=True, exist_ok=True)
    records, media_records, skipped = [], [], []
    for path in _iter_sources(source):
        suffix = path.suffix.lower()
        if suffix in MEDIA_TYPES:
            try:
                size = path.stat().st_size
                if size <= 0 or size > MEDIA_MAX_BYTES:
                    skipped.append({"file": str(path), "reason": "media_empty_or_too_large"})
                    continue
                with path.open("rb") as media_file:
                    header = media_file.read(16)
                    if not _valid_media_header(suffix, header):
                        skipped.append({"file": str(path), "reason": "invalid_media_signature"})
                        continue
                    media_file.seek(0)
                    digest = hashlib.sha256()
                    for chunk in iter(lambda: media_file.read(1024 * 1024), b""):
                        digest.update(chunk)
                try:
                    relative_name = str(path.relative_to(source))
                except ValueError:
                    relative_name = path.name
                media_kind, mime_type = MEDIA_TYPES[suffix]
                media_records.append({
                    "file": relative_name, "kind": media_kind, "format": suffix.lstrip("."),
                    "mime_type": mime_type, "bytes": size, "sha256": digest.hexdigest(),
                })
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
                source_texts = [
                    str(item.get("text", item.get("content", "")))
                    for item in candidates if isinstance(item, dict)
                ]
            except json.JSONDecodeError:
                source_texts = [content]
        elif suffix == ".jsonl":
            source_texts = []
            for line in content.splitlines():
                try:
                    item = json.loads(line)
                    if isinstance(item, dict):
                        # Support generic documents and conversational records.
                        if item.get("text") or item.get("content"):
                            source_texts.append(str(item.get("text") or item.get("content")))
                        elif item.get("user") and item.get("assistant"):
                            source_texts.append("User: " + str(item["user"]) + "\nAssistant: " + str(item["assistant"]))
                except json.JSONDecodeError:
                    skipped.append({"file": str(path), "reason": "invalid_jsonl_line"})
        else:
            source_texts = [content]
        for source_text in source_texts:
            cleaned, flags = clean_text(source_text)
            records.append({"text": cleaned, "source": path.name, "redactions": flags})

    seen, accepted = set(), []
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
    report["media_indexed"] = len(media_records)
    report["images_indexed"] = sum(item["kind"] == "image" for item in media_records)
    report["audio_indexed"] = sum(item["kind"] == "audio" for item in media_records)
    report["video_indexed"] = sum(item["kind"] == "video" for item in media_records)
    report["documents_indexed"] = sum(item["kind"] == "document" for item in media_records)
    report["redactions"] = sum(len(r["redactions"]) for r in accepted)

    outputs = {
        "dataset": output / "cleaned.jsonl",
        "media_manifest": output / "media_manifest.jsonl",
        "images_manifest": output / "images_manifest.jsonl",
        "report": output / "quality_report.json",
        "skipped": output / "skipped_files.json",
    }
    with outputs["dataset"].open("w", encoding="utf-8") as handle:
        for record in accepted:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    with outputs["media_manifest"].open("w", encoding="utf-8") as handle:
        for record in media_records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    # Keep the previous image-only manifest for existing consumers.
    with outputs["images_manifest"].open("w", encoding="utf-8") as handle:
        for record in media_records:
            if record["kind"] == "image":
                handle.write(json.dumps({
                    "file": record["file"], "format": record["format"],
                    "bytes": record["bytes"], "sha256": record["sha256"],
                }, ensure_ascii=False) + "\n")
    outputs["report"].write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    outputs["skipped"].write_text(json.dumps(skipped, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {key: str(value) for key, value in outputs.items()} | report
