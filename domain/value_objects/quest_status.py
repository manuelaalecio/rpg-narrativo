from enum import Enum


class QuestStatus(Enum):
    """Possible states for a quest."""

    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
