# Tamanna AI Training Data Pipeline

A local-first dataset preparation pipeline for text, source code, conversational records and multimedia metadata. It **does not train or fine-tune a model**, download public datasets, or upload user data.

## Run

```bash
python -m data.training_pipeline.cli ./my_dataset ./private_dataset_output
```

The output directory must be outside the source directory. Outputs:

- `cleaned.jsonl`: accepted, normalized text/code records with source filename and redaction flags.
- `media_manifest.jsonl`: validated image/audio/video/PDF metadata (kind, MIME type, format, size and SHA-256).
- `images_manifest.jsonl`: backward-compatible image-only manifest for existing consumers.
- `quality_report.json`: accepted/rejected records, duplicates, short/empty records, redactions and media counts.
- `skipped_files.json`: unsupported, invalid or oversized files and reasons.

## Supported data

- **Text and documents:** TXT, Markdown, reStructuredText, HTML, JSON, JSONL, YAML and TOML.
- **Code repositories:** Python, JavaScript/JSX, TypeScript/TSX, Java, Kotlin, Go, Rust, C/C++, C#, PHP, Ruby, Swift, Dart, CSS/SCSS, SQL and shell scripts.
- **Conversational data:** JSONL rows with `text`/`content`, or chat pairs using `user` + `assistant`. The SFT exporter also accepts `prompt` + `response` and `instruction` + `output`.
- **Multimedia:** JPG/JPEG, PNG, WEBP, GIF, BMP; MP3, WAV, OGG, FLAC, M4A, AAC; MP4, WEBM, MOV, MKV; and PDF. Files up to 20 MiB are signature-checked and indexed. Text/code files are limited to 2 MiB by default.

## What multimedia support means

The current dataset pipeline validates file signatures and writes metadata manifests only. It does **not** decode pixels, transcribe audio, extract video frames, parse PDF pages, create captions/labels, or create model-ready multimodal training examples. Those require dedicated decoders, transcription/OCR/annotation stages, a selected multimodal model, and separate evaluation.

## Privacy, quality and licensing

- Raw source files are never modified.
- Detectable PII is redacted: email addresses, phone-like strings, labelled names/addresses, common government-ID formats (including UAE Emirates ID and US SSN), and payment-card candidates passing the Luhn checksum. API keys, tokens, passwords and private-key assignments are also redacted. Only category flags, not matched values, are recorded.
- Empty, short and duplicate records are excluded.
- Chat histories may contain sensitive personal data. Use only data with a valid legal basis and appropriate user consent; minimize, anonymize, review and restrict access before training.
- Use books, articles, Wikipedia, GitHub repositories and websites only where the source license and terms permit the intended training use. Keep provenance and license records.
- Detection is heuristic, not a guarantee: unlabelled names, free-form addresses, unfamiliar passport/ID formats, indirect identifiers, and PII inside images/audio/video may remain. Add a reviewed NER/DLP stage and human review for high-risk data. This local pipeline does not crawl websites or authenticate to sources; never supply private/password-protected material. Provenance approval does not prove a source is public or licensed. It does not automatically identify piracy/copyright infringement or classify hate, sexual, violent, or other harmful content; apply a separately evaluated moderation policy and quarantine uncertain records before training. Human review is required.
- Keep private datasets and generated output out of GitHub. Never include API keys, passwords, session tokens or private user conversations in a public repository.

## SFT and preference data

Prepare reviewed prompt/response examples:

```bash
python -m data.learning_systems.cli sft ./reviewed_sft.jsonl ./private_learning/sft.jsonl
python -m data.learning_systems.cli preferences ./human_feedback.jsonl ./private_learning/preferences.jsonl
```

Preference pairs require `human_reviewed: true` and an explicit `preferred: "a"` or `"b"`. SFT export is data formatting only. Exporting a dataset does not change model weights or run SFT, DPO, PPO or RLHF.

## Tests

```bash
python -m unittest discover -s tests -p 'test_*.py'
```


## Source provenance and training-use approval

You can require explicit provenance for every ingested file:

```bash
python -m data.training_pipeline.cli ./licensed_sources ./private_dataset_output --provenance ./source_manifest.json
```

The JSON manifest is an array with one record per relative filename. Example:

```json
[
  {
    "file": "article.md",
    "category": "article",
    "source_url": "https://example.org/article",
    "license": "CC-BY-4.0",
    "license_url": "https://creativecommons.org/licenses/by/4.0/",
    "training_use_allowed": true,
    "reviewed_by": "dataset-reviewer"
  }
]
```

When a provenance manifest is supplied, files without a matching entry or
explicit `training_use_allowed: true` are skipped or rejected. Categories
include website, article, book, code, technical documentation, and research
paper. A license label alone is not legal advice: verify the actual license,
terms, attribution, share-alike, privacy, and jurisdictional requirements for
the intended training use. Do not assume that publicly reachable content is
free to train on. Keep the manifest and source snapshots with the private
dataset for auditability.

The pipeline still performs dataset preparation only. It does not crawl the
web, download books/papers/repositories, determine legal rights automatically,
or pre-train/fine-tune model weights.
