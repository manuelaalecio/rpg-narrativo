from application.ports.event_bus.event_bus_port import EventBusPort
from application.ports.repositories.content_repository_port import ContentRepositoryPort
from application.ports.repositories.quest_repository_port import QuestRepositoryPort
from application.use_cases.use_case_result import UseCaseResult
from domain.entities.player import Player
from domain.events.quest_completed import QuestCompleted
from domain.value_objects.quest_status import QuestStatus


class CompleteQuestUseCase:
    """Complete an active quest and grant rewards."""

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
        """Attempt to complete the specified quest.

        Returns success if the quest is active and objectives are met.
        """
        try:
            quest = self._content_repository.get_quest(quest_id)
        except KeyError:
            return UseCaseResult(
                success=False,
                message=f"Quest '{quest_id}' not found.",
            )

        current_status = self._quest_repository.get_quest_status(quest_id)
        if current_status != QuestStatus.ACTIVE:
            return UseCaseResult(
                success=False,
                message=f"Quest '{quest.name}' is not active.",
            )

        if not quest.can_complete(player.inventory):
            return UseCaseResult(
                success=False,
                message=f"Quest objectives not met for '{quest.name}'.",
            )

        self._quest_repository.set_quest_status(quest_id, QuestStatus.COMPLETED)

        for item_id in quest.reward_item_ids:
            player.inventory.add_item(item_id)

        self._event_bus.publish(QuestCompleted(quest_id=quest_id, npc_id=quest.npc_giver_id))

        return UseCaseResult(
            success=True,
            message=f"Quest completed: {quest.name}",
            data={
                "quest_id": quest_id,
                "quest_name": quest.name,
                "rewards": quest.reward_item_ids,
            },
        )
