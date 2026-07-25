from dataclasses import dataclass


@dataclass
class DialogueStarted:
    """Event published when a dialogue begins."""

    npc_id: str
    dialogue_id: str
