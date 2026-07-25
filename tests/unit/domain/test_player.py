import pytest

from domain.entities.inventory import Inventory
from domain.entities.player import Player


@pytest.fixture
def player() -> Player:
    return Player(
        id="player_01",
        name="Hero",
        current_room_id="room_01",
    )


class TestPlayer:
    def test_create_player(self, player: Player) -> None:
        assert player.id == "player_01"
        assert player.name == "Hero"
        assert player.current_room_id == "room_01"
        assert player.health == 100
        assert player.max_health == 100

    def test_default_inventory(self, player: Player) -> None:
        assert isinstance(player.inventory, Inventory)
        assert player.inventory.total_quantity == 0

    def test_move_to(self, player: Player) -> None:
        player.move_to("room_02")
        assert player.current_room_id == "room_02"

    def test_move_to_multiple_times(self, player: Player) -> None:
        player.move_to("room_02")
        player.move_to("room_03")
        assert player.current_room_id == "room_03"

    def test_custom_health(self) -> None:
        player = Player(
            id="player_02",
            name="Wounded Hero",
            current_room_id="room_01",
            health=50,
            max_health=100,
        )
        assert player.health == 50
