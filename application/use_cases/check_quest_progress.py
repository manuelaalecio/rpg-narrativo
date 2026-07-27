from application.ports.repositories.content_repository_port import ContentRepositoryPort
from application.ports.repositories.quest_repository_port import QuestRepositoryPort
from application.use_cases.use_case_result import UseCaseResult
from domain.entities.player import Player
from domain.value_objects.quest_status import QuestStatus


class CheckQuestProgressUseCase:
    """Check which active quests can be completed based on current player state."""

    def __init__(
        self,
        content_repository: ContentRepositoryPort,
        quest_repository: QuestRepositoryPort,
    ) -> None:
        self._content_repository = content_repository
        self._quest_repository = quest_repository

    def execute(self, player: Player) -> UseCaseResult:
        """Check all active quests and return which ones can be completed.

        Returns a list of quest ids that are ready for completion.
        """
        active_quest_ids = self._quest_repository.get_active_quest_ids()
        completable_quests = []

        for quest_id in active_quest_ids:
            try:
                quest = self._content_repository.get_quest(quest_id)
                current_status = self._quest_repository.get_quest_status(quest_id)
                if current_status == QuestStatus.ACTIVE and quest.can_complete(player.inventory):
                    completable_quests.append(
                        {
                            "quest_id": quest_id,
                            "quest_name": quest.name,
                            "status": QuestStatus.ACTIVE.value,
                        }
                    )
            except KeyError:
                continue

        return UseCaseResult(
            success=True,
            message=f"{len(completable_quests)} quest(s) ready for completion.",
            data={"completable_quests": completable_quests},
        )
