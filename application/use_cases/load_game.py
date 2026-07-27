"""Use case for loading a saved game."""

from application.ports.event_bus.event_bus_port import EventBusPort
from application.ports.repositories.quest_repository_port import QuestRepositoryPort
from application.ports.repositories.save_game_repository_port import (
    SaveGameRepositoryPort,
)
from application.use_cases.use_case_result import UseCaseResult
from domain.entities.inventory import Inventory
from domain.entities.player import Player
from domain.events.game_loaded import GameLoaded
from domain.value_objects.quest_status import QuestStatus
from infrastructure.exceptions import SaveCorruptedError, SaveNotFoundError


class LoadGameUseCase:
    """Load a saved game from a slot and reconstruct the Player."""

    def __init__(
        self,
        save_repository: SaveGameRepositoryPort,
        quest_repository: QuestRepositoryPort,
        event_bus: EventBusPort,
    ) -> None:
        self._save_repository = save_repository
        self._quest_repository = quest_repository
        self._event_bus = event_bus

    def execute(self, slot: str) -> UseCaseResult:
        """Execute the load game use case.

        Args:
            slot: The slot identifier to load from

        Returns:
            UseCaseResult with success status, message, and reconstructed Player in data
        """
        try:
            # Load the save game
            save_game = self._save_repository.load(slot)

            # Reconstruct Inventory
            inventory = Inventory()
            for item_id, quantity in save_game.inventory.items():
                inventory.add_item(item_id, quantity)

            # Reconstruct Player
            player = Player(
                id=save_game.player_id,
                name=save_game.player_name,
                current_room_id=save_game.current_room_id,
                inventory=inventory,
                health=save_game.health,
                max_health=save_game.max_health,
            )

            # Restore quest statuses
            for quest_id, status_value in save_game.quest_statuses.items():
                status = QuestStatus(status_value)
                self._quest_repository.set_quest_status(quest_id, status)

            # Publish event
            event = GameLoaded(save_id=save_game.save_id, slot=slot)
            self._event_bus.publish(event)

            return UseCaseResult(
                success=True,
                message=f"Game loaded from slot '{slot}'",
                data={"player": player, "save_name": save_game.save_name},
            )

        except SaveNotFoundError:
            return UseCaseResult(
                success=False,
                message=f"Save slot '{slot}' not found",
            )
        except SaveCorruptedError as e:
            return UseCaseResult(
                success=False,
                message=f"Save slot '{slot}' is corrupted: {e.reason}",
            )
        except Exception as e:
            return UseCaseResult(
                success=False,
                message=f"Failed to load game: {e}",
            )
