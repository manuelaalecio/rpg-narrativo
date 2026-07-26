"""Unit tests for LoadGameUseCase."""

from datetime import datetime

from application.use_cases.load_game import LoadGameUseCase
from domain.entities.save_game import SaveGame
from domain.events.game_loaded import GameLoaded
from tests.fixtures.fake_event_bus import FakeEventBus
from tests.fixtures.fake_save_game_repository import FakeSaveGameRepository


class TestLoadGameUseCase:
    def test_load_success(self) -> None:
        repo = FakeSaveGameRepository()
        event_bus = FakeEventBus()
        use_case = LoadGameUseCase(repo, event_bus)

        # Create a save
        save = SaveGame(
            save_id="slot_1",
            save_name="Test Save",
            timestamp=datetime(2026, 1, 15, 10, 30, 0),
            player_id="player_01",
            player_name="Hero",
            current_room_id="room_05",
            health=80,
            max_health=100,
            inventory={"item_sword": 1, "item_potion": 3},
        )
        repo.save(save, "slot_1")

        result = use_case.execute("slot_1")

        assert result.success is True
        assert "loaded" in result.message.lower()
        assert result.data is not None

        player = result.data["player"]
        assert player.id == "player_01"
        assert player.name == "Hero"
        assert player.current_room_id == "room_05"
        assert player.health == 80
        assert player.max_health == 100
        assert player.inventory.has_item("item_sword")
        assert player.inventory.get_quantity("item_sword") == 1
        assert player.inventory.has_item("item_potion")
        assert player.inventory.get_quantity("item_potion") == 3

        # Verify event was published
        event_bus.assert_event_published(GameLoaded)

    def test_load_nonexistent_slot(self) -> None:
        repo = FakeSaveGameRepository()
        event_bus = FakeEventBus()
        use_case = LoadGameUseCase(repo, event_bus)

        result = use_case.execute("nonexistent")

        assert result.success is False
        assert "not found" in result.message.lower()

    def test_load_corrupted_save(self) -> None:
        repo = FakeSaveGameRepository()
        event_bus = FakeEventBus()
        use_case = LoadGameUseCase(repo, event_bus)

        # Create and mark as corrupted
        save = SaveGame(
            save_id="slot_1",
            save_name="Corrupted",
            timestamp=datetime.now(),
            player_id="player_01",
            player_name="Hero",
            current_room_id="room_01",
            health=100,
            max_health=100,
            inventory={},
        )
        repo.save(save, "slot_1")
        repo.mark_corrupted("slot_1")

        result = use_case.execute("slot_1")

        assert result.success is False
        assert "corrupted" in result.message.lower()

    def test_load_empty_inventory(self) -> None:
        repo = FakeSaveGameRepository()
        event_bus = FakeEventBus()
        use_case = LoadGameUseCase(repo, event_bus)

        save = SaveGame(
            save_id="slot_2",
            save_name="Empty",
            timestamp=datetime.now(),
            player_id="player_01",
            player_name="Hero",
            current_room_id="room_01",
            health=100,
            max_health=100,
            inventory={},
        )
        repo.save(save, "slot_2")

        result = use_case.execute("slot_2")

        assert result.success is True
        player = result.data["player"]
        assert player.inventory.total_quantity == 0
