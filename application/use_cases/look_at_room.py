from application.ports.repositories.content_repository_port import ContentRepositoryPort
from application.use_cases.use_case_result import UseCaseResult
from domain.entities.player import Player


class LookAtRoomUseCase:
    """Retrieve information about the player's current room."""

    def __init__(self, content_repository: ContentRepositoryPort) -> None:
        self._content_repository = content_repository

    def execute(self, player: Player) -> UseCaseResult:
        """Return the current room's details."""
        game_map = self._content_repository.get_map()
        room = game_map.get_room(player.current_room_id)

        return UseCaseResult(
            success=True,
            message=room.description,
            data={
                "room_id": room.id,
                "name": room.name,
                "description": room.description,
                "exits": list(room.exits.keys()),
                "item_ids": room.item_ids,
                "npc_ids": room.npc_ids,
            },
        )
