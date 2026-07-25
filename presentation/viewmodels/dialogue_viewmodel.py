from PySide6.QtCore import QObject, Signal

from application.use_cases.choose_dialogue_option import ChooseDialogueOptionUseCase
from application.use_cases.start_dialogue import StartDialogueUseCase
from domain.entities.dialogue import Dialogue
from domain.entities.player import Player


class DialogueViewModel(QObject):
    """ViewModel for the dialogue screen.

    Exposes primitive observable state (strings, lists) to the View.
    Never exposes domain entities directly.
    """

    dialogue_updated = Signal(str, str, list)
    dialogue_ended = Signal()
    log_message = Signal(str)

    def __init__(
        self,
        player: Player,
        start_dialogue_uc: StartDialogueUseCase,
        choose_option_uc: ChooseDialogueOptionUseCase,
    ) -> None:
        super().__init__()
        self._player = player
        self._start_uc = start_dialogue_uc
        self._choose_uc = choose_option_uc

        self._dialogue: Dialogue | None = None
        self._npc_id: str = ""
        self._npc_name: str = ""
        self._npc_text: str = ""
        self._available_options: list[str] = []

    @property
    def npc_name(self) -> str:
        return self._npc_name

    @property
    def npc_text(self) -> str:
        return self._npc_text

    @property
    def available_options(self) -> list[str]:
        return self._available_options

    @property
    def is_active(self) -> bool:
        return self._dialogue is not None and not self._dialogue.is_ended

    def start_dialogue(self, npc_id: str) -> None:
        """Start a dialogue with the given NPC."""
        result = self._start_uc.execute(self._player, npc_id)
        if not result.success:
            self.log_message.emit(result.message)
            return

        self._npc_id = npc_id
        self._dialogue = result.data["dialogue"] if result.data else None
        self._npc_name = result.data["npc_name"] if result.data else ""
        self._update_state()

    def choose_option(self, option_index: int) -> None:
        """Choose a dialogue option by its displayed index."""
        if self._dialogue is None:
            return

        available = self._dialogue.get_available_options(self._player)
        if option_index < 0 or option_index >= len(available):
            return

        original_index, _ = available[option_index]

        result = self._choose_uc.execute(self._dialogue, original_index, self._player, self._npc_id)

        if not result.success:
            self.log_message.emit(result.message)
            return

        if result.data and result.data.get("ended"):
            self._dialogue = None
            self._npc_text = ""
            self._available_options = []
            self.dialogue_ended.emit()
        else:
            self._update_state()

    def _update_state(self) -> None:
        """Refresh observable state from the current dialogue node."""
        if self._dialogue is None:
            return

        node = self._dialogue.get_current_node()
        if node is None:
            return

        self._npc_text = node.npc_text

        available = self._dialogue.get_available_options(self._player)
        self._available_options = [opt.text for _, opt in available]

        self.dialogue_updated.emit(self._npc_name, self._npc_text, self._available_options)
