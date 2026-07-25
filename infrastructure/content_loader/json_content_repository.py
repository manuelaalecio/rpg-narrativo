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
    "stackable": false
}

item_type must be one of: "weapon", "consumable", "key", "misc"
(must match ItemType enum values in domain/value_objects/item_type.py)
"""

import json
from pathlib import Path

from domain.entities.item import Item
from domain.entities.map import GameMap
from domain.entities.room import Room
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
        self._load_all()

    def _load_all(self) -> None:
        """Load all rooms and items from JSON files into memory."""
        self._load_rooms()
        self._load_items()

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
            return Item(
                id=data["id"],
                name=data["name"],
                description=data["description"],
                item_type=item_type,
                usable=data.get("usable", False),
                stackable=data.get("stackable", False),
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
