from typing import Protocol

from domain.value_objects.quest_status import QuestStatus


class QuestRepositoryPort(Protocol):
    """Interface for quest state persistence.

    Quest definitions come from ContentRepositoryPort (loaded from JSON).
    This repository tracks quest status changes during gameplay.
    """

    def get_quest_status(self, quest_id: str) -> QuestStatus:
        """Return the current status of a quest.

        Returns AVAILABLE if the quest has not been started.
        """
        ...

    def set_quest_status(self, quest_id: str, status: QuestStatus) -> None:
        """Update the status of a quest."""
        ...

    def get_completed_quest_ids(self) -> set[str]:
        """Return the set of all completed quest ids."""
        ...

    def get_active_quest_ids(self) -> set[str]:
        """Return the set of all active quest ids."""
        ...
