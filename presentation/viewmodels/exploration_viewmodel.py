from PySide6.QtCore import QObject, Signal

from application.use_cases.look_at_room import LookAtRoomUseCase
from application.use_cases.move_to_room import MoveToRoomUseCase
from application.use_cases.pick_up_item import PickUpItemUseCase
from domain.entities.player import Player


class ExplorationViewModel(QObject):
    """ViewModel for the exploration screen.

    Exposes primitive observable state (strings, lists) to the View.
    Never exposes domain entities (Room, Item, Player) directly.
    """

    room_updated = Signal(str, str, list, list)
    log_message = Signal(str)

    def __init__(
        self,
        player: Player,
        move_use_case: MoveToRoomUseCase,
        look_use_case: LookAtRoomUseCase,
        pick_up_use_case: PickUpItemUseCase,
    ) -> None:
        super().__init__()
        self._player = player
        self._move_uc = move_use_case
        self._look_uc = look_use_case
        self._pick_up_uc = pick_up_use_case

        self._room_name = ""
        self._room_description = ""
        self._available_exits: list[str] = []
        self._room_items: list[str] = []

    @property
    def room_name(self) -> str:
        return self._room_name

    @property
    def room_description(self) -> str:
        return self._room_description

    @property
    def available_exits(self) -> list[str]:
        return self._available_exits

    @property
    def room_items(self) -> list[str]:
        return self._room_items

    def look(self) -> None:
        """Look at the current room and update observable state."""
        result = self._look_uc.execute(self._player)
        if result.success and result.data:
            self._room_name = result.data.get("name", "")
            self._room_description = result.data.get("description", "")
            self._available_exits = result.data.get("exits", [])
            self._room_items = result.data.get("item_ids", [])
            self.room_updated.emit(
                self._room_name,
                self._room_description,
                self._available_exits,
                self._room_items,
            )

    def move(self, direction: str) -> None:
        """Attempt to move in the given direction."""
        result = self._move_uc.execute(self._player, direction)
        self.log_message.emit(result.message)
        if result.success:
            self.look()

    def pick_up_item(self, item_id: str) -> None:
        """Attempt to pick up an item from the current room."""
        result = self._pick_up_uc.execute(self._player, item_id)
        self.log_message.emit(result.message)
        if result.success:
            self.look()
