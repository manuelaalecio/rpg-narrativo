from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class LoadingScreen(QWidget):
    """Simple loading indicator screen."""

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel("Carregando...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 24px; color: #666;")
        layout.addWidget(label)

        self.setLayout(layout)
