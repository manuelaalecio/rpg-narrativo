from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from presentation.state_machine.game_state import GameState
from presentation.state_machine.game_state_machine import GameStateMachine


class InventoryScreen(QWidget):
    """Placeholder screen for inventory system (to be implemented in Step 8)."""

    def __init__(self, state_machine: GameStateMachine) -> None:
        super().__init__()
        self._state_machine = state_machine

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel("Tela de Inventário (em construção)")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 24px; color: #666;")
        layout.addWidget(label)

        back_button = QPushButton("Voltar à Exploração")
        back_button.setFixedSize(200, 40)
        back_button.clicked.connect(self._on_back_clicked)
        layout.addWidget(back_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def _on_back_clicked(self) -> None:
        self._state_machine.transition_to(GameState.EXPLORATION)
