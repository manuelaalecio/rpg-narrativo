from PySide6.QtCore import Qt
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

from presentation.viewmodels.exploration_viewmodel import ExplorationViewModel


class ExplorationScreen(QWidget):
    """Screen for exploring rooms, viewing exits, and picking up items."""

    def __init__(self, view_model: ExplorationViewModel) -> None:
        super().__init__()
        self._view_model = view_model

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

        self.setLayout(main_layout)

    def _connect_signals(self) -> None:
        self._view_model.room_updated.connect(self._on_room_updated)
        self._view_model.log_message.connect(self._on_log_message)

    def _on_room_updated(self, name: str, description: str, exits: list[str], items: list[str]) -> None:
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
