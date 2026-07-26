from dataclasses import dataclass


@dataclass
class ItemUsed:
    """Event published when a player uses an item."""

    item_id: str
    player_id: str
