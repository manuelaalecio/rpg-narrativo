from application.ports.event_bus.event_bus_port import EventBusPort
from application.ports.repositories.content_repository_port import ContentRepositoryPort
from application.use_cases.use_case_result import UseCaseResult
from domain.entities.player import Player
from domain.events.player_moved import PlayerMoved


class MoveToRoomUseCase:
    """Move the player to an adjacent room in a given direction."""

    def __init__(
        self,
        content_repository: ContentRepositoryPort,
        event_bus: EventBusPort,
    ) -> None:
        self._content_repository = content_repository
        self._event_bus = event_bus

    def execute(self, player: Player, direction: str) -> UseCaseResult:
        """Attempt to move the player in the given direction.

        Returns success if the exit exists, failure otherwise.
        """
        game_map = self._content_repository.get_map()
        current_room = game_map.get_room(player.current_room_id)

        target_room_id = current_room.get_exit(direction)
        if target_room_id is None:
            return UseCaseResult(
                success=False,
                message=f"There is no exit to the {direction}.",
            )

        from_room_id = player.current_room_id
        player.move_to(target_room_id)

        self._event_bus.publish(PlayerMoved(from_room_id=from_room_id, to_room_id=target_room_id))

        return UseCaseResult(
            success=True,
            message=f"You move {direction}.",
            data={"room_id": target_room_id},
        )
