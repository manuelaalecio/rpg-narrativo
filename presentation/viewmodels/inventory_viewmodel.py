from PySide6.QtCore import QObject, Signal

from application.ports.repositories.content_repository_port import ContentRepositoryPort
from application.use_cases.use_item import UseItemUseCase
from domain.entities.player import Player


class InventoryViewModel(QObject):
    """ViewModel for the inventory screen.

    Exposes primitive observable state (strings, lists) to the View.
    Never exposes domain entities (Item, Inventory, Player) directly.
    """

    inventory_updated = Signal(list)
    player_stats_updated = Signal(int, int)
    log_message = Signal(str)

    def __init__(
        self,
        player: Player,
        use_item_uc: UseItemUseCase,
        content_repository: ContentRepositoryPort,
    ) -> None:
        super().__init__()
        self._player = player
        self._use_item_uc = use_item_uc
        self._content_repository = content_repository

        self._items: list[dict] = []

    @property
    def items(self) -> list[dict]:
        return self._items

    @property
    def player_health(self) -> int:
        return self._player.health

    @property
    def player_max_health(self) -> int:
        return self._player.max_health

    def refresh(self) -> None:
        """Reload the inventory state from the player and emit updates."""
        self._items = []
        for item_id in self._player.inventory.item_ids:
            try:
                item = self._content_repository.get_item(item_id)
                self._items.append(
                    {
                        "item_id": item.id,
                        "name": item.name,
                        "description": item.description,
                        "quantity": self._player.inventory.get_quantity(item_id),
                        "usable": item.usable,
                    }
                )
            except KeyError:
                self._items.append(
                    {
                        "item_id": item_id,
                        "name": item_id,
                        "description": "Unknown item.",
                        "quantity": self._player.inventory.get_quantity(item_id),
                        "usable": False,
                    }
                )
        self.inventory_updated.emit(self._items)
        self.player_stats_updated.emit(self._player.health, self._player.max_health)

    def use_item(self, item_id: str) -> None:
        """Use an item from the inventory and refresh."""
        result = self._use_item_uc.execute(self._player, item_id)
        self.log_message.emit(result.message)
        self.refresh()
