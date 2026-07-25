import pytest

from domain.entities.room import Room


@pytest.fixture
def sample_room() -> Room:
    return Room(
        id="room_01",
        name="Entrance Hall",
        description="A dimly lit hall with stone walls.",
        exits={"north": "room_02", "east": "room_03"},
        item_ids=["item_key_01"],
        npc_ids=["npc_guard_01"],
    )


class TestRoom:
    def test_create_room(self, sample_room: Room) -> None:
        assert sample_room.id == "room_01"
        assert sample_room.name == "Entrance Hall"
        assert sample_room.description == "A dimly lit hall with stone walls."

    def test_get_exit_existing_direction(self, sample_room: Room) -> None:
        assert sample_room.get_exit("north") == "room_02"
        assert sample_room.get_exit("east") == "room_03"

    def test_get_exit_nonexistent_direction(self, sample_room: Room) -> None:
        assert sample_room.get_exit("south") is None
        assert sample_room.get_exit("west") is None

    def test_add_item(self, sample_room: Room) -> None:
        sample_room.add_item("item_potion_01")
        assert "item_potion_01" in sample_room.item_ids

    def test_remove_item_existing(self, sample_room: Room) -> None:
        sample_room.remove_item("item_key_01")
        assert "item_key_01" not in sample_room.item_ids

    def test_remove_item_nonexistent(self, sample_room: Room) -> None:
        with pytest.raises(ValueError):
            sample_room.remove_item("nonexistent_item")

    def test_default_empty_collections(self) -> None:
        room = Room(id="empty", name="Empty", description="Nothing here.")
        assert room.exits == {}
        assert room.item_ids == []
        assert room.npc_ids == []
