from PySide6.QtWidgets import QLabel, QPushButton, QTextBrowser, QVBoxLayout, QWidget

from presentation.state_machine.game_state import GameState
from presentation.state_machine.game_state_machine import GameStateMachine
from presentation.viewmodels.dialogue_viewmodel import DialogueViewModel


class DialogueScreen(QWidget):
    """Screen for NPC dialogues. Displays NPC speech and player options."""

    def __init__(self, view_model: DialogueViewModel, state_machine: GameStateMachine) -> None:
        super().__init__()
        self._view_model = view_model
        self._state_machine = state_machine

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()

        self._npc_name_label = QLabel()
        self._npc_name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4a7;")
        layout.addWidget(self._npc_name_label)

        self._npc_text_browser = QTextBrowser()
        self._npc_text_browser.setOpenExternalLinks(False)
        layout.addWidget(self._npc_text_browser)

        options_label = QLabel("Suas opções:")
        options_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(options_label)

        self._options_container = QWidget()
        self._options_layout = QVBoxLayout(self._options_container)
        self._options_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._options_container)

        self.setLayout(layout)

    def _connect_signals(self) -> None:
        self._view_model.dialogue_updated.connect(self._on_dialogue_updated)
        self._view_model.dialogue_ended.connect(self._on_dialogue_ended)

    def _on_dialogue_updated(self, npc_name: str, npc_text: str, options: list[str]) -> None:
        self._npc_name_label.setText(npc_name)
        self._npc_text_browser.setPlainText(npc_text)

        self._clear_options()
        for idx, option_text in enumerate(options):
            button = QPushButton(option_text)
            button.clicked.connect(lambda checked, i=idx: self._on_option_clicked(i))
            self._options_layout.addWidget(button)

    def _on_dialogue_ended(self) -> None:
        self._state_machine.transition_to(GameState.EXPLORATION)

    def _on_option_clicked(self, index: int) -> None:
        self._view_model.choose_option(index)

    def _clear_options(self) -> None:
        while self._options_layout.count():
            child = self._options_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
