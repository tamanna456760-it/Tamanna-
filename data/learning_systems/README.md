# Tamanna AI Learning Systems

This module prepares training/evaluation data. It does **not** fine-tune Gemini or any other model, change model weights, or run reinforcement learning. A model-specific trainer, approved base model, compute environment, and evaluation gate must be selected separately.

## 1. Supervised Fine-Tuning (SFT)

Create a JSONL input file where each line contains `prompt` and `response` (or `instruction` and `output`). Only include examples that are accurate, licensed/owned, and reviewed.

```bash
python -m data.learning_systems.cli sft ./reviewed_sft.jsonl ./private_learning/sft.jsonl
```

The output uses chat `messages` format (user + assistant). Invalid, short, duplicate rows are rejected; common emails, phone-like values, and credential assignments are redacted.

## 2. Human preference / RLHF preparation

Each input JSONL row must contain `prompt`, `response_a`, `response_b`, `preferred` (`a` or `b`), and the explicit boolean `human_reviewed: true`. The preferred answer becomes `chosen`; the other becomes `rejected`.

```bash
python -m data.learning_systems.cli preferences ./human_feedback.jsonl ./private_learning/preferences.jsonl
```

Unreviewed, ambiguous, invalid and duplicate rows are rejected. The pipeline does not invent human feedback or automatically decide which answer is better. This is preference-data preparation, not a complete RLHF trainer; DPO or reward-model/PPO training needs a separate, model-compatible training stack.

## Quality and safety gates

- Keep source data private; generated datasets should stay outside Git and are covered by root ignore rules for private dataset output folders.
- Collect feedback with clear user consent; avoid sensitive personal data and secrets.
- Have reviewers check factuality, harmful content, bias, privacy, and source rights.
- Maintain a held-out evaluation set. Never use test/evaluation examples as training data.
- Compare the candidate model against the current baseline before deployment; require human approval and a rollback path.
- Fine-tuning does not guarantee truth. Use retrieval, citations, and factuality evaluation for knowledge accuracy.
