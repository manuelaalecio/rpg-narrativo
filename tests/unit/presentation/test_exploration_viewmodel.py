import pytest
from PySide6.QtWidgets import QApplication

from application.use_cases.look_at_room import LookAtRoomUseCase
from application.use_cases.move_to_room import MoveToRoomUseCase
from application.use_cases.pick_up_item import PickUpItemUseCase
from domain.entities.item import Item
from domain.entities.map import GameMap
from domain.entities.player import Player
from domain.entities.room import Room
from domain.value_objects.item_type import ItemType
from presentation.viewmodels.exploration_viewmodel import ExplorationViewModel
from tests.fixtures.fake_content_repository import FakeContentRepository
from tests.fixtures.fake_event_bus import FakeEventBus


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def game_map() -> GameMap:
    game_map = GameMap()
    game_map.add_room(
        Room(
            id="room_01",
            name="Test Hall",
            description="A test hall.",
            exits={"north": "room_02"},
            item_ids=["sword_01"],
        )
    )
    game_map.add_room(
        Room(
            id="room_02",
            name="Test Garden",
            description="A test garden.",
            exits={"south": "room_01"},
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
    }


@pytest.fixture
def player() -> Player:
    return Player(id="p1", name="Hero", current_room_id="room_01")


@pytest.fixture
def view_model(
    qapp: QApplication,
    game_map: GameMap,
    items: dict[str, Item],
    player: Player,
) -> ExplorationViewModel:
    content_repo = FakeContentRepository(game_map, items)
    event_bus = FakeEventBus()
    move_uc = MoveToRoomUseCase(content_repo, event_bus)
    look_uc = LookAtRoomUseCase(content_repo)
    pick_up_uc = PickUpItemUseCase(content_repo, event_bus)
    return ExplorationViewModel(player, move_uc, look_uc, pick_up_uc)


class TestExplorationViewModel:
    def test_look_updates_room_state(self, view_model: ExplorationViewModel) -> None:
        view_model.look()

        assert view_model.room_name == "Test Hall"
        assert view_model.room_description == "A test hall."
        assert view_model.available_exits == ["north"]
        assert view_model.room_items == ["sword_01"]

    def test_move_success_updates_room(self, view_model: ExplorationViewModel, player: Player) -> None:
        view_model.move("north")

        assert player.current_room_id == "room_02"
        assert view_model.room_name == "Test Garden"

    def test_move_failure_keeps_room(self, view_model: ExplorationViewModel, player: Player) -> None:
        view_model.look()
        view_model.move("west")

        assert player.current_room_id == "room_01"
        assert view_model.room_name == "Test Hall"

    def test_pick_up_item_removes_from_room(self, view_model: ExplorationViewModel, player: Player) -> None:
        view_model.pick_up_item("sword_01")

        assert player.inventory.has_item("sword_01")
        assert "sword_01" not in view_model.room_items

    def test_pick_up_nonexistent_item_fails(self, view_model: ExplorationViewModel, player: Player) -> None:
        view_model.look()
        view_model.pick_up_item("nonexistent")

        assert not player.inventory.has_item("nonexistent")
        assert "sword_01" in view_model.room_items
