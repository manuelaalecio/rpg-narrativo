from typing import Protocol

from domain.entities.dialogue import Dialogue
from domain.entities.item import Item
from domain.entities.map import GameMap
from domain.entities.npc import NPC


class ContentRepositoryPort(Protocol):
    """Contract for accessing game content (map, rooms, items, NPCs, dialogues)."""

    def get_map(self) -> GameMap:
        """Return the complete game map with all rooms."""
        ...

    def get_item(self, item_id: str) -> Item:
        """Return the item definition for the given id."""
        ...

    def get_npc(self, npc_id: str) -> NPC:
        """Return the NPC definition for the given id."""
        ...

    def get_dialogue(self, dialogue_id: str) -> Dialogue:
        """Return the dialogue graph for the given id."""
        ...
