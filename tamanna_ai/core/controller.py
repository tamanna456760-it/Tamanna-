"""Tamanna AI Core Controller: Echo + Brain + Memory."""

from datetime import datetime
from typing import Any, Dict, Optional

from tamanna_ai.brain.brain import knowledge_brain
from tamanna_ai.tools.echo_power import tamanna_echo, power_status


class TamannaController:
    """Coordinate basic responses, knowledge and system status."""

    def __init__(self, brain: Optional[Any] = None):
        # Dependency injection keeps tests and future per-user sessions isolated.
        self.brain = brain if brain is not None else knowledge_brain

    def respond(self, message: str) -> Dict[str, Any]:
        """Handle a text command and return a stable response dictionary."""
        if not isinstance(message, str):
            return {
                "ok": False,
                "reply": "Message must be text.",
            }

        message = message.strip()
        if not message:
            return {
                "ok": False,
                "reply": "Please enter a message.",
            }

        lowered = message.casefold()

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

            self.brain.learn(item)
            return {
                "ok": True,
                "reply": tamanna_echo("I stored this in the current session."),
                "memory_count": len(self.brain.recall()),
            }

        if lowered in {"recall", "memory"}:
            items = self.brain.recall()
            return {
                "ok": True,
                "reply": "\n".join(items) if items else "No session memories yet.",
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
