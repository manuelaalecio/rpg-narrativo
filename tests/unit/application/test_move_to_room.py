import pytest

from application.use_cases.move_to_room import MoveToRoomUseCase
from domain.entities.map import GameMap
from domain.entities.player import Player
from domain.entities.room import Room
from domain.events.player_moved import PlayerMoved
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
            exits={"north": "room_02", "east": "room_03"},
        )
    )
    game_map.add_room(
        Room(
            id="room_02",
            name="Garden",
            description="A peaceful garden.",
            exits={"south": "room_01"},
        )
    )
    game_map.add_room(
        Room(
            id="room_03",
            name="Library",
            description="A dusty library.",
            exits={"west": "room_01"},
        )
    )
    return game_map


@pytest.fixture
def player() -> Player:
    return Player(id="player_01", name="Hero", current_room_id="room_01")


@pytest.fixture
def event_bus() -> FakeEventBus:
    return FakeEventBus()


@pytest.fixture
def move_use_case(game_map: GameMap, event_bus: FakeEventBus) -> MoveToRoomUseCase:
    content_repo = FakeContentRepository(game_map)
    return MoveToRoomUseCase(content_repo, event_bus)


class TestMoveToRoomUseCase:
    def test_move_success(self, move_use_case: MoveToRoomUseCase, player: Player, event_bus: FakeEventBus) -> None:
        result = move_use_case.execute(player, "north")

        assert result.success is True
        assert player.current_room_id == "room_02"
        assert result.data == {"room_id": "room_02"}
        event_bus.assert_event_published(PlayerMoved)

    def test_move_invalid_direction(self, move_use_case: MoveToRoomUseCase, player: Player) -> None:
        result = move_use_case.execute(player, "west")

        assert result.success is False
        assert player.current_room_id == "room_01"
        assert "no exit" in result.message.lower()

    def test_move_multiple_times(
        self, move_use_case: MoveToRoomUseCase, player: Player, event_bus: FakeEventBus
    ) -> None:
        move_use_case.execute(player, "north")
        assert player.current_room_id == "room_02"

        move_use_case.execute(player, "south")
        assert player.current_room_id == "room_01"

        assert len(event_bus.published_events) == 2
