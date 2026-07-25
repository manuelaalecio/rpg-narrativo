import pytest

from domain.entities.dialogue import Condition
from domain.entities.player import Player
from domain.services.condition_evaluator import ConditionEvaluator


@pytest.fixture
def evaluator() -> ConditionEvaluator:
    return ConditionEvaluator()


@pytest.fixture
def player() -> Player:
    return Player(id="p1", name="Hero", current_room_id="room_01")


@pytest.fixture
def player_with_key() -> Player:
    player = Player(id="p1", name="Hero", current_room_id="room_01")
    player.inventory.add_item("item_old_key")
    return player


class TestConditionEvaluator:
    def test_requires_item_true(self, evaluator: ConditionEvaluator, player_with_key: Player) -> None:
        condition = Condition(condition_type="requires_item", value="item_old_key")
        assert evaluator.evaluate(condition, player_with_key) is True

    def test_requires_item_false(self, evaluator: ConditionEvaluator, player: Player) -> None:
        condition = Condition(condition_type="requires_item", value="item_old_key")
        assert evaluator.evaluate(condition, player) is False

    def test_unknown_condition_returns_false(self, evaluator: ConditionEvaluator, player: Player) -> None:
        condition = Condition(condition_type="unknown_type", value="something")
        assert evaluator.evaluate(condition, player) is False
