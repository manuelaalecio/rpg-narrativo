from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from presentation.state_machine.game_state import GameState
from presentation.state_machine.game_state_machine import GameStateMachine
from presentation.viewmodels.inventory_viewmodel import InventoryViewModel


class InventoryScreen(QWidget):
    """Screen displaying the player's inventory with option to use items."""

    def __init__(self, view_model: InventoryViewModel, state_machine: GameStateMachine) -> None:
        super().__init__()
        self._view_model = view_model
        self._state_machine = state_machine

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()

        title = QLabel("Inventário")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        self._health_label = QLabel()
        self._health_label.setStyleSheet("font-size: 14px; color: #c44;")
        layout.addWidget(self._health_label)

        self._items_container = QWidget()
        self._items_layout = QVBoxLayout(self._items_container)
        self._items_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._items_container)

        self._empty_label = QLabel("Seu inventário está vazio.")
        self._empty_label.setStyleSheet("color: #666;")
        self._empty_label.hide()
        layout.addWidget(self._empty_label)

        log_label = QLabel("Log:")
        log_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(log_label)
        self._log_browser = QTextBrowser()
        self._log_browser.setMaximumHeight(120)
        layout.addWidget(self._log_browser)

        back_button = QPushButton("Voltar à Exploração")
        back_button.setFixedSize(200, 40)
        back_button.clicked.connect(self._on_back_clicked)
        layout.addWidget(back_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def _connect_signals(self) -> None:
        self._view_model.inventory_updated.connect(self._on_inventory_updated)
        self._view_model.player_stats_updated.connect(self._on_player_stats_updated)
        self._view_model.log_message.connect(self._on_log_message)

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._view_model.refresh()

    def _on_inventory_updated(self, items: list) -> None:
        self._clear_items()
        if not items:
            self._empty_label.show()
            return
        self._empty_label.hide()
        for item_data in items:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 2, 0, 2)

            name_label = QLabel(f"{item_data['name']} (x{item_data['quantity']})")
            name_label.setStyleSheet("font-weight: bold;")
            row_layout.addWidget(name_label)

            desc_label = QLabel(item_data["description"])
            desc_label.setStyleSheet("color: #666;")
            row_layout.addWidget(desc_label)

            row_layout.addStretch()

            if item_data["usable"]:
                use_btn = QPushButton("Usar")
                use_btn.setFixedSize(60, 30)
                item_id = item_data["item_id"]
                use_btn.clicked.connect(lambda checked, iid=item_id: self._on_use_item(iid))
                row_layout.addWidget(use_btn)

            self._items_layout.addWidget(row)

    def _on_player_stats_updated(self, health: int, max_health: int) -> None:
        self._health_label.setText(f"Saúde: {health}/{max_health}")

    def _on_log_message(self, message: str) -> None:
        self._log_browser.append(f"> {message}")

    def _on_use_item(self, item_id: str) -> None:
        self._view_model.use_item(item_id)

    def _on_back_clicked(self) -> None:
        self._state_machine.transition_to(GameState.EXPLORATION)

    def _clear_items(self) -> None:
        while self._items_layout.count():
            child = self._items_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
