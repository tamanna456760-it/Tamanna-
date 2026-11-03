"""Tamanna AI Core Controller: Echo + Brain + Memory."""

from datetime import datetime
from typing import Any, Dict

from tamanna_ai.brain.brain import knowledge_brain
from tamanna_ai.tools.echo_power import tamanna_echo, power_status
from tamanna_ai.persistence.database import database


class TamannaController:
    """Coordinate basic responses, knowledge and system status."""

    def __init__(self):
        self.brain = knowledge_brain

    def respond(self, message: str) -> Dict[str, Any]:
        message = message.strip()

        if not message:
            return {
                "ok": False,
                "reply": "Please enter a message.",
            }

        lowered = message.lower()

        if lowered in {"status", "power", "system status"}:
            return {
                "ok": True,
                "reply": tamanna_echo("System status checked."),
                "power": power_status(),
            }

        if lowered.startswith("remember "):
            item = message[len("remember "):].strip()

            if not item:
                return {
                    "ok": False,
                    "reply": "Tell me what to remember.",
                }

            database.add_memory(item, metadata={"source": "chat_command"})
            return {
                "ok": True,
                "reply": tamanna_echo("I stored this in persistent memory."),
                "memory_count": len(database.list_memories()),
            }

        if lowered in {"recall", "memory"}:
            items = database.list_memories()
            return {
                "ok": True,
                "reply": "\n".join(items) if items else "No saved memories yet.",
                "memory_count": len(items),
            }

        thought = self.brain.think(message)

        return {
            "ok": True,
            "reply": tamanna_echo(
                "I received your message. I need a knowledge source or AI model "
                "to generate a more intelligent answer."
            ),
            "input": message,
            "brain": thought,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }


tamanna_controller = TamannaController()

__all__ = ["TamannaController", "tamanna_controller"]
