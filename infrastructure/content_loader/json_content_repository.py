"""JSON content loader — Factory that converts JSON files into domain entities.

JSON Schema
-----------

Room (data/rooms/<room_id>.json):
{
    "id": "room_01",
    "name": "Room Name",
    "description": "Text description shown to the player.",
    "exits": {"north": "room_02", "east": "room_03"},
    "item_ids": ["item_sword_01"],
    "npc_ids": []
}

Item (data/items/<item_id>.json):
{
    "id": "item_sword_01",
    "name": "Iron Sword",
    "description": "A sturdy iron sword.",
    "item_type": "weapon",
    "usable": false,
    "stackable": false,
    "effect": null
}

Usable items may include an "effect" field:
{
    "effect": {"effect_type": "heal", "value": 30}
}

item_type must be one of: "weapon", "consumable", "key", "misc"
effect_type must be one of: "heal"
(must match enum values in domain/value_objects/)

NPC (data/npcs/<npc_id>.json):
{
    "id": "npc_tavern_keeper",
    "name": "Tavern Keeper",
    "description": "A burly man behind the bar.",
    "dialogue_id": "dialogue_tavern_keeper"
}

Dialogue (data/dialogues/<dialogue_id>.json):
{
    "id": "dialogue_tavern_keeper",
    "start_node_id": "node_01",
    "nodes": {
        "node_01": {
            "id": "node_01",
            "npc_text": "Welcome to the tavern!",
            "options": [
                {"text": "Hello!", "next_node_id": "node_02"},
                {"text": "Show me the key.", "next_node_id": "node_03",
                 "condition": {"condition_type": "requires_item", "value": "item_old_key"}},
                {"text": "Goodbye.", "next_node_id": null}
            ]
        },
        "node_02": {
            "id": "node_02",
            "npc_text": "Nice to meet you.",
            "options": [{"text": "Goodbye.", "next_node_id": null}]
        },
        "node_03": {
            "id": "node_03",
            "npc_text": "Ah, you have the key! Here's a secret...",
            "options": [{"text": "Thanks!", "next_node_id": null}]
        }
    }
}

Conditions are structured data, never executable code.
Supported condition_type values: "requires_item"
"""

import json
from pathlib import Path

from domain.entities.dialogue import Condition, Dialogue, DialogueNode, DialogueOption
from domain.entities.item import Item
from domain.entities.map import GameMap
from domain.entities.npc import NPC
from domain.entities.room import Room
from domain.value_objects.item_effect import EffectType, ItemEffect
from domain.value_objects.item_type import ItemType
from infrastructure.exceptions import ContentLoadError


class JsonContentRepository:
    """Loads game content from JSON files and provides domain entities.

    All content is loaded eagerly at initialization. For future lazy loading,
    replace _load_all() with on-demand loading in get_map()/get_item(),
    caching results in self._map and self._items.
    """

    def __init__(self, data_path: Path) -> None:
        self._data_path = data_path
        self._map = GameMap()
        self._items: dict[str, Item] = {}
        self._npcs: dict[str, NPC] = {}
        self._dialogues: dict[str, Dialogue] = {}
        self._load_all()

    def _load_all(self) -> None:
        """Load all rooms, items, NPCs, and dialogues from JSON files into memory."""
        self._load_rooms()
        self._load_items()
        self._load_npcs()
        self._load_dialogues()

    def _load_rooms(self) -> None:
        rooms_dir = self._data_path / "rooms"
        if not rooms_dir.exists():
            raise ContentLoadError(str(rooms_dir), "Rooms directory does not exist")
        for json_file in sorted(rooms_dir.glob("*.json")):
            room = self._parse_room(json_file)
            self._map.add_room(room)

    def _load_items(self) -> None:
        items_dir = self._data_path / "items"
        if not items_dir.exists():
            raise ContentLoadError(str(items_dir), "Items directory does not exist")
        for json_file in sorted(items_dir.glob("*.json")):
            item = self._parse_item(json_file)
            self._items[item.id] = item

    def _parse_room(self, file_path: Path) -> Room:
        data = self._read_json(file_path)
        try:
            return Room(
                id=data["id"],
                name=data["name"],
                description=data["description"],
                exits=data.get("exits", {}),
                item_ids=data.get("item_ids", []),
                npc_ids=data.get("npc_ids", []),
            )
        except KeyError as e:
            raise ContentLoadError(str(file_path), f"Missing required field: {e}") from e

    def _parse_item(self, file_path: Path) -> Item:
        data = self._read_json(file_path)
        try:
            item_type_str = data["item_type"]
            try:
                item_type = ItemType(item_type_str)
            except ValueError:
                raise ContentLoadError(
                    str(file_path),
                    f"Invalid item_type '{item_type_str}'. Must be one of: {[t.value for t in ItemType]}",
                )
            effect = None
            if "effect" in data:
                effect_data = data["effect"]
                try:
                    effect_type = EffectType(effect_data["effect_type"])
                except ValueError:
                    raise ContentLoadError(
                        str(file_path),
                        f"Invalid effect_type '{effect_data['effect_type']}'. "
                        f"Must be one of: {[t.value for t in EffectType]}",
                    )
                effect = ItemEffect(effect_type=effect_type, value=effect_data["value"])
            return Item(
                id=data["id"],
                name=data["name"],
                description=data["description"],
                item_type=item_type,
                usable=data.get("usable", False),
                stackable=data.get("stackable", False),
                effect=effect,
            )
        except KeyError as e:
            raise ContentLoadError(str(file_path), f"Missing required field: {e}") from e

    def _read_json(self, file_path: Path) -> dict:
        try:
            text = file_path.read_text(encoding="utf-8")
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ContentLoadError(str(file_path), f"Invalid JSON: {e}") from e
        except OSError as e:
            raise ContentLoadError(str(file_path), f"Cannot read file: {e}") from e

    def get_map(self) -> GameMap:
        """Return the complete game map with all rooms."""
        return self._map

    def get_item(self, item_id: str) -> Item:
        """Return the item definition for the given id."""
        return self._items[item_id]

    def get_npc(self, npc_id: str) -> NPC:
        """Return the NPC definition for the given id."""
        return self._npcs[npc_id]

    def get_dialogue(self, dialogue_id: str) -> Dialogue:
        """Return the dialogue graph for the given id."""
        return self._dialogues[dialogue_id]

    def _load_npcs(self) -> None:
        npcs_dir = self._data_path / "npcs"
        if not npcs_dir.exists():
            return
        for json_file in sorted(npcs_dir.glob("*.json")):
            npc = self._parse_npc(json_file)
            self._npcs[npc.id] = npc

    def _load_dialogues(self) -> None:
        dialogues_dir = self._data_path / "dialogues"
        if not dialogues_dir.exists():
            return
        for json_file in sorted(dialogues_dir.glob("*.json")):
            dialogue = self._parse_dialogue(json_file)
            self._dialogues[dialogue.id] = dialogue

    def _parse_npc(self, file_path: Path) -> NPC:
        data = self._read_json(file_path)
        try:
            return NPC(
                id=data["id"],
                name=data["name"],
                description=data["description"],
                dialogue_id=data.get("dialogue_id"),
            )
        except KeyError as e:
            raise ContentLoadError(str(file_path), f"Missing required field: {e}") from e

    def _parse_dialogue(self, file_path: Path) -> Dialogue:
        data = self._read_json(file_path)
        try:
            nodes: dict[str, DialogueNode] = {}
            for node_id, node_data in data["nodes"].items():
                options = []
                for opt_data in node_data.get("options", []):
                    condition = None
                    if "condition" in opt_data:
                        cond_data = opt_data["condition"]
                        condition = Condition(
                            condition_type=cond_data["condition_type"],
                            value=cond_data["value"],
                        )
                    options.append(
                        DialogueOption(
                            text=opt_data["text"],
                            next_node_id=opt_data.get("next_node_id"),
                            condition=condition,
                        )
                    )
                nodes[node_id] = DialogueNode(
                    id=node_data["id"],
                    npc_text=node_data["npc_text"],
                    options=options,
                )
            return Dialogue(
                id=data["id"],
                start_node_id=data["start_node_id"],
                nodes=nodes,
            )
        except KeyError as e:
            raise ContentLoadError(str(file_path), f"Missing required field: {e}") from e
