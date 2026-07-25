import pytest

from presentation.state_machine.game_state import GameState
from presentation.state_machine.game_state_machine import GameStateMachine


@pytest.fixture
def state_machine() -> GameStateMachine:
    return GameStateMachine(initial_state=GameState.MAIN_MENU)


class TestGameStateMachine:
    def test_initial_state(self, state_machine: GameStateMachine) -> None:
        assert state_machine.current_state == GameState.MAIN_MENU

    def test_allowed_transition(self, state_machine: GameStateMachine) -> None:
        assert state_machine.can_transition_to(GameState.EXPLORATION)
        result = state_machine.transition_to(GameState.EXPLORATION)
        assert result is True
        assert state_machine.current_state == GameState.EXPLORATION

    def test_disallowed_transition(self, state_machine: GameStateMachine) -> None:
        assert not state_machine.can_transition_to(GameState.COMBAT)
        result = state_machine.transition_to(GameState.COMBAT)
        assert result is False
        assert state_machine.current_state == GameState.MAIN_MENU

    def test_callback_called_on_transition(self, state_machine: GameStateMachine) -> None:
        received_states: list[GameState] = []
        state_machine.on_state_change(lambda s: received_states.append(s))

        state_machine.transition_to(GameState.EXPLORATION)
        state_machine.transition_to(GameState.DIALOGUE)

        assert received_states == [GameState.EXPLORATION, GameState.DIALOGUE]

    def test_callback_not_called_on_failed_transition(self, state_machine: GameStateMachine) -> None:
        received_states: list[GameState] = []
        state_machine.on_state_change(lambda s: received_states.append(s))

        state_machine.transition_to(GameState.COMBAT)

        assert received_states == []

    def test_multiple_callbacks(self, state_machine: GameStateMachine) -> None:
        calls: list[int] = []
        state_machine.on_state_change(lambda _: calls.append(1))
        state_machine.on_state_change(lambda _: calls.append(2))

        state_machine.transition_to(GameState.EXPLORATION)

        assert calls == [1, 2]

    def test_exploration_transitions(self) -> None:
        sm = GameStateMachine(initial_state=GameState.EXPLORATION)
        assert sm.can_transition_to(GameState.DIALOGUE)
        assert sm.can_transition_to(GameState.COMBAT)
        assert sm.can_transition_to(GameState.INVENTORY)
        assert sm.can_transition_to(GameState.PAUSED)
        assert sm.can_transition_to(GameState.MAIN_MENU)
        assert not sm.can_transition_to(GameState.LOADING)

    def test_all_valid_transitions(self) -> None:
        """Test all valid transitions according to the transition table."""
        # MAIN_MENU -> LOADING, EXPLORATION
        sm = GameStateMachine(initial_state=GameState.MAIN_MENU)
        assert sm.transition_to(GameState.LOADING)
        sm = GameStateMachine(initial_state=GameState.MAIN_MENU)
        assert sm.transition_to(GameState.EXPLORATION)

        # LOADING -> EXPLORATION, MAIN_MENU
        sm = GameStateMachine(initial_state=GameState.LOADING)
        assert sm.transition_to(GameState.EXPLORATION)
        sm = GameStateMachine(initial_state=GameState.LOADING)
        assert sm.transition_to(GameState.MAIN_MENU)

        # EXPLORATION -> DIALOGUE, COMBAT, INVENTORY, PAUSED, MAIN_MENU
        sm = GameStateMachine(initial_state=GameState.EXPLORATION)
        assert sm.transition_to(GameState.DIALOGUE)
        sm = GameStateMachine(initial_state=GameState.EXPLORATION)
        assert sm.transition_to(GameState.COMBAT)
        sm = GameStateMachine(initial_state=GameState.EXPLORATION)
        assert sm.transition_to(GameState.INVENTORY)
        sm = GameStateMachine(initial_state=GameState.EXPLORATION)
        assert sm.transition_to(GameState.PAUSED)
        sm = GameStateMachine(initial_state=GameState.EXPLORATION)
        assert sm.transition_to(GameState.MAIN_MENU)

        # DIALOGUE -> EXPLORATION, COMBAT
        sm = GameStateMachine(initial_state=GameState.DIALOGUE)
        assert sm.transition_to(GameState.EXPLORATION)
        sm = GameStateMachine(initial_state=GameState.DIALOGUE)
        assert sm.transition_to(GameState.COMBAT)

        # COMBAT -> EXPLORATION, INVENTORY
        sm = GameStateMachine(initial_state=GameState.COMBAT)
        assert sm.transition_to(GameState.EXPLORATION)
        sm = GameStateMachine(initial_state=GameState.COMBAT)
        assert sm.transition_to(GameState.INVENTORY)

        # INVENTORY -> EXPLORATION, COMBAT
        sm = GameStateMachine(initial_state=GameState.INVENTORY)
        assert sm.transition_to(GameState.EXPLORATION)
        sm = GameStateMachine(initial_state=GameState.INVENTORY)
        assert sm.transition_to(GameState.COMBAT)

        # PAUSED -> EXPLORATION, MAIN_MENU
        sm = GameStateMachine(initial_state=GameState.PAUSED)
        assert sm.transition_to(GameState.EXPLORATION)
        sm = GameStateMachine(initial_state=GameState.PAUSED)
        assert sm.transition_to(GameState.MAIN_MENU)

    def test_invalid_transitions(self) -> None:
        """Test that invalid transitions are rejected."""
        # MAIN_MENU cannot go to DIALOGUE, COMBAT, INVENTORY, PAUSED
        sm = GameStateMachine(initial_state=GameState.MAIN_MENU)
        assert not sm.transition_to(GameState.DIALOGUE)
        assert not sm.transition_to(GameState.COMBAT)
        assert not sm.transition_to(GameState.INVENTORY)
        assert not sm.transition_to(GameState.PAUSED)

        # DIALOGUE cannot go to INVENTORY, PAUSED, MAIN_MENU, LOADING
        sm = GameStateMachine(initial_state=GameState.DIALOGUE)
        assert not sm.transition_to(GameState.INVENTORY)
        assert not sm.transition_to(GameState.PAUSED)
        assert not sm.transition_to(GameState.MAIN_MENU)
        assert not sm.transition_to(GameState.LOADING)

        # COMBAT cannot go to DIALOGUE, PAUSED, MAIN_MENU, LOADING
        sm = GameStateMachine(initial_state=GameState.COMBAT)
        assert not sm.transition_to(GameState.DIALOGUE)
        assert not sm.transition_to(GameState.PAUSED)
        assert not sm.transition_to(GameState.MAIN_MENU)
        assert not sm.transition_to(GameState.LOADING)

        # LOADING cannot go to DIALOGUE, COMBAT, INVENTORY, PAUSED
        sm = GameStateMachine(initial_state=GameState.LOADING)
        assert not sm.transition_to(GameState.DIALOGUE)
        assert not sm.transition_to(GameState.COMBAT)
        assert not sm.transition_to(GameState.INVENTORY)
        assert not sm.transition_to(GameState.PAUSED)

    def test_state_unchanged_on_invalid_transition(self) -> None:
        """Verify state doesn't change when transition is invalid."""
        sm = GameStateMachine(initial_state=GameState.MAIN_MENU)
        initial_state = sm.current_state

        result = sm.transition_to(GameState.COMBAT)

        assert result is False
        assert sm.current_state == initial_state

    def test_all_game_states_defined(self) -> None:
        """Verify all expected game states are defined in the enum."""
        expected_states = {
            "MAIN_MENU",
            "LOADING",
            "EXPLORATION",
            "DIALOGUE",
            "COMBAT",
            "INVENTORY",
            "PAUSED",
        }
        actual_states = {state.name for state in GameState}
        assert actual_states == expected_states
