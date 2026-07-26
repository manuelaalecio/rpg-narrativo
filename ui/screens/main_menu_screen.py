from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from presentation.state_machine.game_state import GameState
from presentation.state_machine.game_state_machine import GameStateMachine


class MainMenuScreen(QWidget):
    """Main menu screen with 'New Game' and 'Load Game' options."""

    load_game_requested = Signal(str)  # slot

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

        # Saves list
        saves_label = QLabel("Jogos Salvos:")
        saves_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
        layout.addWidget(saves_label, alignment=Qt.AlignCenter)

        self._saves_list = QListWidget()
        self._saves_list.setFixedSize(400, 200)
        self._saves_list.itemDoubleClicked.connect(self._on_save_double_clicked)
        layout.addWidget(self._saves_list, alignment=Qt.AlignCenter)

        load_button = QPushButton("Carregar Jogo")
        load_button.setFixedSize(200, 40)
        load_button.clicked.connect(self._on_load_clicked)
        layout.addWidget(load_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def update_saves_list(self, saves: list[dict]) -> None:
        """Update the saves list display."""
        self._saves_list.clear()
        for save_data in saves:
            item = QListWidgetItem(save_data["save_name"])
            item.setData(Qt.UserRole, save_data["slot"])
            self._saves_list.addItem(item)

    def _on_new_game_clicked(self) -> None:
        self._state_machine.transition_to(GameState.EXPLORATION)

    def _on_load_clicked(self) -> None:
        current_item = self._saves_list.currentItem()
        if current_item:
            slot = current_item.data(Qt.UserRole)
            self.load_game_requested.emit(slot)

    def _on_save_double_clicked(self, item: QListWidgetItem) -> None:
        slot = item.data(Qt.UserRole)
        self.load_game_requested.emit(slot)
