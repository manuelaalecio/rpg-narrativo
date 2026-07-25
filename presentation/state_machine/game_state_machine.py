"""
Game State Machine - Controls screen transitions in the RPG.

Transition Table (from -> allowed targets):
--------------------------------------------
MAIN_MENU    -> LOADING, EXPLORATION
LOADING      -> EXPLORATION, MAIN_MENU
EXPLORATION  -> DIALOGUE, COMBAT, INVENTORY, PAUSED, MAIN_MENU
DIALOGUE     -> EXPLORATION, COMBAT
COMBAT       -> EXPLORATION, INVENTORY
INVENTORY    -> EXPLORATION, COMBAT
PAUSED       -> EXPLORATION, MAIN_MENU

Invalid transitions return False (no exception raised) to allow
UI code to gracefully handle user actions without try/except blocks.
"""

from collections.abc import Callable

from presentation.state_machine.game_state import GameState

StateChangeCallback = Callable[[GameState], None]


class GameStateMachine:
    """Controls transitions between game states/screens.

    Uses plain callbacks for state change notifications to remain
    testable without Qt. The MainWindow connects to these callbacks
    to switch screens in the QStackedWidget.
    """

    ALLOWED_TRANSITIONS: dict[GameState, set[GameState]] = {
        GameState.MAIN_MENU: {GameState.LOADING, GameState.EXPLORATION},
        GameState.LOADING: {GameState.EXPLORATION, GameState.MAIN_MENU},
        GameState.EXPLORATION: {
            GameState.DIALOGUE,
            GameState.COMBAT,
            GameState.INVENTORY,
            GameState.PAUSED,
            GameState.MAIN_MENU,
        },
        GameState.DIALOGUE: {GameState.EXPLORATION, GameState.COMBAT},
        GameState.COMBAT: {GameState.EXPLORATION, GameState.INVENTORY},
        GameState.INVENTORY: {GameState.EXPLORATION, GameState.COMBAT},
        GameState.PAUSED: {GameState.EXPLORATION, GameState.MAIN_MENU},
    }

    def __init__(self, initial_state: GameState = GameState.MAIN_MENU) -> None:
        self._current_state = initial_state
        self._on_state_change_callbacks: list[StateChangeCallback] = []

    @property
    def current_state(self) -> GameState:
        """Return the current game state."""
        return self._current_state

    def can_transition_to(self, target_state: GameState) -> bool:
        """Check if transitioning to the target state is allowed."""
        allowed = self.ALLOWED_TRANSITIONS.get(self._current_state, set())
        return target_state in allowed

    def transition_to(self, target_state: GameState) -> bool:
        """Attempt to transition to the target state.

        Returns True if successful, False if the transition is not allowed.
        """
        if not self.can_transition_to(target_state):
            return False

        self._current_state = target_state
        for callback in self._on_state_change_callbacks:
            callback(target_state)
        return True

    def on_state_change(self, callback: StateChangeCallback) -> None:
        """Register a callback to be called when the state changes."""
        self._on_state_change_callbacks.append(callback)
