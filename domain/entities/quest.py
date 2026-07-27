from dataclasses import dataclass, field

from domain.value_objects.quest_status import QuestStatus


@dataclass
class Quest:
    """A quest/mission in the game.

    Quests are given by NPCs and have prerequisites, objectives, and rewards.
    The status tracks whether the quest is available, active, or completed.
    """

    id: str
    name: str
    description: str
    npc_giver_id: str
    required_item_ids: list[str] = field(default_factory=list)
    required_quest_ids: list[str] = field(default_factory=list)
    reward_item_ids: list[str] = field(default_factory=list)
    completion_dialogue_id: str | None = None
    status: QuestStatus = QuestStatus.AVAILABLE

    def can_accept(self, player_inventory, completed_quest_ids: set[str]) -> bool:
        """Check if the quest can be accepted based on prerequisites."""
        if self.status != QuestStatus.AVAILABLE:
            return False

        for item_id in self.required_item_ids:
            if not player_inventory.has_item(item_id):
                return False

        for quest_id in self.required_quest_ids:
            if quest_id not in completed_quest_ids:
                return False

        return True

    def accept(self) -> None:
        """Mark the quest as active."""
        self.status = QuestStatus.ACTIVE

    def can_complete(self, player_inventory) -> bool:
        """Check if the quest objectives are met (simplified: quest is active)."""
        return True

    def complete(self) -> None:
        """Mark the quest as completed."""
        self.status = QuestStatus.COMPLETED

    def is_completed(self) -> bool:
        """Check if the quest is completed."""
        return self.status == QuestStatus.COMPLETED
