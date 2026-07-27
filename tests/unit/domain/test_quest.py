import pytest

from domain.entities.player import Player
from domain.entities.quest import Quest
from domain.value_objects.quest_status import QuestStatus


@pytest.fixture
def player() -> Player:
    return Player(id="p1", name="Hero", current_room_id="room_01")


@pytest.fixture
def player_with_key() -> Player:
    player = Player(id="p1", name="Hero", current_room_id="room_01")
    player.inventory.add_item("item_old_key")
    return player


@pytest.fixture
def simple_quest() -> Quest:
    return Quest(
        id="quest_01",
        name="Simple Quest",
        description="A simple quest.",
        npc_giver_id="npc_01",
    )


@pytest.fixture
def quest_with_item_requirement() -> Quest:
    return Quest(
        id="quest_02",
        name="Key Quest",
        description="Requires the old key.",
        npc_giver_id="npc_01",
        required_item_ids=["item_old_key"],
    )


@pytest.fixture
def quest_with_quest_requirement() -> Quest:
    return Quest(
        id="quest_03",
        name="Follow-up Quest",
        description="Requires quest_01 to be completed.",
        npc_giver_id="npc_01",
        required_quest_ids=["quest_01"],
    )


@pytest.fixture
def quest_with_rewards() -> Quest:
    return Quest(
        id="quest_04",
        name="Reward Quest",
        description="Gives a reward.",
        npc_giver_id="npc_01",
        reward_item_ids=["item_reward_01", "item_reward_02"],
    )


class TestQuest:
    def test_create_quest(self, simple_quest: Quest) -> None:
        assert simple_quest.id == "quest_01"
        assert simple_quest.name == "Simple Quest"
        assert simple_quest.status == QuestStatus.AVAILABLE

    def test_default_status_is_available(self, simple_quest: Quest) -> None:
        assert simple_quest.status == QuestStatus.AVAILABLE

    def test_can_accept_simple_quest(self, simple_quest: Quest, player: Player) -> None:
        assert simple_quest.can_accept(player.inventory, set()) is True

    def test_can_accept_quest_with_item_requirement(
        self, quest_with_item_requirement: Quest, player: Player, player_with_key: Player
    ) -> None:
        assert quest_with_item_requirement.can_accept(player.inventory, set()) is False
        assert quest_with_item_requirement.can_accept(player_with_key.inventory, set()) is True

    def test_can_accept_quest_with_quest_requirement(self, quest_with_quest_requirement: Quest, player: Player) -> None:
        assert quest_with_quest_requirement.can_accept(player.inventory, set()) is False
        assert quest_with_quest_requirement.can_accept(player.inventory, {"quest_01"}) is True

    def test_cannot_accept_if_not_available(self, simple_quest: Quest, player: Player) -> None:
        simple_quest.accept()
        assert simple_quest.can_accept(player.inventory, set()) is False

    def test_accept_changes_status(self, simple_quest: Quest) -> None:
        simple_quest.accept()
        assert simple_quest.status == QuestStatus.ACTIVE

    def test_can_complete_active_quest(self, simple_quest: Quest, player: Player) -> None:
        simple_quest.accept()
        assert simple_quest.can_complete(player.inventory) is True

    def test_can_complete_returns_true_regardless_of_status(self, simple_quest: Quest, player: Player) -> None:
        # Status check is done in use case, not in entity
        assert simple_quest.can_complete(player.inventory) is True

    def test_complete_changes_status(self, simple_quest: Quest) -> None:
        simple_quest.accept()
        simple_quest.complete()
        assert simple_quest.status == QuestStatus.COMPLETED

    def test_is_completed(self, simple_quest: Quest) -> None:
        assert simple_quest.is_completed() is False
        simple_quest.accept()
        assert simple_quest.is_completed() is False
        simple_quest.complete()
        assert simple_quest.is_completed() is True

    def test_quest_with_rewards(self, quest_with_rewards: Quest) -> None:
        assert quest_with_rewards.reward_item_ids == ["item_reward_01", "item_reward_02"]

    def test_quest_with_completion_dialogue(self) -> None:
        quest = Quest(
            id="quest_05",
            name="Dialogue Quest",
            description="Has a completion dialogue.",
            npc_giver_id="npc_01",
            completion_dialogue_id="dialogue_complete",
        )
        assert quest.completion_dialogue_id == "dialogue_complete"


class TestQuestStatus:
    def test_status_values(self) -> None:
        assert QuestStatus.AVAILABLE.value == "available"
        assert QuestStatus.ACTIVE.value == "active"
        assert QuestStatus.COMPLETED.value == "completed"
