"""Build preference pairs from explicit human judgments only."""

from __future__ import annotations

import json
from pathlib import Path

from data.training_pipeline.cleaning import clean_text


def export_preference_dataset(source_path: str | Path, output_path: str | Path, *, min_chars: int = 2) -> dict:
    """Export prompt/chosen/rejected pairs only when human_reviewed is true.

    Input fields: prompt, response_a, response_b, preferred ('a' or 'b'),
    and human_reviewed=true. Unreviewed or ambiguous rows are rejected.
    """
    source = Path(source_path)
    output = Path(output_path)
    if source.resolve() == output.resolve():
        raise ValueError("Input and output paths must be different")
    accepted = rejected = redactions = 0
    seen: set[tuple[str, str, str]] = set()
    output.parent.mkdir(parents=True, exist_ok=True)
    with source.open(encoding="utf-8") as src, output.open("w", encoding="utf-8") as dst:
        for line_number, line in enumerate(src, 1):
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                rejected += 1
                continue
            if not isinstance(row, dict) or row.get("human_reviewed") is not True:
                rejected += 1
                continue
            prompt = str(row.get("prompt", "")).strip()
            response_a = str(row.get("response_a", "")).strip()
            response_b = str(row.get("response_b", "")).strip()
            preferred = row.get("preferred")
            if preferred not in {"a", "b"} or min(map(len, (prompt, response_a, response_b))) < min_chars:
                rejected += 1
                continue
            chosen, rejected_response = (response_a, response_b) if preferred == "a" else (response_b, response_a)
            prompt, pflags = clean_text(prompt)
            chosen, cflags = clean_text(chosen)
            rejected_response, rflags = clean_text(rejected_response)
            key = (prompt.casefold(), chosen.casefold(), rejected_response.casefold())
            if key in seen:
                rejected += 1
                continue
            seen.add(key)
            dst.write(json.dumps({
                "prompt": prompt,
                "chosen": chosen,
                "rejected": rejected_response,
                "metadata": {"source_line": line_number, "human_reviewed": True},
            }, ensure_ascii=False) + "\n")
            accepted += 1
            redactions += len(pflags) + len(cflags) + len(rflags)
    return {"accepted": accepted, "rejected": rejected, "redactions": redactions, "output": str(output)}
