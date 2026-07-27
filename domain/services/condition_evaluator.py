from domain.entities.dialogue import Condition


class ConditionEvaluator:
    """Evaluates structured conditions against player state.

    Uses Strategy pattern: each condition type is a separate evaluation method.
    New condition types can be added by implementing new _evaluate_<type> methods.
    """

    def evaluate(self, condition: Condition, player) -> bool:
        """Evaluate a condition against the player's current state."""
        method_name = f"_evaluate_{condition.condition_type}"
        evaluator = getattr(self, method_name, None)
        if evaluator is None:
            return False
        return evaluator(condition.value, player)

    def _evaluate_requires_item(self, item_id: str, player) -> bool:
        """Check if player has the required item in inventory."""
        return player.inventory.has_item(item_id)

    def _evaluate_requires_quest_completed(self, quest_id: str, player) -> bool:
        """Check if the required quest has been completed.

        This requires the player to have a 'completed_quest_ids' attribute
        or the condition evaluator to be configured with a quest repository.
        For simplicity, we check player.completed_quest_ids if it exists.
        """
        if hasattr(player, "completed_quest_ids"):
            return quest_id in player.completed_quest_ids
        return False
