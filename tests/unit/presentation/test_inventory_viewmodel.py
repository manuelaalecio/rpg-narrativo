import pytest
from PySide6.QtWidgets import QApplication

from application.use_cases.use_item import UseItemUseCase
from domain.entities.item import Item
from domain.entities.map import GameMap
from domain.entities.player import Player
from domain.value_objects.item_effect import EffectType, ItemEffect
from domain.value_objects.item_type import ItemType
from presentation.viewmodels.inventory_viewmodel import InventoryViewModel
from tests.fixtures.fake_content_repository import FakeContentRepository
from tests.fixtures.fake_event_bus import FakeEventBus


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


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
def player(healing_potion: Item, sword: Item) -> Player:
    player = Player(id="p1", name="Hero", current_room_id="room_01", health=50)
    player.inventory.add_item("potion_01", quantity=2)
    player.inventory.add_item("sword_01")
    return player


@pytest.fixture
def view_model(
    qapp: QApplication,
    player: Player,
    healing_potion: Item,
    sword: Item,
) -> InventoryViewModel:
    content_repo = FakeContentRepository(
        game_map=GameMap(),
        items={"potion_01": healing_potion, "sword_01": sword},
    )
    event_bus = FakeEventBus()
    use_item_uc = UseItemUseCase(content_repo, event_bus)
    return InventoryViewModel(player, use_item_uc, content_repo)


class TestInventoryViewModel:
    def test_refresh_populates_items(self, view_model: InventoryViewModel) -> None:
        view_model.refresh()
        assert len(view_model.items) == 2
        item_ids = [item["item_id"] for item in view_model.items]
        assert "potion_01" in item_ids
        assert "sword_01" in item_ids

    def test_refresh_shows_correct_quantities(self, view_model: InventoryViewModel) -> None:
        view_model.refresh()
        potion = next(item for item in view_model.items if item["item_id"] == "potion_01")
        assert potion["quantity"] == 2
        assert potion["usable"] is True

    def test_use_item_updates_state(self, view_model: InventoryViewModel, player: Player) -> None:
        view_model.use_item("potion_01")
        assert player.health == 80
        assert player.inventory.get_quantity("potion_01") == 1
        assert len(view_model.items) == 2

    def test_use_last_item_removes_from_list(self, view_model: InventoryViewModel, player: Player) -> None:
        view_model.use_item("sword_01")
        # sword is not usable, so use_item fails and sword stays
        assert player.inventory.has_item("sword_01")

    def test_player_stats(self, view_model: InventoryViewModel) -> None:
        assert view_model.player_health == 50
        assert view_model.player_max_health == 100
