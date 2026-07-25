"""End-to-end integration test: real JsonContentRepository + InMemoryEventBus + Use Cases."""

from pathlib import Path

from application.use_cases.look_at_room import LookAtRoomUseCase
from application.use_cases.move_to_room import MoveToRoomUseCase
from application.use_cases.pick_up_item import PickUpItemUseCase
from domain.entities.player import Player
from domain.events.item_picked_up import ItemPickedUp
from domain.events.player_moved import PlayerMoved
from infrastructure.content_loader.json_content_repository import JsonContentRepository
from infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus

DATA_PATH = Path(__file__).parent.parent.parent / "data"


class TestEndToEnd:
    def test_explore_and_pick_up_item(self) -> None:
        content_repo = JsonContentRepository(DATA_PATH)
        event_bus = InMemoryEventBus()

        published_events: list = []
        event_bus.subscribe(PlayerMoved, lambda e: published_events.append(e))
        event_bus.subscribe(ItemPickedUp, lambda e: published_events.append(e))

        move_uc = MoveToRoomUseCase(content_repo, event_bus)
        look_uc = LookAtRoomUseCase(content_repo)
        pick_up_uc = PickUpItemUseCase(content_repo, event_bus)

        player = Player(id="p1", name="Hero", current_room_id="room_01")

        look_result = look_uc.execute(player)
        assert look_result.success is True
        assert look_result.data is not None
        assert look_result.data["name"] == "Town Square"
        assert "north" in look_result.data["exits"]
        assert "item_old_key" in look_result.data["item_ids"]

        pick_result = pick_up_uc.execute(player, "item_old_key")
        assert pick_result.success is True
        assert player.inventory.has_item("item_old_key")

        room_after_pick = content_repo.get_map().get_room("room_01")
        assert "item_old_key" not in room_after_pick.item_ids

        move_result = move_uc.execute(player, "north")
        assert move_result.success is True
        assert player.current_room_id == "room_02"
        assert move_result.data == {"room_id": "room_02"}

        look_result_2 = look_uc.execute(player)
        assert look_result_2.data is not None
        assert look_result_2.data["name"] == "Old Tavern"

        move_back = move_uc.execute(player, "south")
        assert move_back.success is True
        assert player.current_room_id == "room_01"

        move_invalid = move_uc.execute(player, "west")
        assert move_invalid.success is False

        assert len(published_events) == 3
        assert isinstance(published_events[0], ItemPickedUp)
        assert isinstance(published_events[1], PlayerMoved)
        assert isinstance(published_events[2], PlayerMoved)
        assert published_events[1].from_room_id == "room_01"
        assert published_events[1].to_room_id == "room_02"
        assert published_events[2].from_room_id == "room_02"
        assert published_events[2].to_room_id == "room_01"

    def test_move_to_market_alley_and_pick_up_sword(self) -> None:
        content_repo = JsonContentRepository(DATA_PATH)
        event_bus = InMemoryEventBus()

        move_uc = MoveToRoomUseCase(content_repo, event_bus)
        pick_up_uc = PickUpItemUseCase(content_repo, event_bus)

        player = Player(id="p1", name="Hero", current_room_id="room_01")

        move_result = move_uc.execute(player, "east")
        assert move_result.success is True
        assert player.current_room_id == "room_03"

        pick_result = pick_up_uc.execute(player, "item_rusty_sword")
        assert pick_result.success is True
        assert player.inventory.has_item("item_rusty_sword")
