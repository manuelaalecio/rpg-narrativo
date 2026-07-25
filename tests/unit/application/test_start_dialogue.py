import pytest

from application.use_cases.start_dialogue import StartDialogueUseCase
from domain.entities.dialogue import Dialogue, DialogueNode, DialogueOption
from domain.entities.map import GameMap
from domain.entities.npc import NPC
from domain.events.dialogue_started import DialogueStarted
from tests.fixtures.fake_content_repository import FakeContentRepository
from tests.fixtures.fake_event_bus import FakeEventBus


@pytest.fixture
def dialogue() -> Dialogue:
    return Dialogue(
        id="dlg_01",
        start_node_id="node_01",
        nodes={
            "node_01": DialogueNode(
                id="node_01",
                npc_text="Hello!",
                options=[DialogueOption(text="Hi!", next_node_id=None)],
            ),
        },
    )


@pytest.fixture
def npc_with_dialogue() -> NPC:
    return NPC(id="npc_01", name="Guard", description="A guard.", dialogue_id="dlg_01")


@pytest.fixture
def npc_without_dialogue() -> NPC:
    return NPC(id="npc_02", name="Silent NPC", description="Says nothing.")


@pytest.fixture
def event_bus() -> FakeEventBus:
    return FakeEventBus()


@pytest.fixture
def use_case(
    npc_with_dialogue: NPC,
    npc_without_dialogue: NPC,
    dialogue: Dialogue,
    event_bus: FakeEventBus,
) -> StartDialogueUseCase:
    content_repo = FakeContentRepository(
        game_map=GameMap(),
        npcs={"npc_01": npc_with_dialogue, "npc_02": npc_without_dialogue},
        dialogues={"dlg_01": dialogue},
    )
    return StartDialogueUseCase(content_repo, event_bus)


class TestStartDialogueUseCase:
    def test_success(self, use_case: StartDialogueUseCase, event_bus: FakeEventBus) -> None:
        from domain.entities.player import Player

        player = Player(id="p1", name="Hero", current_room_id="room_01")
        result = use_case.execute(player, "npc_01")

        assert result.success is True
        assert result.data is not None
        assert result.data["npc_name"] == "Guard"
        assert result.data["dialogue"] is not None
        event_bus.assert_event_published(DialogueStarted)

    def test_npc_not_found(self, use_case: StartDialogueUseCase) -> None:
        from domain.entities.player import Player

        player = Player(id="p1", name="Hero", current_room_id="room_01")
        result = use_case.execute(player, "nonexistent")

        assert result.success is False

    def test_npc_without_dialogue(self, use_case: StartDialogueUseCase) -> None:
        from domain.entities.player import Player

        player = Player(id="p1", name="Hero", current_room_id="room_01")
        result = use_case.execute(player, "npc_02")

        assert result.success is False
