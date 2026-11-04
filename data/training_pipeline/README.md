# Tamanna AI Dataset Pipeline

A local-first, dependency-free starter pipeline for preparing **text and source-code** datasets. It does not train or fine-tune a model and does not download datasets or upload data anywhere.

## Run

```bash
python -m data.training_pipeline.cli ./my_dataset ./private_dataset_output
```

The output directory must be outside the source directory. The pipeline writes:

- `cleaned.jsonl`: accepted text records with source filename and redaction flags.
- `images_manifest.jsonl`: validated local image file metadata (format, size and SHA-256); image bytes are not copied or uploaded.
- `quality_report.json`: counts for accepted/rejected records, duplicates, short/empty records and redactions.
- `skipped_files.json`: files/JSONL rows that could not be processed and reasons.

Supported text/code extensions: TXT, MD, PY, JS/JSX, TS/TSX, JSON, JSONL, YAML, HTML and CSS. Files larger than 2 MiB are skipped by default. JSON/JSONL records may use a `text` or `content` field. Images and other binary files are intentionally not ingested as text; image training requires a separate vision model, licensed image dataset, labels/captions, and a dedicated image preprocessing pipeline.

## Safety and quality

- Raw input files are never changed.
- Common email addresses, phone-like strings and credential assignments are redacted before output.
- Empty, short and duplicate records are excluded.
- This is a heuristic filter, not a complete harmful-content, privacy, copyright or factuality detector. Review samples and source licenses before training.
- Keep datasets and generated output private; do not commit private, personal, copyrighted or secret data to GitHub.
- The pipeline creates a dataset only. Connect it to a model-training job only after selecting a model, approved data sources, compute budget and evaluation set.

## Tests

```bash
python -m unittest discover -s tests -p 'test_*.py'
```
