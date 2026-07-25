from dataclasses import dataclass, field

from domain.entities.inventory import Inventory


@dataclass
class Player:
    """Player state: identity, position, inventory, and basic attributes."""

    id: str
    name: str
    current_room_id: str
    inventory: Inventory = field(default_factory=Inventory)
    health: int = 100
    max_health: int = 100

    def move_to(self, room_id: str) -> None:
        """Update the player's current room. Validation is the Use Case's responsibility."""
        self.current_room_id = room_id
