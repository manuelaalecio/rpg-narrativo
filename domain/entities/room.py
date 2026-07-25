from dataclasses import dataclass, field


@dataclass
class Room:
    """A game scenario location with exits, items, and NPCs."""

    id: str
    name: str
    description: str
    exits: dict[str, str] = field(default_factory=dict)
    item_ids: list[str] = field(default_factory=list)
    npc_ids: list[str] = field(default_factory=list)

    def get_exit(self, direction: str) -> str | None:
        """Return the room id for the given direction, or None if no exit exists."""
        return self.exits.get(direction)

    def add_item(self, item_id: str) -> None:
        """Add an item to this room."""
        self.item_ids.append(item_id)

    def remove_item(self, item_id: str) -> None:
        """Remove an item from this room. Raises ValueError if not present."""
        self.item_ids.remove(item_id)
