from enum import Enum


class GameState(Enum):
    """Possible game states/screens."""

    MAIN_MENU = "main_menu"
    LOADING = "loading"
    EXPLORATION = "exploration"
    DIALOGUE = "dialogue"
    COMBAT = "combat"
    INVENTORY = "inventory"
    PAUSED = "paused"
