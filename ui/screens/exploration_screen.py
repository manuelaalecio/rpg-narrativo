from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from presentation.state_machine.game_state import GameState
from presentation.state_machine.game_state_machine import GameStateMachine
from presentation.viewmodels.exploration_viewmodel import ExplorationViewModel


class ExplorationScreen(QWidget):
    """Screen for exploring rooms, viewing exits, and picking up items."""

    talk_to_npc_requested = Signal(str)

    def __init__(self, view_model: ExplorationViewModel, state_machine: GameStateMachine) -> None:
        super().__init__()
        self._view_model = view_model
        self._state_machine = state_machine

        self._setup_ui()
        self._connect_signals()

        self._view_model.look()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout()

        self._room_name_label = QLabel()
        self._room_name_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        main_layout.addWidget(self._room_name_label)

        self._description_browser = QTextBrowser()
        self._description_browser.setOpenExternalLinks(False)
        main_layout.addWidget(self._description_browser)

        exits_layout = QHBoxLayout()
        exits_label = QLabel("Saídas:")
        exits_label.setStyleSheet("font-weight: bold;")
        exits_layout.addWidget(exits_label)
        self._exits_container = QWidget()
        self._exits_layout = QHBoxLayout(self._exits_container)
        self._exits_layout.setContentsMargins(0, 0, 0, 0)
        exits_layout.addWidget(self._exits_container)
        exits_layout.addStretch()
        main_layout.addLayout(exits_layout)

        items_layout = QHBoxLayout()
        items_label = QLabel("Itens:")
        items_label.setStyleSheet("font-weight: bold;")
        items_layout.addWidget(items_label)
        self._items_list = QListWidget()
        self._items_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        items_layout.addWidget(self._items_list)
        main_layout.addLayout(items_layout)

        log_label = QLabel("Log:")
        log_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(log_label)
        self._log_browser = QTextBrowser()
        self._log_browser.setMaximumHeight(150)
        main_layout.addWidget(self._log_browser)

        # Temporary navigation buttons for testing state transitions
        # These will be replaced by real triggers in future steps
        nav_label = QLabel("Ações:")
        nav_label.setStyleSheet("font-weight: bold; color: #999;")
        main_layout.addWidget(nav_label)

        nav_layout = QHBoxLayout()

        combat_btn = QPushButton("Combate (placeholder)")
        combat_btn.clicked.connect(lambda: self._state_machine.transition_to(GameState.COMBAT))
        nav_layout.addWidget(combat_btn)

        inventory_btn = QPushButton("Inventário")
        inventory_btn.clicked.connect(lambda: self._state_machine.transition_to(GameState.INVENTORY))
        nav_layout.addWidget(inventory_btn)

        pause_btn = QPushButton("Pausar (placeholder)")
        pause_btn.clicked.connect(lambda: self._state_machine.transition_to(GameState.PAUSED))
        nav_layout.addWidget(pause_btn)

        main_layout.addLayout(nav_layout)

        npcs_label = QLabel("NPCs:")
        npcs_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(npcs_label)
        self._npcs_container = QWidget()
        self._npcs_layout = QVBoxLayout(self._npcs_container)
        self._npcs_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._npcs_container)

        self.setLayout(main_layout)

    def _connect_signals(self) -> None:
        self._view_model.room_updated.connect(self._on_room_updated)
        self._view_model.log_message.connect(self._on_log_message)

    def _on_room_updated(
        self, name: str, description: str, exits: list[str], items: list[str], npc_ids: list[str]
    ) -> None:
        self._room_name_label.setText(name)
        self._description_browser.setPlainText(description)

        self._clear_exits()
        for exit_direction in exits:
            button = QPushButton(exit_direction.capitalize())
            button.clicked.connect(lambda checked, d=exit_direction: self._on_exit_clicked(d))
            self._exits_layout.addWidget(button)

        self._items_list.clear()
        for item_id in items:
            list_item = QListWidgetItem(item_id)
            list_item.setData(Qt.UserRole, item_id)
            self._items_list.addItem(list_item)

        self._clear_npcs()
        for npc_id in npc_ids:
            button = QPushButton(f"Falar com {npc_id}")
            button.clicked.connect(lambda checked, nid=npc_id: self._on_talk_to_npc(nid))
            self._npcs_layout.addWidget(button)

    def _on_log_message(self, message: str) -> None:
        self._log_browser.append(f"> {message}")

    def _on_exit_clicked(self, direction: str) -> None:
        self._view_model.move(direction)

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        item_id = item.data(Qt.UserRole)
        if item_id:
            self._view_model.pick_up_item(item_id)

    def _clear_exits(self) -> None:
        while self._exits_layout.count():
            child = self._exits_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _on_talk_to_npc(self, npc_id: str) -> None:
        self.talk_to_npc_requested.emit(npc_id)

    def _clear_npcs(self) -> None:
        while self._npcs_layout.count():
            child = self._npcs_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
