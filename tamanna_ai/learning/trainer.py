"""Curated learning-example storage.

This module prepares an explicitly approved dataset. It does not train model
weights, upload examples, or collect conversation data automatically.
"""

from __future__ import annotations

from typing import Any

from ..memory.memory import recall, remember

DATASET_KEY = "curated_learning_examples"
MAX_EXAMPLES = 10_000


class LearningTrainer:
    """Store user-approved prompt/answer examples for later model training."""

    def add_example(
        self,
        prompt: str,
        answer: str,
        *,
        approved: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if approved is not True:
            raise PermissionError("Explicit approval is required to store an example.")

        prompt = str(prompt).strip()
        answer = str(answer).strip()
        if not prompt or not answer:
            raise ValueError("Both prompt and answer are required.")

        examples = recall(DATASET_KEY, [])
        if not isinstance(examples, list):
            raise RuntimeError("Curated learning dataset is not a JSON list.")
        if len(examples) >= MAX_EXAMPLES:
            raise OverflowError(f"Learning dataset limit ({MAX_EXAMPLES}) reached.")

        item = {
            "prompt": prompt,
            "answer": answer,
            "metadata": metadata or {},
        }
        examples.append(item)
        remember(DATASET_KEY, examples)
        return {"status": "stored", "count": len(examples)}

    def list_examples(self, limit: int = 100) -> list[dict[str, Any]]:
        if not 1 <= int(limit) <= MAX_EXAMPLES:
            raise ValueError("limit must be between 1 and 10000.")
        examples = recall(DATASET_KEY, [])
        if not isinstance(examples, list):
            raise RuntimeError("Curated learning dataset is not a JSON list.")
        return examples[-int(limit):]

    def dataset_status(self) -> dict[str, Any]:
        examples = recall(DATASET_KEY, [])
        if not isinstance(examples, list):
            raise RuntimeError("Curated learning dataset is not a JSON list.")
        return {
            "count": len(examples),
            "limit": MAX_EXAMPLES,
            "model_training_performed": False,
        }


learning_trainer = LearningTrainer()

__all__ = ["LearningTrainer", "learning_trainer", "MAX_EXAMPLES"]
