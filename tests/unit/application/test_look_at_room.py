import pytest

from application.use_cases.look_at_room import LookAtRoomUseCase
from domain.entities.map import GameMap
from domain.entities.player import Player
from domain.entities.room import Room
from tests.fixtures.fake_content_repository import FakeContentRepository


@pytest.fixture
def game_map() -> GameMap:
    game_map = GameMap()
    game_map.add_room(
        Room(
            id="room_01",
            name="Entrance",
            description="The entrance hall.",
            exits={"north": "room_02"},
            item_ids=["sword_01"],
            npc_ids=["guard_01"],
        )
    )
    return game_map


@pytest.fixture
def player() -> Player:
    return Player(id="player_01", name="Hero", current_room_id="room_01")


@pytest.fixture
def look_use_case(game_map: GameMap) -> LookAtRoomUseCase:
    content_repo = FakeContentRepository(game_map)
    return LookAtRoomUseCase(content_repo)


class TestLookAtRoomUseCase:
    def test_look_at_room(self, look_use_case: LookAtRoomUseCase, player: Player) -> None:
        result = look_use_case.execute(player)

        assert result.success is True
        assert result.data is not None
        assert result.data["room_id"] == "room_01"
        assert result.data["name"] == "Entrance"
        assert result.data["description"] == "The entrance hall."
        assert result.data["exits"] == ["north"]
        assert result.data["item_ids"] == ["sword_01"]
        assert result.data["npc_ids"] == ["guard_01"]

    def test_look_returns_description_in_message(self, look_use_case: LookAtRoomUseCase, player: Player) -> None:
        result = look_use_case.execute(player)
        assert result.message == "The entrance hall."
