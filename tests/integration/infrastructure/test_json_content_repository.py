from pathlib import Path

import pytest

from domain.entities.item import Item
from domain.entities.map import GameMap
from domain.entities.room import Room
from domain.value_objects.item_type import ItemType
from infrastructure.content_loader.json_content_repository import JsonContentRepository
from infrastructure.exceptions import ContentLoadError

FIXTURES_PATH = Path(__file__).parent.parent.parent / "fixtures" / "json_data"


@pytest.fixture
def repo() -> JsonContentRepository:
    return JsonContentRepository(FIXTURES_PATH)


class TestJsonContentRepository:
    def test_loads_rooms_into_map(self, repo: JsonContentRepository) -> None:
        game_map = repo.get_map()
        assert isinstance(game_map, GameMap)
        assert game_map.has_room("test_room_01")
        assert game_map.has_room("test_room_02")

    def test_room_fields_parsed_correctly(self, repo: JsonContentRepository) -> None:
        room = repo.get_map().get_room("test_room_01")
        assert isinstance(room, Room)
        assert room.name == "Test Hall"
        assert room.description == "A test hall."
        assert room.exits == {"north": "test_room_02"}
        assert room.item_ids == ["test_item_01"]
        assert room.npc_ids == []

    def test_loads_items(self, repo: JsonContentRepository) -> None:
        item = repo.get_item("test_item_01")
        assert isinstance(item, Item)
        assert item.name == "Test Sword"
        assert item.item_type == ItemType.WEAPON
        assert item.usable is False
        assert item.stackable is False

    def test_item_consumable_type(self, repo: JsonContentRepository) -> None:
        item = repo.get_item("test_item_02")
        assert item.item_type == ItemType.CONSUMABLE
        assert item.usable is True
        assert item.stackable is True

    def test_missing_rooms_directory_raises(self, tmp_path: Path) -> None:
        (tmp_path / "items").mkdir()
        with pytest.raises(ContentLoadError, match="Rooms directory does not exist"):
            JsonContentRepository(tmp_path)

    def test_missing_items_directory_raises(self, tmp_path: Path) -> None:
        (tmp_path / "rooms").mkdir()
        with pytest.raises(ContentLoadError, match="Items directory does not exist"):
            JsonContentRepository(tmp_path)

    def test_invalid_json_raises(self, tmp_path: Path) -> None:
        rooms_dir = tmp_path / "rooms"
        items_dir = tmp_path / "items"
        rooms_dir.mkdir()
        items_dir.mkdir()
        (rooms_dir / "bad.json").write_text("{invalid json", encoding="utf-8")
        with pytest.raises(ContentLoadError, match="Invalid JSON"):
            JsonContentRepository(tmp_path)

    def test_missing_required_field_raises(self, tmp_path: Path) -> None:
        rooms_dir = tmp_path / "rooms"
        items_dir = tmp_path / "items"
        rooms_dir.mkdir()
        items_dir.mkdir()
        (rooms_dir / "incomplete.json").write_text('{"id": "x"}', encoding="utf-8")
        with pytest.raises(ContentLoadError, match="Missing required field"):
            JsonContentRepository(tmp_path)

    def test_invalid_item_type_raises(self, tmp_path: Path) -> None:
        rooms_dir = tmp_path / "rooms"
        items_dir = tmp_path / "items"
        rooms_dir.mkdir()
        items_dir.mkdir()
        (items_dir / "bad_type.json").write_text(
            '{"id": "x", "name": "X", "description": "X", "item_type": "invalid"}',
            encoding="utf-8",
        )
        with pytest.raises(ContentLoadError, match="Invalid item_type"):
            JsonContentRepository(tmp_path)

    def test_empty_directories_load_successfully(self, tmp_path: Path) -> None:
        (tmp_path / "rooms").mkdir()
        (tmp_path / "items").mkdir()
        repo = JsonContentRepository(tmp_path)
        assert repo.get_map().room_ids == []
