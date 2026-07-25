from application.ports.event_bus.event_bus_port import EventBusPort
from application.ports.repositories.content_repository_port import ContentRepositoryPort
from application.use_cases.use_case_result import UseCaseResult
from domain.entities.player import Player
from domain.events.item_picked_up import ItemPickedUp


class PickUpItemUseCase:
    """Pick up an item from the current room and add it to the player's inventory."""

    def __init__(
        self,
        content_repository: ContentRepositoryPort,
        event_bus: EventBusPort,
    ) -> None:
        self._content_repository = content_repository
        self._event_bus = event_bus

    def execute(self, player: Player, item_id: str) -> UseCaseResult:
        """Attempt to pick up the specified item from the current room."""
        game_map = self._content_repository.get_map()
        room = game_map.get_room(player.current_room_id)

        if item_id not in room.item_ids:
            return UseCaseResult(
                success=False,
                message=f"There is no '{item_id}' here to pick up.",
            )

        item = self._content_repository.get_item(item_id)
        player.inventory.add_item(item_id)
        room.remove_item(item_id)

        self._event_bus.publish(ItemPickedUp(item_id=item_id, room_id=room.id))

        return UseCaseResult(
            success=True,
            message=f"You pick up the {item.name}.",
            data={"item_id": item_id},
        )
