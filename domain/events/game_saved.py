"""Domain event published when a game is saved."""

from dataclasses import dataclass


@dataclass
class GameSaved:
    """Event published when player saves the game."""

    save_id: str
    slot: str
