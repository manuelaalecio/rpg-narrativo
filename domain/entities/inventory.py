from dataclasses import dataclass, field

from domain.exceptions import (
    InvalidQuantityError,
    InventoryFullError,
    ItemNotFoundError,
)


@dataclass
class Inventory:
    """Collection of items owned by a player, with optional capacity limit."""

    max_capacity: int | None = None
    _items: dict[str, int] = field(default_factory=dict)

    @property
    def total_quantity(self) -> int:
        """Sum of all item quantities in the inventory."""
        return sum(self._items.values())

    def add_item(self, item_id: str, quantity: int = 1) -> None:
        """Add quantity of an item. Raises on invalid quantity or full inventory."""
        if quantity <= 0:
            raise InvalidQuantityError(quantity)
        if self.max_capacity is not None and self.total_quantity + quantity > self.max_capacity:
            raise InventoryFullError(self.max_capacity)
        self._items[item_id] = self._items.get(item_id, 0) + quantity

    def remove_item(self, item_id: str, quantity: int = 1) -> None:
        """Remove quantity of an item. Raises on invalid quantity or missing item."""
        if quantity <= 0:
            raise InvalidQuantityError(quantity)
        if item_id not in self._items:
            raise ItemNotFoundError(item_id)
        current = self._items[item_id]
        if quantity > current:
            raise ItemNotFoundError(item_id)
        if current == quantity:
            del self._items[item_id]
        else:
            self._items[item_id] = current - quantity

    def has_item(self, item_id: str) -> bool:
        """Check whether the inventory contains at least one of the given item."""
        return self._items.get(item_id, 0) > 0

    def get_quantity(self, item_id: str) -> int:
        """Return the quantity of an item, or 0 if not present."""
        return self._items.get(item_id, 0)

    @property
    def item_ids(self) -> list[str]:
        """Return all item ids currently in the inventory."""
        return list(self._items.keys())
