from enum import Enum


class ItemType(Enum):
    """Classification of item types available in the game."""

    WEAPON = "weapon"
    CONSUMABLE = "consumable"
    KEY = "key"
    MISC = "misc"
