"""Unit tests for SaveGameUseCase."""

from datetime import datetime

from application.use_cases.save_game import SaveGameUseCase
from domain.entities.inventory import Inventory
from domain.entities.player import Player
from domain.events.game_saved import GameSaved
from tests.fixtures.fake_event_bus import FakeEventBus
from tests.fixtures.fake_save_game_repository import FakeSaveGameRepository


class TestSaveGameUseCase:
    def test_save_success(self) -> None:
        repo = FakeSaveGameRepository()
        event_bus = FakeEventBus()
        use_case = SaveGameUseCase(repo, event_bus)

        inventory = Inventory()
        inventory.add_item("item_sword", 1)
        inventory.add_item("item_potion", 2)

        player = Player(
            id="player_01",
            name="Hero",
            current_room_id="room_03",
            inventory=inventory,
            health=75,
            max_health=100,
        )

        result = use_case.execute(player, "slot_1", "My Save")

        assert result.success is True
        assert "saved" in result.message.lower()
        assert result.data is not None
        assert result.data["slot"] == "slot_1"
        assert result.data["save_name"] == "My Save"

        # Verify save was persisted
        saved = repo.load("slot_1")
        assert saved.save_id == "slot_1"
        assert saved.save_name == "My Save"
        assert saved.player_id == "player_01"
        assert saved.player_name == "Hero"
        assert saved.current_room_id == "room_03"
        assert saved.health == 75
        assert saved.max_health == 100
        assert saved.inventory == {"item_sword": 1, "item_potion": 2}

        # Verify event was published
        event_bus.assert_event_published(GameSaved)

    def test_save_with_auto_name(self) -> None:
        repo = FakeSaveGameRepository()
        event_bus = FakeEventBus()
        use_case = SaveGameUseCase(repo, event_bus)

        player = Player(
            id="player_01",
            name="Hero",
            current_room_id="room_01",
        )

        result = use_case.execute(player, "slot_2")

        assert result.success is True
        assert result.data is not None
        assert "Hero" in result.data["save_name"]

    def test_save_empty_inventory(self) -> None:
        repo = FakeSaveGameRepository()
        event_bus = FakeEventBus()
        use_case = SaveGameUseCase(repo, event_bus)

        player = Player(
            id="player_01",
            name="Hero",
            current_room_id="room_01",
        )

        result = use_case.execute(player, "slot_3", "Empty Save")

        assert result.success is True
        saved = repo.load("slot_3")
        assert saved.inventory == {}
