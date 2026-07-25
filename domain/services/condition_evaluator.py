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
