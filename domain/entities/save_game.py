"""Save game entity - serializable snapshot of player state."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SaveGame:
    """Snapshot of player state for saving/loading game progress.

    Contains only player state, not game content (rooms, items, etc.).
    Game content is loaded separately from data/ via ContentRepositoryPort.
    """

    save_id: str
    save_name: str
    timestamp: datetime
    player_id: str
    player_name: str
    current_room_id: str
    health: int
    max_health: int
    inventory: dict[str, int]  # item_id -> quantity
    quest_statuses: dict[str, str] = field(default_factory=dict)  # quest_id -> status value

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization.

        This is not I/O - just data transformation.
        Actual file writing is infrastructure's responsibility.
        """
        return {
            "save_id": self.save_id,
            "save_name": self.save_name,
            "timestamp": self.timestamp.isoformat(),
            "player_id": self.player_id,
            "player_name": self.player_name,
            "current_room_id": self.current_room_id,
            "health": self.health,
            "max_health": self.max_health,
            "inventory": self.inventory,
            "quest_statuses": self.quest_statuses,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SaveGame":
        """Reconstruct SaveGame from dictionary.

        This is not I/O - just data transformation.
        Actual file reading is infrastructure's responsibility.
        """
        return cls(
            save_id=data["save_id"],
            save_name=data["save_name"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            player_id=data["player_id"],
            player_name=data["player_name"],
            current_room_id=data["current_room_id"],
            health=data["health"],
            max_health=data["max_health"],
            inventory=data["inventory"],
            quest_statuses=data.get("quest_statuses", {}),
        )
