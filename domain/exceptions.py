class DomainError(Exception):
    """Base exception for all domain errors."""


class InventoryFullError(DomainError):
    """Raised when adding an item would exceed inventory capacity."""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        super().__init__(f"Inventory is full (capacity: {capacity})")


class InvalidQuantityError(DomainError):
    """Raised when an item quantity operation receives an invalid value."""

    def __init__(self, quantity: int) -> None:
        self.quantity = quantity
        super().__init__(f"Quantity must be positive, got {quantity}")


class ItemNotFoundError(DomainError):
    """Raised when an item is not found in the inventory."""

    def __init__(self, item_id: str) -> None:
        self.item_id = item_id
        super().__init__(f"Item '{item_id}' not found in inventory")


class RoomNotFoundError(DomainError):
    """Raised when a room is not found in the map."""

    def __init__(self, room_id: str) -> None:
        self.room_id = room_id
        super().__init__(f"Room '{room_id}' not found in map")
