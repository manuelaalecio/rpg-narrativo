from dataclasses import dataclass


@dataclass
class PlayerMoved:
    """Event published when the player moves from one room to another."""

    from_room_id: str
    to_room_id: str
