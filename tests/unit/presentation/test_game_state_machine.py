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
        assert not sm.can_transition_to(GameState.LOADING)
