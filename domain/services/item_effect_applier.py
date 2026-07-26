from domain.entities.player import Player
from domain.value_objects.item_effect import ItemEffect


class ItemEffectApplier:
    """Applies item effects to a player using the Strategy pattern.

    Each effect type maps to a dedicated method, allowing new effect types
    to be added without modifying existing logic.
    """

    def apply(self, effect: ItemEffect, player: Player) -> str:
        """Apply an effect to the player and return a description of what happened."""
        method_name = f"_apply_{effect.effect_type.value}"
        applier = getattr(self, method_name, None)
        if applier is None:
            return "Nothing happens."
        return applier(effect.value, player)

    def _apply_heal(self, value: int, player: Player) -> str:
        """Restore health, capped at max_health."""
        old_health = player.health
        player.health = min(player.health + value, player.max_health)
        healed = player.health - old_health
        if healed == 0:
            return "You are already at full health."
        return f"You recover {healed} health."
