"""Domain event published when a game is loaded."""

from dataclasses import dataclass


@dataclass
class GameLoaded:
    """Event published when player loads a saved game."""

    save_id: str
    slot: str
