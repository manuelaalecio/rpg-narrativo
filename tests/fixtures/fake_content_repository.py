from domain.entities.dialogue import Dialogue
from domain.entities.item import Item
from domain.entities.map import GameMap
from domain.entities.npc import NPC
from domain.entities.quest import Quest


class FakeContentRepository:
    """In-memory fake content repository for testing."""

    def __init__(
        self,
        game_map: GameMap,
        items: dict[str, Item] | None = None,
        npcs: dict[str, NPC] | None = None,
        dialogues: dict[str, Dialogue] | None = None,
        quests: dict[str, Quest] | None = None,
    ) -> None:
        self._game_map = game_map
        self._items = items or {}
        self._npcs = npcs or {}
        self._dialogues = dialogues or {}
        self._quests = quests or {}

    def get_map(self) -> GameMap:
        return self._game_map

    def get_item(self, item_id: str) -> Item:
        return self._items[item_id]

    def get_npc(self, npc_id: str) -> NPC:
        return self._npcs[npc_id]

    def get_dialogue(self, dialogue_id: str) -> Dialogue:
        return self._dialogues[dialogue_id]

    def get_quest(self, quest_id: str) -> Quest:
        return self._quests[quest_id]

    def get_all_quests(self) -> dict[str, Quest]:
        return self._quests
