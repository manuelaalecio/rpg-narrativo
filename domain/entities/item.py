from dataclasses import dataclass

from domain.value_objects.item_type import ItemType


@dataclass
class Item:
    """Definition of a game item: name, description, type, and flags."""

    id: str
    name: str
    description: str
    item_type: ItemType
    usable: bool = False
    stackable: bool = False
