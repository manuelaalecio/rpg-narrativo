from typing import Protocol

from domain.entities.dialogue import Dialogue
from domain.entities.item import Item
from domain.entities.map import GameMap
from domain.entities.npc import NPC
from domain.entities.quest import Quest


class ContentRepositoryPort(Protocol):
    """Contract for accessing game content (map, rooms, items, NPCs, dialogues, quests)."""

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

    def get_quest(self, quest_id: str) -> Quest:
        """Return the quest definition for the given id."""
        ...

    def get_all_quests(self) -> dict[str, Quest]:
        """Return all quests indexed by id."""
        ...
