import pytest

from domain.entities.dialogue import Condition
from domain.entities.player import Player
from domain.services.condition_evaluator import ConditionEvaluator


@pytest.fixture
def player() -> Player:
    return Player(id="p1", name="Hero", current_room_id="room_01")


@pytest.fixture
def player_with_quest() -> Player:
    player = Player(id="p1", name="Hero", current_room_id="room_01")
    player.completed_quest_ids = {"quest_01"}
    return player


@pytest.fixture
def evaluator() -> ConditionEvaluator:
    return ConditionEvaluator()


class TestConditionEvaluatorQuests:
    def test_requires_quest_completed_false_without_attribute(
        self, evaluator: ConditionEvaluator, player: Player
    ) -> None:
        condition = Condition(condition_type="requires_quest_completed", value="quest_01")
        assert evaluator.evaluate(condition, player) is False

    def test_requires_quest_completed_true_with_quest(
        self, evaluator: ConditionEvaluator, player_with_quest: Player
    ) -> None:
        condition = Condition(condition_type="requires_quest_completed", value="quest_01")
        assert evaluator.evaluate(condition, player_with_quest) is True

    def test_requires_quest_completed_false_without_quest(
        self, evaluator: ConditionEvaluator, player_with_quest: Player
    ) -> None:
        condition = Condition(condition_type="requires_quest_completed", value="quest_02")
        assert evaluator.evaluate(condition, player_with_quest) is False

    def test_requires_item_still_works(self, evaluator: ConditionEvaluator, player: Player) -> None:
        player.inventory.add_item("item_old_key")
        condition = Condition(condition_type="requires_item", value="item_old_key")
        assert evaluator.evaluate(condition, player) is True

    def test_unknown_condition_type_returns_false(self, evaluator: ConditionEvaluator, player: Player) -> None:
        condition = Condition(condition_type="unknown_type", value="something")
        assert evaluator.evaluate(condition, player) is False
