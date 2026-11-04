"""Safe, bounded text extraction from user-selected knowledge documents."""
from __future__ import annotations

from pathlib import Path

SUPPORTED = {".txt", ".md", ".rst", ".pdf", ".docx"}


def load_document_text(file_path: str | Path, *, max_bytes: int = 10 * 1024 * 1024) -> str:
    path = Path(file_path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("Document must be an existing regular file")
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED:
        raise ValueError("Supported formats: TXT, Markdown, RST, PDF, DOCX")
    size = path.stat().st_size
    if size <= 0 or size > max_bytes:
        raise ValueError("Document is empty or exceeds the configured size limit")
    if suffix in {".txt", ".md", ".rst"}:
        return path.read_text(encoding="utf-8")
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("PDF support requires optional dependency: pypdf") from exc
        reader = PdfReader(str(path), strict=True)
        if reader.is_encrypted:
            raise ValueError("Encrypted PDFs are not supported")
        if len(reader.pages) > 500:
            raise ValueError("PDF exceeds the 500-page limit")
        return "\n\n".join((page.extract_text() or "") for page in reader.pages)
    try:
        from docx import Document
    except ImportError as exc:
        raise RuntimeError("DOCX support requires optional dependency: python-docx") from exc
    document = Document(str(path))
    return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())


__all__ = ["load_document_text"]
