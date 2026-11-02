"""Tests for explicit-approval learning dataset collection."""

import pytest

from tamanna_ai.learning.trainer import LearningTrainer


def test_trainer_requires_explicit_approval(tmp_path, monkeypatch):
    # Use a temporary file-backed store by patching the shared memory facade.
    from tamanna_ai.memory.memory_store import MemoryStore
    import tamanna_ai.memory.memory as memory_module

    store = MemoryStore(path=tmp_path / "memory.json")
    monkeypatch.setattr(memory_module, "memory_store", store)
    trainer = LearningTrainer()

    with pytest.raises(PermissionError):
        trainer.add_example("prompt", "answer")

    result = trainer.add_example("prompt", "answer", approved=True)
    assert result == {"status": "stored", "count": 1}
    assert trainer.list_examples() == [
        {"prompt": "prompt", "answer": "answer", "metadata": {}}
    ]
    assert trainer.dataset_status()["model_training_performed"] is False
