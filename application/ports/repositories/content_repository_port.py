from typing import Protocol

from domain.entities.item import Item
from domain.entities.map import GameMap


class ContentRepositoryPort(Protocol):
    """Contract for accessing game content (map, rooms, items)."""

    def get_map(self) -> GameMap:
        """Return the complete game map with all rooms."""
        ...

    def get_item(self, item_id: str) -> Item:
        """Return the item definition for the given id."""
        ...
