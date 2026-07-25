from dataclasses import dataclass


@dataclass
class ItemPickedUp:
    """Event published when the player picks up an item from a room."""

    item_id: str
    room_id: str
