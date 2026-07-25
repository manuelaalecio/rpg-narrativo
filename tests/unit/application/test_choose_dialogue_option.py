import pytest

from application.use_cases.choose_dialogue_option import ChooseDialogueOptionUseCase
from domain.entities.dialogue import Dialogue, DialogueNode, DialogueOption
from domain.entities.player import Player
from domain.events.dialogue_ended import DialogueEnded
from tests.fixtures.fake_event_bus import FakeEventBus


@pytest.fixture
def dialogue() -> Dialogue:
    d = Dialogue(
        id="dlg_01",
        start_node_id="node_01",
        nodes={
            "node_01": DialogueNode(
                id="node_01",
                npc_text="Hello!",
                options=[
                    DialogueOption(text="Hi!", next_node_id="node_02"),
                    DialogueOption(text="Bye.", next_node_id=None),
                ],
            ),
            "node_02": DialogueNode(
                id="node_02",
                npc_text="Nice to meet you.",
                options=[DialogueOption(text="Bye.", next_node_id=None)],
            ),
        },
    )
    d.start()
    return d


@pytest.fixture
def event_bus() -> FakeEventBus:
    return FakeEventBus()


@pytest.fixture
def use_case(event_bus: FakeEventBus) -> ChooseDialogueOptionUseCase:
    return ChooseDialogueOptionUseCase(event_bus)


class TestChooseDialogueOptionUseCase:
    def test_continue_dialogue(self, use_case: ChooseDialogueOptionUseCase, dialogue: Dialogue) -> None:
        player = Player(id="p1", name="Hero", current_room_id="room_01")
        result = use_case.execute(dialogue, 0, player, "npc_01")

        assert result.success is True
        assert result.data is not None
        assert result.data["ended"] is False
        assert result.data["npc_text"] == "Nice to meet you."

    def test_end_dialogue(
        self, use_case: ChooseDialogueOptionUseCase, dialogue: Dialogue, event_bus: FakeEventBus
    ) -> None:
        player = Player(id="p1", name="Hero", current_room_id="room_01")
        result = use_case.execute(dialogue, 1, player, "npc_01")

        assert result.success is True
        assert result.data is not None
        assert result.data["ended"] is True
        event_bus.assert_event_published(DialogueEnded)

    def test_invalid_option(self, use_case: ChooseDialogueOptionUseCase, dialogue: Dialogue) -> None:
        player = Player(id="p1", name="Hero", current_room_id="room_01")
        result = use_case.execute(dialogue, 99, player, "npc_01")

        assert result.success is False

    def test_ended_dialogue(self, use_case: ChooseDialogueOptionUseCase, dialogue: Dialogue) -> None:
        player = Player(id="p1", name="Hero", current_room_id="room_01")
        use_case.execute(dialogue, 1, player, "npc_01")
        result = use_case.execute(dialogue, 0, player, "npc_01")

        assert result.success is False
