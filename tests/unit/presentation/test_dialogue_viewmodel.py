import pytest
from PySide6.QtWidgets import QApplication

from application.use_cases.choose_dialogue_option import ChooseDialogueOptionUseCase
from application.use_cases.start_dialogue import StartDialogueUseCase
from domain.entities.dialogue import Condition, Dialogue, DialogueNode, DialogueOption
from domain.entities.map import GameMap
from domain.entities.npc import NPC
from domain.entities.player import Player
from presentation.viewmodels.dialogue_viewmodel import DialogueViewModel
from tests.fixtures.fake_content_repository import FakeContentRepository
from tests.fixtures.fake_event_bus import FakeEventBus


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def dialogue() -> Dialogue:
    return Dialogue(
        id="dlg_01",
        start_node_id="node_01",
        nodes={
            "node_01": DialogueNode(
                id="node_01",
                npc_text="Hello!",
                options=[
                    DialogueOption(text="Hi!", next_node_id="node_02"),
                    DialogueOption(
                        text="Show key.",
                        next_node_id="node_03",
                        condition=Condition(condition_type="requires_item", value="item_key"),
                    ),
                    DialogueOption(text="Bye.", next_node_id=None),
                ],
            ),
            "node_02": DialogueNode(
                id="node_02",
                npc_text="Nice to meet you.",
                options=[DialogueOption(text="Bye.", next_node_id=None)],
            ),
            "node_03": DialogueNode(
                id="node_03",
                npc_text="The key! Here's a secret.",
                options=[DialogueOption(text="Thanks!", next_node_id=None)],
            ),
        },
    )


@pytest.fixture
def player() -> Player:
    return Player(id="p1", name="Hero", current_room_id="room_01")


@pytest.fixture
def view_model(qapp: QApplication, dialogue: Dialogue, player: Player) -> DialogueViewModel:
    npc = NPC(id="npc_01", name="Guard", description="A guard.", dialogue_id="dlg_01")
    content_repo = FakeContentRepository(
        game_map=GameMap(),
        npcs={"npc_01": npc},
        dialogues={"dlg_01": dialogue},
    )
    event_bus = FakeEventBus()
    start_uc = StartDialogueUseCase(content_repo, event_bus)
    choose_uc = ChooseDialogueOptionUseCase(event_bus)
    return DialogueViewModel(player, start_uc, choose_uc)


class TestDialogueViewModel:
    def test_start_dialogue(self, view_model: DialogueViewModel) -> None:
        view_model.start_dialogue("npc_01")

        assert view_model.is_active is True
        assert view_model.npc_name == "Guard"
        assert view_model.npc_text == "Hello!"
        assert len(view_model.available_options) == 2

    def test_choose_option_continues(self, view_model: DialogueViewModel) -> None:
        view_model.start_dialogue("npc_01")
        view_model.choose_option(0)

        assert view_model.npc_text == "Nice to meet you."
        assert len(view_model.available_options) == 1

    def test_choose_option_ends(self, view_model: DialogueViewModel) -> None:
        view_model.start_dialogue("npc_01")
        view_model.choose_option(1)

        assert view_model.is_active is False

    def test_conditional_option_hidden_without_item(self, view_model: DialogueViewModel) -> None:
        view_model.start_dialogue("npc_01")
        assert "Show key." not in view_model.available_options

    def test_conditional_option_visible_with_item(self, qapp: QApplication, dialogue: Dialogue) -> None:
        player = Player(id="p1", name="Hero", current_room_id="room_01")
        player.inventory.add_item("item_key")
        npc = NPC(id="npc_01", name="Guard", description="A guard.", dialogue_id="dlg_01")
        content_repo = FakeContentRepository(
            game_map=GameMap(),
            npcs={"npc_01": npc},
            dialogues={"dlg_01": dialogue},
        )
        event_bus = FakeEventBus()
        start_uc = StartDialogueUseCase(content_repo, event_bus)
        choose_uc = ChooseDialogueOptionUseCase(event_bus)
        vm = DialogueViewModel(player, start_uc, choose_uc)

        vm.start_dialogue("npc_01")
        assert "Show key." in vm.available_options

    def test_start_nonexistent_npc(self, view_model: DialogueViewModel) -> None:
        view_model.start_dialogue("nonexistent")
        assert view_model.is_active is False
