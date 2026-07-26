from application.ports.event_bus.event_bus_port import EventBusPort
from application.ports.repositories.content_repository_port import ContentRepositoryPort
from application.use_cases.use_case_result import UseCaseResult
from domain.entities.player import Player
from domain.events.item_used import ItemUsed
from domain.services.item_effect_applier import ItemEffectApplier


class UseItemUseCase:
    """Use an item from the player's inventory, applying its effect."""

    def __init__(
        self,
        content_repository: ContentRepositoryPort,
        event_bus: EventBusPort,
    ) -> None:
        self._content_repository = content_repository
        self._event_bus = event_bus
        self._effect_applier = ItemEffectApplier()

    def execute(self, player: Player, item_id: str) -> UseCaseResult:
        """Use the specified item from the player's inventory."""
        if not player.inventory.has_item(item_id):
            return UseCaseResult(
                success=False,
                message=f"You don't have '{item_id}' in your inventory.",
            )

        try:
            item = self._content_repository.get_item(item_id)
        except KeyError:
            return UseCaseResult(
                success=False,
                message=f"Item '{item_id}' not found in content.",
            )

        if not item.usable:
            return UseCaseResult(
                success=False,
                message=f"You can't use {item.name}.",
            )

        effect_message = ""
        if item.effect is not None:
            effect_message = self._effect_applier.apply(item.effect, player)

        player.inventory.remove_item(item_id)

        self._event_bus.publish(ItemUsed(item_id=item_id, player_id=player.id))

        return UseCaseResult(
            success=True,
            message=f"You use {item.name}. {effect_message}".strip(),
            data={"item_id": item_id, "effect_message": effect_message},
        )
