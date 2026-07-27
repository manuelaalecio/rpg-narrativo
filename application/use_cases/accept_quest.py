from application.ports.event_bus.event_bus_port import EventBusPort
from application.ports.repositories.content_repository_port import ContentRepositoryPort
from application.ports.repositories.quest_repository_port import QuestRepositoryPort
from application.use_cases.use_case_result import UseCaseResult
from domain.entities.player import Player
from domain.events.quest_started import QuestStarted
from domain.value_objects.quest_status import QuestStatus


class AcceptQuestUseCase:
    """Accept a quest from an NPC."""

    def __init__(
        self,
        content_repository: ContentRepositoryPort,
        quest_repository: QuestRepositoryPort,
        event_bus: EventBusPort,
    ) -> None:
        self._content_repository = content_repository
        self._quest_repository = quest_repository
        self._event_bus = event_bus

    def execute(self, player: Player, quest_id: str) -> UseCaseResult:
        """Attempt to accept the specified quest.

        Returns success if prerequisites are met, failure otherwise.
        """
        try:
            quest = self._content_repository.get_quest(quest_id)
        except KeyError:
            return UseCaseResult(
                success=False,
                message=f"Quest '{quest_id}' not found.",
            )

        current_status = self._quest_repository.get_quest_status(quest_id)
        if current_status != QuestStatus.AVAILABLE:
            return UseCaseResult(
                success=False,
                message=f"Quest '{quest.name}' is not available.",
            )

        completed_quest_ids = self._quest_repository.get_completed_quest_ids()
        if not quest.can_accept(player.inventory, completed_quest_ids):
            return UseCaseResult(
                success=False,
                message=f"You don't meet the requirements for '{quest.name}'.",
            )

        quest.accept()
        self._quest_repository.set_quest_status(quest_id, QuestStatus.ACTIVE)

        self._event_bus.publish(QuestStarted(quest_id=quest_id, npc_id=quest.npc_giver_id))

        return UseCaseResult(
            success=True,
            message=f"Quest accepted: {quest.name}",
            data={"quest_id": quest_id, "quest_name": quest.name},
        )
