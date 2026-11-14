"""User-scoped learning facade over the canonical persistence adapter."""
from tamanna_ai.learning.memory import LearningMemory

class BrainLearning:
    def __init__(self, memory=None):
        self.memory = memory if memory is not None else LearningMemory()
    def learn(self, content, *, user_id, metadata=None):
        return self.memory.remember(content, user_id=user_id, metadata=metadata)
    def recall(self, *, user_id, limit=100):
        return self.memory.recall(user_id=user_id, limit=limit)

__all__ = ["BrainLearning"]
