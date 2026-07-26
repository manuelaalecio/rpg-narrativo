"""Unit tests for SaveGame entity."""

from datetime import datetime

from domain.entities.save_game import SaveGame


class TestSaveGame:
    def test_to_dict(self) -> None:
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

        data = save.to_dict()

        assert data["save_id"] == "slot_1"
        assert data["save_name"] == "Test Save"
        assert data["timestamp"] == "2026-01-15T10:30:00"
        assert data["player_id"] == "player_01"
        assert data["player_name"] == "Hero"
        assert data["current_room_id"] == "room_02"
        assert data["health"] == 80
        assert data["max_health"] == 100
        assert data["inventory"] == {"item_sword": 1, "item_potion": 3}

    def test_from_dict(self) -> None:
        data = {
            "save_id": "slot_2",
            "save_name": "Another Save",
            "timestamp": "2026-02-20T14:45:30",
            "player_id": "player_02",
            "player_name": "Warrior",
            "current_room_id": "room_05",
            "health": 50,
            "max_health": 120,
            "inventory": {"item_shield": 1},
        }

        save = SaveGame.from_dict(data)

        assert save.save_id == "slot_2"
        assert save.save_name == "Another Save"
        assert save.timestamp == datetime(2026, 2, 20, 14, 45, 30)
        assert save.player_id == "player_02"
        assert save.player_name == "Warrior"
        assert save.current_room_id == "room_05"
        assert save.health == 50
        assert save.max_health == 120
        assert save.inventory == {"item_shield": 1}

    def test_roundtrip(self) -> None:
        original = SaveGame(
            save_id="slot_3",
            save_name="Roundtrip Test",
            timestamp=datetime(2026, 3, 10, 8, 15, 45),
            player_id="player_03",
            player_name="Mage",
            current_room_id="room_10",
            health=100,
            max_health=100,
            inventory={},
        )

        data = original.to_dict()
        restored = SaveGame.from_dict(data)

        assert restored.save_id == original.save_id
        assert restored.save_name == original.save_name
        assert restored.timestamp == original.timestamp
        assert restored.player_id == original.player_id
        assert restored.player_name == original.player_name
        assert restored.current_room_id == original.current_room_id
        assert restored.health == original.health
        assert restored.max_health == original.max_health
        assert restored.inventory == original.inventory
