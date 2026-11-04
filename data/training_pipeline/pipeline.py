"""Build a cleaned JSONL dataset and quality report from local text/code files."""

from __future__ import annotations

import json
from pathlib import Path

from .cleaning import clean_text
from .quality import inspect_records

SUPPORTED = {".txt", ".md", ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".yaml", ".yml", ".html", ".css"}
DEFAULT_MAX_BYTES = 2 * 1024 * 1024


def _iter_sources(source: Path):
    if source.is_file():
        yield source
        return
    for path in sorted(source.rglob("*")):
        if path.is_file() and not path.is_symlink() and path.suffix.lower() in SUPPORTED:
            if not any(part.startswith(".") for part in path.relative_to(source).parts):
                yield path


def run_pipeline(source_dir: str | Path, output_dir: str | Path, *, min_chars: int = 20, max_bytes: int = DEFAULT_MAX_BYTES) -> dict:
    """Process local text/code files. Raw source files are never modified or uploaded."""
    source = Path(source_dir).expanduser().resolve()
    output = Path(output_dir).expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(f"Dataset source does not exist: {source}")
    if source == output or source in output.parents:
        raise ValueError("Output directory must not be inside the source directory")
    output.mkdir(parents=True, exist_ok=True)
    records = []
    skipped = []
    for path in _iter_sources(source):
        if path.suffix.lower() not in SUPPORTED:
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
        # JSONL input may contain structured records; ordinary files become one record.
        if path.suffix.lower() == ".json":
            try:
                parsed = json.loads(content)
                candidates = parsed if isinstance(parsed, list) else [parsed]
                source_texts = [str(item.get("text", item.get("content", ""))) for item in candidates if isinstance(item, dict)]
            except json.JSONDecodeError:
                source_texts = [content]
        else:
            source_texts = content.splitlines() if path.suffix.lower() == ".jsonl" else [content]
            if path.suffix.lower() == ".jsonl":
                decoded = []
                for line in source_texts:
                    try:
                        item = json.loads(line)
                        if isinstance(item, dict):
                            decoded.append(str(item.get("text", item.get("content", ""))))
                    except json.JSONDecodeError:
                        skipped.append({"file": str(path), "reason": "invalid_jsonl_line"})
                source_texts = decoded
        for text in source_texts:
            cleaned, flags = clean_text(text)
            records.append({"text": cleaned, "source": path.name, "redactions": flags})

    # Deduplicate and reject empty/short records while preserving first occurrence.
    seen = set()
    accepted = []
    quality_input = []
    for record in records:
        text = record["text"]
        key = text.casefold()
        if not text or len(text) < min_chars or key in seen:
            quality_input.append({"text": text})
            continue
        seen.add(key)
        accepted.append(record)
        quality_input.append({"text": text})
    report = inspect_records(quality_input, min_chars=min_chars)
    report["accepted"] = len(accepted)
    report["rejected"] = len(records) - len(accepted)
    report["files_skipped"] = len(skipped)
    report["redactions"] = sum(len(r["redactions"]) for r in accepted)

    dataset_path = output / "cleaned.jsonl"
    with dataset_path.open("w", encoding="utf-8") as handle:
        for record in accepted:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    report_path = output / "quality_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    skipped_path = output / "skipped_files.json"
    skipped_path.write_text(json.dumps(skipped, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"dataset": str(dataset_path), "report": str(report_path), "skipped": str(skipped_path), **report}
