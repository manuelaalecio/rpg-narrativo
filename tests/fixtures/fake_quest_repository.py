from application.ports.repositories.quest_repository_port import QuestRepositoryPort
from domain.value_objects.quest_status import QuestStatus


class FakeQuestRepository:
    """In-memory fake quest repository for testing."""

    def __init__(self) -> None:
        self._statuses: dict[str, QuestStatus] = {}

    def get_quest_status(self, quest_id: str) -> QuestStatus:
        """Return the current status of a quest."""
        return self._statuses.get(quest_id, QuestStatus.AVAILABLE)

    def set_quest_status(self, quest_id: str, status: QuestStatus) -> None:
        """Update the status of a quest."""
        self._statuses[quest_id] = status

    def get_completed_quest_ids(self) -> set[str]:
        """Return the set of all completed quest ids."""
        return {quest_id for quest_id, status in self._statuses.items() if status == QuestStatus.COMPLETED}

    def get_active_quest_ids(self) -> set[str]:
        """Return the set of all active quest ids."""
        return {quest_id for quest_id, status in self._statuses.items() if status == QuestStatus.ACTIVE}


# Type assertion: FakeQuestRepository satisfies QuestRepositoryPort
_: QuestRepositoryPort = FakeQuestRepository()
