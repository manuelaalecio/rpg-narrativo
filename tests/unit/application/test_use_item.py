import pytest

from application.use_cases.use_item import UseItemUseCase
from domain.entities.item import Item
from domain.entities.map import GameMap
from domain.entities.player import Player
from domain.events.item_used import ItemUsed
from domain.value_objects.item_effect import EffectType, ItemEffect
from domain.value_objects.item_type import ItemType
from tests.fixtures.fake_content_repository import FakeContentRepository
from tests.fixtures.fake_event_bus import FakeEventBus


@pytest.fixture
def healing_potion() -> Item:
    return Item(
        id="potion_01",
        name="Health Potion",
        description="Restores health.",
        item_type=ItemType.CONSUMABLE,
        usable=True,
        stackable=True,
        effect=ItemEffect(effect_type=EffectType.HEAL, value=30),
    )


@pytest.fixture
def sword() -> Item:
    return Item(
        id="sword_01",
        name="Iron Sword",
        description="A sturdy sword.",
        item_type=ItemType.WEAPON,
        usable=False,
    )


@pytest.fixture
def event_bus() -> FakeEventBus:
    return FakeEventBus()


@pytest.fixture
def use_case(healing_potion: Item, sword: Item, event_bus: FakeEventBus) -> UseItemUseCase:
    content_repo = FakeContentRepository(
        game_map=GameMap(),
        items={"potion_01": healing_potion, "sword_01": sword},
    )
    return UseItemUseCase(content_repo, event_bus)


class TestUseItemUseCase:
    def test_use_healing_potion(self, use_case: UseItemUseCase, event_bus: FakeEventBus) -> None:
        player = Player(id="p1", name="Hero", current_room_id="room_01", health=50)
        player.inventory.add_item("potion_01")

        result = use_case.execute(player, "potion_01")

        assert result.success is True
        assert player.health == 80
        assert not player.inventory.has_item("potion_01")
        event_bus.assert_event_published(ItemUsed)

    def test_use_item_not_in_inventory(self, use_case: UseItemUseCase) -> None:
        player = Player(id="p1", name="Hero", current_room_id="room_01")

        result = use_case.execute(player, "potion_01")

        assert result.success is False
        assert "don't have" in result.message.lower()

    def test_use_non_usable_item(self, use_case: UseItemUseCase) -> None:
        player = Player(id="p1", name="Hero", current_room_id="room_01")
        player.inventory.add_item("sword_01")

        result = use_case.execute(player, "sword_01")

        assert result.success is False
        assert "can't use" in result.message.lower()
        assert player.inventory.has_item("sword_01")

    def test_use_item_not_in_content(self, use_case: UseItemUseCase) -> None:
        player = Player(id="p1", name="Hero", current_room_id="room_01")
        player.inventory.add_item("unknown_item")

        result = use_case.execute(player, "unknown_item")

        assert result.success is False

    def test_use_multiple_stackable_items(self, use_case: UseItemUseCase, event_bus: FakeEventBus) -> None:
        player = Player(id="p1", name="Hero", current_room_id="room_01", health=50)
        player.inventory.add_item("potion_01", quantity=3)

        result = use_case.execute(player, "potion_01")

        assert result.success is True
        assert player.health == 80
        assert player.inventory.get_quantity("potion_01") == 2

    def test_heal_capped_at_max(self, use_case: UseItemUseCase) -> None:
        player = Player(id="p1", name="Hero", current_room_id="room_01", health=95)
        player.inventory.add_item("potion_01")

        result = use_case.execute(player, "potion_01")

        assert result.success is True
        assert player.health == 100
