from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from presentation.state_machine.game_state import GameState
from presentation.state_machine.game_state_machine import GameStateMachine


class PauseScreen(QWidget):
    """Pause menu screen with save, resume, and quit options."""

    save_game_requested = Signal()

    def __init__(self, state_machine: GameStateMachine) -> None:
        super().__init__()
        self._state_machine = state_machine

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel("Jogo Pausado")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(label)

        resume_button = QPushButton("Continuar")
        resume_button.setFixedSize(200, 40)
        resume_button.clicked.connect(self._on_resume_clicked)
        layout.addWidget(resume_button, alignment=Qt.AlignCenter)

        save_button = QPushButton("Salvar Jogo")
        save_button.setFixedSize(200, 40)
        save_button.clicked.connect(self._on_save_clicked)
        layout.addWidget(save_button, alignment=Qt.AlignCenter)

        menu_button = QPushButton("Menu Principal")
        menu_button.setFixedSize(200, 40)
        menu_button.clicked.connect(self._on_menu_clicked)
        layout.addWidget(menu_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def _on_resume_clicked(self) -> None:
        self._state_machine.transition_to(GameState.EXPLORATION)

    def _on_save_clicked(self) -> None:
        self.save_game_requested.emit()

    def _on_menu_clicked(self) -> None:
        self._state_machine.transition_to(GameState.MAIN_MENU)
