from dataclasses import dataclass


@dataclass
class NPC:
    """Non-player character with optional associated dialogue."""

    id: str
    name: str
    description: str
    dialogue_id: str | None = None
