"""End-to-end integration test for save/load flow."""

from pathlib import Path

import pytest

from application.use_cases.load_game import LoadGameUseCase
from application.use_cases.move_to_room import MoveToRoomUseCase
from application.use_cases.pick_up_item import PickUpItemUseCase
from application.use_cases.save_game import SaveGameUseCase
from application.use_cases.use_item import UseItemUseCase
from domain.entities.player import Player
from infrastructure.content_loader.json_content_repository import JsonContentRepository
from infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus
from infrastructure.persistence.in_memory_quest_repository import InMemoryQuestRepository
from infrastructure.persistence.json_save_game_repository import JsonSaveGameRepository


@pytest.fixture
def temp_save_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for save files."""
    save_dir = tmp_path / "saves"
    save_dir.mkdir()
    return save_dir


class TestSaveLoadEndToEnd:
    def test_play_save_restart_load(self, temp_save_dir: Path) -> None:
        """Test complete flow: play, save, restart, load, verify state."""
        data_path = Path(__file__).parent.parent.parent / "data"
        content_repo = JsonContentRepository(data_path)
        save_repo = JsonSaveGameRepository(temp_save_dir)
        quest_repo = InMemoryQuestRepository()
        event_bus = InMemoryEventBus()

        move_uc = MoveToRoomUseCase(content_repo, event_bus)
        pick_up_uc = PickUpItemUseCase(content_repo, event_bus)
        use_item_uc = UseItemUseCase(content_repo, event_bus)
        save_uc = SaveGameUseCase(save_repo, quest_repo, event_bus)
        load_uc = LoadGameUseCase(save_repo, quest_repo, event_bus)

        # Start playing
        player = Player(id="player_01", name="Hero", current_room_id="room_01", health=70)

        # Move to room_02
        move_result = move_uc.execute(player, "north")
        assert move_result.success is True
        assert player.current_room_id == "room_02"

        # Pick up health potion
        pick_result = pick_up_uc.execute(player, "item_health_potion")
        assert pick_result.success is True
        assert player.inventory.has_item("item_health_potion")

        # Use the potion
        use_result = use_item_uc.execute(player, "item_health_potion")
        assert use_result.success is True
        assert player.health == 100  # 70 + 30 = 100
        assert not player.inventory.has_item("item_health_potion")

        # Save the game
        save_result = save_uc.execute(player, "autosave", "Mid-Adventure Save")
        assert save_result.success is True

        # Simulate restart: create a new player with default state
        restarted_player = Player(id="player_01", name="Hero", current_room_id="room_01", health=100)
        assert restarted_player.current_room_id == "room_01"
        assert restarted_player.health == 100
        assert restarted_player.inventory.total_quantity == 0

        # Load the save
        load_result = load_uc.execute("autosave")
        assert load_result.success is True
        assert load_result.data is not None

        loaded_player = load_result.data["player"]

        # Verify state was restored correctly
        assert loaded_player.id == "player_01"
        assert loaded_player.name == "Hero"
        assert loaded_player.current_room_id == "room_02"  # Was in room_02 when saved
        assert loaded_player.health == 100  # Was healed to 100 when saved
        assert loaded_player.max_health == 100
        assert loaded_player.inventory.total_quantity == 0  # Potion was used

    def test_save_load_with_inventory(self, temp_save_dir: Path) -> None:
        """Test save/load with items in inventory."""
        data_path = Path(__file__).parent.parent.parent / "data"
        content_repo = JsonContentRepository(data_path)
        save_repo = JsonSaveGameRepository(temp_save_dir)
        quest_repo = InMemoryQuestRepository()
        event_bus = InMemoryEventBus()

        pick_up_uc = PickUpItemUseCase(content_repo, event_bus)
        save_uc = SaveGameUseCase(save_repo, quest_repo, event_bus)
        load_uc = LoadGameUseCase(save_repo, quest_repo, event_bus)

        # Start in room_01 and pick up the key
        player = Player(id="player_01", name="Hero", current_room_id="room_01")
        pick_result = pick_up_uc.execute(player, "item_old_key")
        assert pick_result.success is True
        assert player.inventory.has_item("item_old_key")

        # Save
        save_result = save_uc.execute(player, "slot_1", "With Key")
        assert save_result.success is True

        # Load
        load_result = load_uc.execute("slot_1")
        assert load_result.success is True

        loaded_player = load_result.data["player"]
        assert loaded_player.inventory.has_item("item_old_key")
        assert loaded_player.inventory.get_quantity("item_old_key") == 1

    def test_multiple_saves(self, temp_save_dir: Path) -> None:
        """Test saving to multiple slots."""
        data_path = Path(__file__).parent.parent.parent / "data"
        content_repo = JsonContentRepository(data_path)
        save_repo = JsonSaveGameRepository(temp_save_dir)
        quest_repo = InMemoryQuestRepository()
        event_bus = InMemoryEventBus()

        move_uc = MoveToRoomUseCase(content_repo, event_bus)
        save_uc = SaveGameUseCase(save_repo, quest_repo, event_bus)
        load_uc = LoadGameUseCase(save_repo, quest_repo, event_bus)

        player = Player(id="player_01", name="Hero", current_room_id="room_01")

        # Save at room_01
        save_uc.execute(player, "slot_1", "Start")

        # Move to room_02 and save
        move_uc.execute(player, "north")
        save_uc.execute(player, "slot_2", "Tavern")

        # Move to room_03 and save
        move_uc.execute(player, "south")  # Back to room_01
        move_uc.execute(player, "east")  # To room_03
        save_uc.execute(player, "slot_3", "Market")

        # Verify all saves exist
        saves = save_repo.list_saves()
        assert len(saves) == 3

        # Load each and verify
        result1 = load_uc.execute("slot_1")
        assert result1.data["player"].current_room_id == "room_01"

        result2 = load_uc.execute("slot_2")
        assert result2.data["player"].current_room_id == "room_02"

        result3 = load_uc.execute("slot_3")
        assert result3.data["player"].current_room_id == "room_03"
