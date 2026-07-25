import pytest

from domain.entities.map import GameMap
from domain.entities.room import Room
from domain.exceptions import RoomNotFoundError


@pytest.fixture
def game_map() -> GameMap:
    game_map = GameMap()
    game_map.add_room(Room(id="room_01", name="Hall", description="A hall."))
    game_map.add_room(Room(id="room_02", name="Garden", description="A garden."))
    return game_map


class TestGameMap:
    def test_add_and_get_room(self, game_map: GameMap) -> None:
        room = game_map.get_room("room_01")
        assert room.id == "room_01"
        assert room.name == "Hall"

    def test_get_room_not_found(self, game_map: GameMap) -> None:
        with pytest.raises(RoomNotFoundError):
            game_map.get_room("nonexistent")

    def test_has_room(self, game_map: GameMap) -> None:
        assert game_map.has_room("room_01")
        assert not game_map.has_room("nonexistent")

    def test_room_ids(self, game_map: GameMap) -> None:
        assert set(game_map.room_ids) == {"room_01", "room_02"}

    def test_empty_map(self) -> None:
        game_map = GameMap()
        assert game_map.room_ids == []
        assert not game_map.has_room("any")
