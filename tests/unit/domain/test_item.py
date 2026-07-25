from domain.entities.item import Item
from domain.value_objects.item_type import ItemType


class TestItem:
    def test_create_item(self) -> None:
        item = Item(
            id="sword_01",
            name="Iron Sword",
            description="A sturdy iron sword.",
            item_type=ItemType.WEAPON,
            usable=True,
            stackable=False,
        )
        assert item.id == "sword_01"
        assert item.name == "Iron Sword"
        assert item.item_type == ItemType.WEAPON
        assert item.usable is True
        assert item.stackable is False

    def test_default_flags(self) -> None:
        item = Item(
            id="misc_01",
            name="Mysterious Stone",
            description="A smooth stone.",
            item_type=ItemType.MISC,
        )
        assert item.usable is False
        assert item.stackable is False

    def test_item_types(self) -> None:
        assert ItemType.WEAPON.value == "weapon"
        assert ItemType.CONSUMABLE.value == "consumable"
        assert ItemType.KEY.value == "key"
        assert ItemType.MISC.value == "misc"
