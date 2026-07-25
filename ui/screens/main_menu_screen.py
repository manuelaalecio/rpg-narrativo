from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from presentation.state_machine.game_state import GameState
from presentation.state_machine.game_state_machine import GameStateMachine


class MainMenuScreen(QWidget):
    """Main menu placeholder screen with a 'New Game' button."""

    def __init__(self, state_machine: GameStateMachine) -> None:
        super().__init__()
        self._state_machine = state_machine

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel("RPG Narrativo")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 32px; font-weight: bold;")
        layout.addWidget(title_label)

        new_game_button = QPushButton("Novo Jogo")
        new_game_button.setFixedSize(200, 50)
        new_game_button.clicked.connect(self._on_new_game_clicked)
        layout.addWidget(new_game_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def _on_new_game_clicked(self) -> None:
        self._state_machine.transition_to(GameState.EXPLORATION)
