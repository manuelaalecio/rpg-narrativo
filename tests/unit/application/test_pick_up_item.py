import pytest

from application.use_cases.pick_up_item import PickUpItemUseCase
from domain.entities.item import Item
from domain.entities.map import GameMap
from domain.entities.player import Player
from domain.entities.room import Room
from domain.events.item_picked_up import ItemPickedUp
from domain.value_objects.item_type import ItemType
from tests.fixtures.fake_content_repository import FakeContentRepository
from tests.fixtures.fake_event_bus import FakeEventBus


@pytest.fixture
def game_map() -> GameMap:
    game_map = GameMap()
    game_map.add_room(
        Room(
            id="room_01",
            name="Entrance",
            description="The entrance hall.",
            item_ids=["sword_01", "potion_01"],
        )
    )
    return game_map


@pytest.fixture
def items() -> dict[str, Item]:
    return {
        "sword_01": Item(
            id="sword_01",
            name="Iron Sword",
            description="A sturdy sword.",
            item_type=ItemType.WEAPON,
        ),
        "potion_01": Item(
            id="potion_01",
            name="Health Potion",
            description="Restores health.",
            item_type=ItemType.CONSUMABLE,
        ),
    }


@pytest.fixture
def player() -> Player:
    return Player(id="player_01", name="Hero", current_room_id="room_01")


@pytest.fixture
def event_bus() -> FakeEventBus:
    return FakeEventBus()


@pytest.fixture
def pick_up_use_case(game_map: GameMap, items: dict[str, Item], event_bus: FakeEventBus) -> PickUpItemUseCase:
    content_repo = FakeContentRepository(game_map, items)
    return PickUpItemUseCase(content_repo, event_bus)


class TestPickUpItemUseCase:
    def test_pick_up_success(
        self,
        pick_up_use_case: PickUpItemUseCase,
        player: Player,
        game_map: GameMap,
        event_bus: FakeEventBus,
    ) -> None:
        result = pick_up_use_case.execute(player, "sword_01")

        assert result.success is True
        assert player.inventory.has_item("sword_01")
        room = game_map.get_room("room_01")
        assert "sword_01" not in room.item_ids
        event_bus.assert_event_published(ItemPickedUp)

    def test_pick_up_item_not_in_room(self, pick_up_use_case: PickUpItemUseCase, player: Player) -> None:
        result = pick_up_use_case.execute(player, "nonexistent_item")

        assert result.success is False
        assert not player.inventory.has_item("nonexistent_item")
        assert "no" in result.message.lower()

    def test_pick_up_multiple_items(
        self,
        pick_up_use_case: PickUpItemUseCase,
        player: Player,
        game_map: GameMap,
    ) -> None:
        pick_up_use_case.execute(player, "sword_01")
        pick_up_use_case.execute(player, "potion_01")

        assert player.inventory.has_item("sword_01")
        assert player.inventory.has_item("potion_01")
        room = game_map.get_room("room_01")
        assert len(room.item_ids) == 0
