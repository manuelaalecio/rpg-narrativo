from dataclasses import dataclass


@dataclass
class DialogueEnded:
    """Event published when a dialogue concludes."""

    npc_id: str
    dialogue_id: str
