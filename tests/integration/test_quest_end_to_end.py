"""End-to-end integration test for the quest system using real JsonContentRepository."""

from pathlib import Path

import pytest

from application.use_cases.accept_quest import AcceptQuestUseCase
from application.use_cases.check_quest_progress import CheckQuestProgressUseCase
from application.use_cases.complete_quest import CompleteQuestUseCase
from domain.entities.player import Player
from domain.entities.quest import Quest
from domain.events.quest_completed import QuestCompleted
from domain.events.quest_started import QuestStarted
from domain.value_objects.quest_status import QuestStatus
from infrastructure.content_loader.json_content_repository import JsonContentRepository
from infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus
from tests.fixtures.fake_quest_repository import FakeQuestRepository

DATA_PATH = Path(__file__).parent.parent.parent / "data"


@pytest.fixture
def content_repo() -> JsonContentRepository:
    return JsonContentRepository(DATA_PATH)


@pytest.fixture
def quest_repo() -> FakeQuestRepository:
    return FakeQuestRepository()


@pytest.fixture
def event_bus() -> InMemoryEventBus:
    return InMemoryEventBus()


@pytest.fixture
def player() -> Player:
    return Player(id="p1", name="Hero", current_room_id="room_01")


class TestQuestEndToEnd:
    def test_accept_quest_success(
        self,
        content_repo: JsonContentRepository,
        quest_repo: FakeQuestRepository,
        event_bus: InMemoryEventBus,
        player: Player,
    ) -> None:
        published_events: list = []
        event_bus.subscribe(QuestStarted, lambda e: published_events.append(e))

        accept_uc = AcceptQuestUseCase(content_repo, quest_repo, event_bus)

        quest = Quest(
            id="test_quest_01",
            name="Test Quest",
            description="A test quest.",
            npc_giver_id="npc_tavern_keeper",
        )
        content_repo._quests["test_quest_01"] = quest

        result = accept_uc.execute(player, "test_quest_01")

        assert result.success is True
        assert result.data is not None
        assert result.data["quest_id"] == "test_quest_01"
        assert quest_repo.get_quest_status("test_quest_01") == QuestStatus.ACTIVE
        assert len(published_events) == 1
        assert isinstance(published_events[0], QuestStarted)

    def test_accept_quest_not_found(
        self,
        content_repo: JsonContentRepository,
        quest_repo: FakeQuestRepository,
        event_bus: InMemoryEventBus,
        player: Player,
    ) -> None:
        accept_uc = AcceptQuestUseCase(content_repo, quest_repo, event_bus)

        result = accept_uc.execute(player, "nonexistent_quest")

        assert result.success is False
        assert "not found" in result.message

    def test_accept_quest_already_active(
        self,
        content_repo: JsonContentRepository,
        quest_repo: FakeQuestRepository,
        event_bus: InMemoryEventBus,
        player: Player,
    ) -> None:
        accept_uc = AcceptQuestUseCase(content_repo, quest_repo, event_bus)

        quest = Quest(
            id="test_quest_02",
            name="Test Quest 2",
            description="Another test quest.",
            npc_giver_id="npc_tavern_keeper",
        )
        content_repo._quests["test_quest_02"] = quest
        quest_repo.set_quest_status("test_quest_02", QuestStatus.ACTIVE)

        result = accept_uc.execute(player, "test_quest_02")

        assert result.success is False
        assert "not available" in result.message

    def test_complete_quest_success(
        self,
        content_repo: JsonContentRepository,
        quest_repo: FakeQuestRepository,
        event_bus: InMemoryEventBus,
        player: Player,
    ) -> None:
        published_events: list = []
        event_bus.subscribe(QuestCompleted, lambda e: published_events.append(e))

        complete_uc = CompleteQuestUseCase(content_repo, quest_repo, event_bus)

        quest = Quest(
            id="test_quest_03",
            name="Test Quest 3",
            description="A completable quest.",
            npc_giver_id="npc_tavern_keeper",
            reward_item_ids=["item_reward_01"],
        )
        content_repo._quests["test_quest_03"] = quest
        quest_repo.set_quest_status("test_quest_03", QuestStatus.ACTIVE)

        result = complete_uc.execute(player, "test_quest_03")

        assert result.success is True
        assert result.data is not None
        assert result.data["quest_id"] == "test_quest_03"
        assert result.data["rewards"] == ["item_reward_01"]
        assert quest_repo.get_quest_status("test_quest_03") == QuestStatus.COMPLETED
        assert player.inventory.has_item("item_reward_01")
        assert len(published_events) == 1
        assert isinstance(published_events[0], QuestCompleted)

    def test_complete_quest_not_active(
        self,
        content_repo: JsonContentRepository,
        quest_repo: FakeQuestRepository,
        event_bus: InMemoryEventBus,
        player: Player,
    ) -> None:
        complete_uc = CompleteQuestUseCase(content_repo, quest_repo, event_bus)

        quest = Quest(
            id="test_quest_04",
            name="Test Quest 4",
            description="Not active yet.",
            npc_giver_id="npc_tavern_keeper",
        )
        content_repo._quests["test_quest_04"] = quest

        result = complete_uc.execute(player, "test_quest_04")

        assert result.success is False
        assert "not active" in result.message

    def test_check_quest_progress(
        self, content_repo: JsonContentRepository, quest_repo: FakeQuestRepository, player: Player
    ) -> None:
        check_uc = CheckQuestProgressUseCase(content_repo, quest_repo)

        quest = Quest(
            id="test_quest_05",
            name="Test Quest 5",
            description="Active and completable.",
            npc_giver_id="npc_tavern_keeper",
        )
        content_repo._quests["test_quest_05"] = quest
        quest_repo.set_quest_status("test_quest_05", QuestStatus.ACTIVE)

        result = check_uc.execute(player)

        assert result.success is True
        assert result.data is not None
        completable = result.data["completable_quests"]
        assert len(completable) == 1
        assert completable[0]["quest_id"] == "test_quest_05"

    def test_quest_with_item_requirement(
        self,
        content_repo: JsonContentRepository,
        quest_repo: FakeQuestRepository,
        event_bus: InMemoryEventBus,
        player: Player,
    ) -> None:
        accept_uc = AcceptQuestUseCase(content_repo, quest_repo, event_bus)

        quest = Quest(
            id="test_quest_06",
            name="Key Quest",
            description="Requires item_old_key.",
            npc_giver_id="npc_tavern_keeper",
            required_item_ids=["item_old_key"],
        )
        content_repo._quests["test_quest_06"] = quest

        result = accept_uc.execute(player, "test_quest_06")
        assert result.success is False
        assert "requirements" in result.message

        player.inventory.add_item("item_old_key")
        result = accept_uc.execute(player, "test_quest_06")
        assert result.success is True

    def test_quest_with_quest_requirement(
        self,
        content_repo: JsonContentRepository,
        quest_repo: FakeQuestRepository,
        event_bus: InMemoryEventBus,
        player: Player,
    ) -> None:
        accept_uc = AcceptQuestUseCase(content_repo, quest_repo, event_bus)

        quest = Quest(
            id="test_quest_07",
            name="Follow-up Quest",
            description="Requires test_quest_01 to be completed.",
            npc_giver_id="npc_tavern_keeper",
            required_quest_ids=["test_quest_01"],
        )
        content_repo._quests["test_quest_07"] = quest

        result = accept_uc.execute(player, "test_quest_07")
        assert result.success is False
        assert "requirements" in result.message

        quest_repo.set_quest_status("test_quest_01", QuestStatus.COMPLETED)
        result = accept_uc.execute(player, "test_quest_07")
        assert result.success is True
