"""Use case for saving the current game state."""

from datetime import datetime

from application.ports.event_bus.event_bus_port import EventBusPort
from application.ports.repositories.save_game_repository_port import (
    SaveGameRepositoryPort,
)
from application.use_cases.use_case_result import UseCaseResult
from domain.entities.player import Player
from domain.entities.save_game import SaveGame
from domain.events.game_saved import GameSaved


class SaveGameUseCase:
    """Save the current game state to a slot."""

    def __init__(
        self,
        save_repository: SaveGameRepositoryPort,
        event_bus: EventBusPort,
    ) -> None:
        self._save_repository = save_repository
        self._event_bus = event_bus

    def execute(self, player: Player, slot: str, save_name: str | None = None) -> UseCaseResult:
        """Execute the save game use case.

        Args:
            player: The current player whose state will be saved
            slot: The slot identifier to save to
            save_name: Optional display name for the save (defaults to player name + timestamp)

        Returns:
            UseCaseResult with success status and message
        """
        try:
            # Generate save name if not provided
            if save_name is None:
                timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                save_name = f"{player.name} - {timestamp_str}"

            # Build SaveGame from current player state
            save_game = SaveGame(
                save_id=slot,
                save_name=save_name,
                timestamp=datetime.now(),
                player_id=player.id,
                player_name=player.name,
                current_room_id=player.current_room_id,
                health=player.health,
                max_health=player.max_health,
                inventory=dict(player.inventory._items),  # Copy inventory
            )

            # Persist the save
            self._save_repository.save(save_game, slot)

            # Publish event
            event = GameSaved(save_id=save_game.save_id, slot=slot)
            self._event_bus.publish(event)

            return UseCaseResult(
                success=True,
                message=f"Game saved to slot '{slot}'",
                data={"slot": slot, "save_name": save_name},
            )

        except Exception as e:
            return UseCaseResult(
                success=False,
                message=f"Failed to save game: {e}",
            )
