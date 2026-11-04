"""Prepare supervised fine-tuning examples; does not train a model."""

from __future__ import annotations

import json
from pathlib import Path

from data.training_pipeline.cleaning import clean_text


def export_sft_dataset(source_path: str | Path, output_path: str | Path, *, min_chars: int = 2) -> dict:
    """Convert reviewed prompt/response JSONL into chat-format SFT JSONL.

    Accepted source keys: prompt + response, instruction + output, or user + assistant.
    """
    source = Path(source_path)
    output = Path(output_path)
    if source.resolve() == output.resolve():
        raise ValueError("Input and output paths must be different")
    accepted = rejected = redactions = 0
    seen: set[tuple[str, str]] = set()
    output.parent.mkdir(parents=True, exist_ok=True)
    with source.open(encoding="utf-8") as src, output.open("w", encoding="utf-8") as dst:
        for line_number, line in enumerate(src, 1):
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                rejected += 1
                continue
            if not isinstance(row, dict):
                rejected += 1
                continue
            prompt = str(row.get("prompt") or row.get("instruction") or row.get("user") or "").strip()
            response = str(row.get("response") or row.get("output") or row.get("assistant") or "").strip()
            if len(prompt) < min_chars or len(response) < min_chars:
                rejected += 1
                continue
            prompt, pflags = clean_text(prompt)
            response, rflags = clean_text(response)
            pair = (prompt.casefold(), response.casefold())
            if pair in seen:
                rejected += 1
                continue
            seen.add(pair)
            record = {
                "messages": [
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": response},
                ],
                "metadata": {"source_line": line_number, "human_reviewed": bool(row.get("human_reviewed", False))},
            }
            dst.write(json.dumps(record, ensure_ascii=False) + "\n")
            accepted += 1
            redactions += len(pflags) + len(rflags)
    return {"accepted": accepted, "rejected": rejected, "redactions": redactions, "output": str(output)}
