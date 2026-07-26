"""ViewModel for main menu and save/load operations."""

from PySide6.QtCore import QObject, Signal

from application.ports.repositories.save_game_repository_port import (
    SaveGameRepositoryPort,
)
from application.use_cases.load_game import LoadGameUseCase
from application.use_cases.save_game import SaveGameUseCase
from domain.entities.player import Player


class MenuViewModel(QObject):
    """ViewModel for menu operations including save/load."""

    saves_list_updated = Signal(list)  # list[dict]
    game_loaded = Signal(object)  # Player
    save_completed = Signal(str)  # message
    error_occurred = Signal(str)  # error message

    def __init__(
        self,
        save_repository: SaveGameRepositoryPort,
        save_use_case: SaveGameUseCase,
        load_use_case: LoadGameUseCase,
    ) -> None:
        super().__init__()
        self._save_repository = save_repository
        self._save_use_case = save_use_case
        self._load_use_case = load_use_case

    def refresh_saves_list(self) -> None:
        """Refresh the list of available saves."""
        try:
            saves = self._save_repository.list_saves()
            # Convert to list of dicts for UI (primitives only)
            saves_data = [
                {
                    "slot": save.slot,
                    "save_name": save.save_name,
                    "timestamp": save.timestamp.isoformat(),
                }
                for save in saves
            ]
            self.saves_list_updated.emit(saves_data)
        except Exception as e:
            self.error_occurred.emit(f"Failed to load saves list: {e}")

    def save_game(self, player: Player, slot: str, save_name: str | None = None) -> None:
        """Save the current game."""
        result = self._save_use_case.execute(player, slot, save_name)

        if result.success:
            self.save_completed.emit(result.message)
            self.refresh_saves_list()  # Refresh list after save
        else:
            self.error_occurred.emit(result.message)

    def load_game(self, slot: str) -> None:
        """Load a game from the specified slot."""
        result = self._load_use_case.execute(slot)

        if result.success and result.data:
            player = result.data["player"]
            self.game_loaded.emit(player)
        else:
            self.error_occurred.emit(result.message)
