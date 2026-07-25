from PySide6.QtWidgets import QMainWindow, QStackedWidget, QWidget

from presentation.state_machine.game_state import GameState
from presentation.state_machine.game_state_machine import GameStateMachine


class MainWindow(QMainWindow):
    """Main application window with screen stack controlled by GameStateMachine."""

    def __init__(self, state_machine: GameStateMachine) -> None:
        super().__init__()
        self.setWindowTitle("RPG Narrativo")
        self.setMinimumSize(800, 600)

        self._state_machine = state_machine

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._screens: dict[GameState, int] = {}

        self._state_machine.on_state_change(self._on_state_change)

    def register_screen(self, state: GameState, screen: QWidget) -> None:
        """Register a screen widget for a given game state."""
        index = self._stack.addWidget(screen)
        self._screens[state] = index

    def show_initial_screen(self) -> None:
        """Display the screen for the current state."""
        self._switch_to_state(self._state_machine.current_state)

    def _on_state_change(self, new_state: GameState) -> None:
        self._switch_to_state(new_state)

    def _switch_to_state(self, state: GameState) -> None:
        if state in self._screens:
            self._stack.setCurrentIndex(self._screens[state])
