"""End-to-end integration test for inventory: pick up, use, and verify effects."""

from pathlib import Path

from application.use_cases.move_to_room import MoveToRoomUseCase
from application.use_cases.pick_up_item import PickUpItemUseCase
from application.use_cases.use_item import UseItemUseCase
from domain.entities.player import Player
from domain.events.item_used import ItemUsed
from infrastructure.content_loader.json_content_repository import JsonContentRepository
from infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus

DATA_PATH = Path(__file__).parent.parent.parent / "data"


class TestInventoryEndToEnd:
    def test_pick_up_and_use_health_potion(self) -> None:
        content_repo = JsonContentRepository(DATA_PATH)
        event_bus = InMemoryEventBus()

        published_events: list = []
        event_bus.subscribe(ItemUsed, lambda e: published_events.append(e))

        move_uc = MoveToRoomUseCase(content_repo, event_bus)
        pick_up_uc = PickUpItemUseCase(content_repo, event_bus)
        use_item_uc = UseItemUseCase(content_repo, event_bus)

        player = Player(id="p1", name="Hero", current_room_id="room_01", health=70)

        move_result = move_uc.execute(player, "north")
        assert move_result.success is True
        assert player.current_room_id == "room_02"

        pick_result = pick_up_uc.execute(player, "item_health_potion")
        assert pick_result.success is True
        assert player.inventory.has_item("item_health_potion")

        use_result = use_item_uc.execute(player, "item_health_potion")
        assert use_result.success is True
        assert player.health == 100
        assert not player.inventory.has_item("item_health_potion")
        assert len(published_events) == 1
        assert isinstance(published_events[0], ItemUsed)

    def test_use_item_not_in_inventory(self) -> None:
        content_repo = JsonContentRepository(DATA_PATH)
        event_bus = InMemoryEventBus()
        use_item_uc = UseItemUseCase(content_repo, event_bus)

        player = Player(id="p1", name="Hero", current_room_id="room_01")

        result = use_item_uc.execute(player, "item_health_potion")
        assert result.success is False

    def test_use_non_usable_item(self) -> None:
        content_repo = JsonContentRepository(DATA_PATH)
        event_bus = InMemoryEventBus()
        pick_up_uc = PickUpItemUseCase(content_repo, event_bus)
        use_item_uc = UseItemUseCase(content_repo, event_bus)

        player = Player(id="p1", name="Hero", current_room_id="room_03")

        pick_result = pick_up_uc.execute(player, "item_rusty_sword")
        assert pick_result.success is True

        use_result = use_item_uc.execute(player, "item_rusty_sword")
        assert use_result.success is False
        assert player.inventory.has_item("item_rusty_sword")
