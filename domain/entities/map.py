from dataclasses import dataclass, field

from domain.entities.room import Room
from domain.exceptions import RoomNotFoundError


@dataclass
class GameMap:
    """Collection of rooms indexed by id, representing the game world."""

    _rooms: dict[str, Room] = field(default_factory=dict)

    def add_room(self, room: Room) -> None:
        """Register a room in the map."""
        self._rooms[room.id] = room

    def get_room(self, room_id: str) -> Room:
        """Return the room with the given id. Raises RoomNotFoundError if missing."""
        if room_id not in self._rooms:
            raise RoomNotFoundError(room_id)
        return self._rooms[room_id]

    def has_room(self, room_id: str) -> bool:
        """Check whether a room with the given id exists in the map."""
        return room_id in self._rooms

    @property
    def room_ids(self) -> list[str]:
        """Return all registered room ids."""
        return list(self._rooms.keys())
