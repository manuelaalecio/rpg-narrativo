from dataclasses import dataclass


@dataclass
class QuestCompleted:
    """Event published when a quest is completed."""

    quest_id: str
    npc_id: str
