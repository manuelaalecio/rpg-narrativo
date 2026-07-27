from dataclasses import dataclass


@dataclass
class QuestStarted:
    """Event published when a quest is accepted."""

    quest_id: str
    npc_id: str
