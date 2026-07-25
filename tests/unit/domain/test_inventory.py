import pytest

from domain.entities.inventory import Inventory
from domain.exceptions import (
    InvalidQuantityError,
    InventoryFullError,
    ItemNotFoundError,
)


@pytest.fixture
def inventory() -> Inventory:
    return Inventory()


@pytest.fixture
def limited_inventory() -> Inventory:
    return Inventory(max_capacity=5)


class TestInventory:
    def test_add_item(self, inventory: Inventory) -> None:
        inventory.add_item("sword_01")
        assert inventory.has_item("sword_01")
        assert inventory.get_quantity("sword_01") == 1

    def test_add_item_multiple(self, inventory: Inventory) -> None:
        inventory.add_item("potion_01", quantity=3)
        assert inventory.get_quantity("potion_01") == 3

    def test_add_item_stacks(self, inventory: Inventory) -> None:
        inventory.add_item("potion_01", quantity=2)
        inventory.add_item("potion_01", quantity=3)
        assert inventory.get_quantity("potion_01") == 5

    def test_add_item_invalid_quantity_zero(self, inventory: Inventory) -> None:
        with pytest.raises(InvalidQuantityError):
            inventory.add_item("sword_01", quantity=0)

    def test_add_item_invalid_quantity_negative(self, inventory: Inventory) -> None:
        with pytest.raises(InvalidQuantityError):
            inventory.add_item("sword_01", quantity=-1)

    def test_add_item_exceeds_capacity(self, limited_inventory: Inventory) -> None:
        limited_inventory.add_item("potion_01", quantity=5)
        with pytest.raises(InventoryFullError):
            limited_inventory.add_item("potion_02", quantity=1)

    def test_add_item_within_capacity(self, limited_inventory: Inventory) -> None:
        limited_inventory.add_item("potion_01", quantity=3)
        limited_inventory.add_item("potion_02", quantity=2)
        assert limited_inventory.total_quantity == 5

    def test_remove_item(self, inventory: Inventory) -> None:
        inventory.add_item("sword_01", quantity=2)
        inventory.remove_item("sword_01", quantity=1)
        assert inventory.get_quantity("sword_01") == 1

    def test_remove_item_all(self, inventory: Inventory) -> None:
        inventory.add_item("sword_01", quantity=2)
        inventory.remove_item("sword_01", quantity=2)
        assert not inventory.has_item("sword_01")

    def test_remove_item_nonexistent(self, inventory: Inventory) -> None:
        with pytest.raises(ItemNotFoundError):
            inventory.remove_item("nonexistent")

    def test_remove_item_invalid_quantity(self, inventory: Inventory) -> None:
        inventory.add_item("sword_01")
        with pytest.raises(InvalidQuantityError):
            inventory.remove_item("sword_01", quantity=0)

    def test_remove_item_more_than_available(self, inventory: Inventory) -> None:
        inventory.add_item("sword_01", quantity=1)
        with pytest.raises(ItemNotFoundError):
            inventory.remove_item("sword_01", quantity=5)

    def test_has_item_false(self, inventory: Inventory) -> None:
        assert not inventory.has_item("nonexistent")

    def test_get_quantity_missing(self, inventory: Inventory) -> None:
        assert inventory.get_quantity("nonexistent") == 0

    def test_total_quantity_empty(self, inventory: Inventory) -> None:
        assert inventory.total_quantity == 0

    def test_total_capacity_none_is_unlimited(self, inventory: Inventory) -> None:
        for i in range(100):
            inventory.add_item(f"item_{i}")
        assert inventory.total_quantity == 100
