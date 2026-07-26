"""Integration tests for JsonSaveGameRepository."""

import json
from datetime import datetime
from pathlib import Path

import pytest

from domain.entities.save_game import SaveGame
from infrastructure.exceptions import SaveCorruptedError, SaveNotFoundError
from infrastructure.persistence.json_save_game_repository import JsonSaveGameRepository


@pytest.fixture
def temp_save_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for save files."""
    save_dir = tmp_path / "saves"
    save_dir.mkdir()
    return save_dir


@pytest.fixture
def repo(temp_save_dir: Path) -> JsonSaveGameRepository:
    """Create a JsonSaveGameRepository with temporary directory."""
    return JsonSaveGameRepository(temp_save_dir)


class TestJsonSaveGameRepository:
    def test_save_and_load(self, repo: JsonSaveGameRepository) -> None:
        save = SaveGame(
            save_id="slot_1",
            save_name="Test Save",
            timestamp=datetime(2026, 1, 15, 10, 30, 0),
            player_id="player_01",
            player_name="Hero",
            current_room_id="room_02",
            health=80,
            max_health=100,
            inventory={"item_sword": 1, "item_potion": 3},
        )

        repo.save(save, "slot_1")
        loaded = repo.load("slot_1")

        assert loaded.save_id == save.save_id
        assert loaded.save_name == save.save_name
        assert loaded.timestamp == save.timestamp
        assert loaded.player_id == save.player_id
        assert loaded.player_name == save.player_name
        assert loaded.current_room_id == save.current_room_id
        assert loaded.health == save.health
        assert loaded.max_health == save.max_health
        assert loaded.inventory == save.inventory

    def test_load_nonexistent(self, repo: JsonSaveGameRepository) -> None:
        with pytest.raises(SaveNotFoundError):
            repo.load("nonexistent")

    def test_load_corrupted_json(self, repo: JsonSaveGameRepository, temp_save_dir: Path) -> None:
        # Create a corrupted JSON file
        corrupted_file = temp_save_dir / "corrupted.json"
        corrupted_file.write_text("{invalid json", encoding="utf-8")

        with pytest.raises(SaveCorruptedError):
            repo.load("corrupted")

    def test_load_invalid_data(self, repo: JsonSaveGameRepository, temp_save_dir: Path) -> None:
        # Create a valid JSON but with missing required fields
        invalid_file = temp_save_dir / "invalid.json"
        invalid_file.write_text('{"save_id": "invalid"}', encoding="utf-8")

        with pytest.raises(SaveCorruptedError):
            repo.load("invalid")

    def test_list_saves(self, repo: JsonSaveGameRepository) -> None:
        # Create multiple saves
        save1 = SaveGame(
            save_id="slot_1",
            save_name="First Save",
            timestamp=datetime(2026, 1, 10, 10, 0, 0),
            player_id="player_01",
            player_name="Hero",
            current_room_id="room_01",
            health=100,
            max_health=100,
            inventory={},
        )
        save2 = SaveGame(
            save_id="slot_2",
            save_name="Second Save",
            timestamp=datetime(2026, 1, 15, 14, 30, 0),
            player_id="player_01",
            player_name="Hero",
            current_room_id="room_05",
            health=80,
            max_health=100,
            inventory={"item_sword": 1},
        )

        repo.save(save1, "slot_1")
        repo.save(save2, "slot_2")

        saves = repo.list_saves()

        assert len(saves) == 2
        # Should be sorted by timestamp, newest first
        assert saves[0].slot == "slot_2"
        assert saves[0].save_name == "Second Save"
        assert saves[1].slot == "slot_1"
        assert saves[1].save_name == "First Save"

    def test_list_saves_skips_corrupted(self, repo: JsonSaveGameRepository, temp_save_dir: Path) -> None:
        # Create a valid save
        save = SaveGame(
            save_id="slot_1",
            save_name="Valid",
            timestamp=datetime.now(),
            player_id="player_01",
            player_name="Hero",
            current_room_id="room_01",
            health=100,
            max_health=100,
            inventory={},
        )
        repo.save(save, "slot_1")

        # Create a corrupted file
        corrupted_file = temp_save_dir / "corrupted.json"
        corrupted_file.write_text("{invalid", encoding="utf-8")

        saves = repo.list_saves()

        # Should only return the valid save
        assert len(saves) == 1
        assert saves[0].slot == "slot_1"

    def test_delete(self, repo: JsonSaveGameRepository) -> None:
        save = SaveGame(
            save_id="slot_1",
            save_name="To Delete",
            timestamp=datetime.now(),
            player_id="player_01",
            player_name="Hero",
            current_room_id="room_01",
            health=100,
            max_health=100,
            inventory={},
        )
        repo.save(save, "slot_1")

        repo.delete("slot_1")

        with pytest.raises(SaveNotFoundError):
            repo.load("slot_1")

    def test_delete_nonexistent(self, repo: JsonSaveGameRepository) -> None:
        with pytest.raises(SaveNotFoundError):
            repo.delete("nonexistent")

    def test_overwrite_save(self, repo: JsonSaveGameRepository) -> None:
        save1 = SaveGame(
            save_id="slot_1",
            save_name="First",
            timestamp=datetime(2026, 1, 10, 10, 0, 0),
            player_id="player_01",
            player_name="Hero",
            current_room_id="room_01",
            health=100,
            max_health=100,
            inventory={},
        )
        save2 = SaveGame(
            save_id="slot_1",
            save_name="Second",
            timestamp=datetime(2026, 1, 15, 14, 30, 0),
            player_id="player_01",
            player_name="Hero",
            current_room_id="room_05",
            health=80,
            max_health=100,
            inventory={"item_sword": 1},
        )

        repo.save(save1, "slot_1")
        repo.save(save2, "slot_1")

        loaded = repo.load("slot_1")
        assert loaded.save_name == "Second"
        assert loaded.current_room_id == "room_05"
        assert loaded.health == 80
