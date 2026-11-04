"""Bounded, read-only analysis for CSV, XLSX, and PDF files.

Returns deterministic summaries and chart-ready data; it never executes
spreadsheet formulas or modifies the source file.
"""
from __future__ import annotations

import csv
import math
from collections import Counter
from pathlib import Path
from typing import Any

MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_ROWS = 100_000
MAX_COLUMNS = 200
SUPPORTED = {".csv", ".xlsx", ".pdf"}


def _number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        result = float(value)
    else:
        raw = str(value).strip().replace(",", "")
        if not raw:
            return None
        if raw.startswith("$"):
            raw = raw[1:]
        if raw.endswith("%"):
            raw = raw[:-1]
        try:
            result = float(raw)
        except (TypeError, ValueError):
            return None
    return result if math.isfinite(result) else None


def _summarize_rows(headers: list[str], rows: list[list[Any]], source: str) -> dict[str, Any]:
    columns: dict[str, Any] = {}
    for index, header in enumerate(headers):
        values = [row[index] if index < len(row) else None for row in rows]
        nums = [n for value in values if (n := _number(value)) is not None]
        nonempty = [str(v).strip() for v in values if v is not None and str(v).strip()]
        if nums:
            columns[header] = {
                "type": "numeric", "count": len(nums),
                "missing": len(values) - len(nonempty),
                "sum": round(sum(nums), 6), "mean": round(sum(nums) / len(nums), 6),
                "min": min(nums), "max": max(nums),
            }
        else:
            counts = Counter(nonempty)
            columns[header] = {
                "type": "categorical", "count": len(nonempty),
                "missing": len(values) - len(nonempty), "unique": len(counts),
                "top_values": [{"value": key, "count": count} for key, count in counts.most_common(5)],
            }
    numeric = [name for name, stats in columns.items() if stats["type"] == "numeric"]
    chart = None
    if numeric and len(rows) <= 500:
        x_key = headers[0] if headers else "row"
        chart = {
            "kind": "line", "x_key": x_key, "series": numeric[:8],
            "data": [
                {x_key: str(row[0] if row else i + 1),
                 **{name: _number(row[headers.index(name)]) for name in numeric[:8]}}
                for i, row in enumerate(rows)
            ],
        }
    return {
        "source": source, "row_count": len(rows), "column_count": len(headers),
        "columns": columns, "chart_data": chart,
        "limitations": ["Chart data is a specification; rendering requires a UI/report renderer."],
    }


def analyze_file(file_path: str | Path, *, max_bytes: int = MAX_FILE_BYTES) -> dict[str, Any]:
    """Analyze CSV, XLSX, or text-based PDF without executing embedded content."""
    path = Path(file_path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("Input must be an existing regular file")
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED:
        raise ValueError("Supported formats: CSV, XLSX, PDF")
    size = path.stat().st_size
    if size <= 0 or size > min(int(max_bytes), MAX_FILE_BYTES):
        raise ValueError("File is empty or exceeds the 20 MiB analysis limit")

    if suffix == ".pdf":
        from tamanna_ai.knowledge.document_loader import load_document_text
        content = load_document_text(path, max_bytes=max_bytes)
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        return {
            "source": path.name, "format": "pdf_text", "page_text_lines": len(lines),
            "text_characters": len(content), "preview": lines[:40],
            "limitations": ["PDF extraction is text-only; scanned pages require OCR.",
                            "Extracted tables may need manual verification."],
        }

    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            sample = stream.read(8192)
            stream.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
            except csv.Error:
                dialect = csv.excel
            reader = csv.reader(stream, dialect)
            headers = next(reader, [])
            if not headers or len(headers) > MAX_COLUMNS:
                raise ValueError("CSV must contain 1 to 200 columns")
            rows = []
            for row in reader:
                if len(rows) >= MAX_ROWS:
                    raise ValueError("CSV exceeds the 100,000-row analysis limit")
                rows.append(row[:MAX_COLUMNS])
        result = _summarize_rows([str(h) for h in headers], rows, path.name)
        result["format"] = "csv"
        return result

    try:
        from openpyxl import load_workbook
    except ImportError as exc:
        raise RuntimeError("XLSX analysis requires optional dependency: openpyxl") from exc
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        if not workbook.worksheets:
            raise ValueError("Workbook contains no worksheets")
        sheet = workbook.worksheets[0]
        iterator = sheet.iter_rows(values_only=True)
        header_row = next(iterator, None)
        headers = [str(value or f"column_{i+1}") for i, value in enumerate(header_row or ())]
        if not headers or len(headers) > MAX_COLUMNS:
            raise ValueError("Worksheet must contain 1 to 200 columns")
        rows = []
        for row in iterator:
            if len(rows) >= MAX_ROWS:
                raise ValueError("Worksheet exceeds the 100,000-row analysis limit")
            rows.append(list(row[:MAX_COLUMNS]))
        result = _summarize_rows(headers, rows, path.name)
        result["format"] = "xlsx"
        result["worksheet"] = sheet.title
        return result
    finally:
        workbook.close()


__all__ = ["analyze_file"]
