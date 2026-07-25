import pytest

from domain.entities.dialogue import Condition, Dialogue, DialogueNode, DialogueOption
from domain.entities.player import Player


@pytest.fixture
def player() -> Player:
    return Player(id="p1", name="Hero", current_room_id="room_01")


@pytest.fixture
def player_with_key() -> Player:
    player = Player(id="p1", name="Hero", current_room_id="room_01")
    player.inventory.add_item("item_old_key")
    return player


@pytest.fixture
def dialogue() -> Dialogue:
    return Dialogue(
        id="dlg_01",
        start_node_id="node_01",
        nodes={
            "node_01": DialogueNode(
                id="node_01",
                npc_text="Hello there!",
                options=[
                    DialogueOption(text="Hi!", next_node_id="node_02"),
                    DialogueOption(
                        text="Show me the key.",
                        next_node_id="node_03",
                        condition=Condition(condition_type="requires_item", value="item_old_key"),
                    ),
                    DialogueOption(text="Goodbye.", next_node_id=None),
                ],
            ),
            "node_02": DialogueNode(
                id="node_02",
                npc_text="Nice to meet you.",
                options=[DialogueOption(text="Bye.", next_node_id=None)],
            ),
            "node_03": DialogueNode(
                id="node_03",
                npc_text="Ah, the key! Here's a secret.",
                options=[DialogueOption(text="Thanks!", next_node_id=None)],
            ),
        },
    )


class TestDialogue:
    def test_start_sets_current_node(self, dialogue: Dialogue) -> None:
        dialogue.start()
        node = dialogue.get_current_node()
        assert node is not None
        assert node.id == "node_01"
        assert node.npc_text == "Hello there!"

    def test_get_available_options_without_item(self, dialogue: Dialogue, player: Player) -> None:
        dialogue.start()
        available = dialogue.get_available_options(player)
        assert len(available) == 2
        assert available[0][1].text == "Hi!"
        assert available[1][1].text == "Goodbye."

    def test_get_available_options_with_item(self, dialogue: Dialogue, player_with_key: Player) -> None:
        dialogue.start()
        available = dialogue.get_available_options(player_with_key)
        assert len(available) == 3
        assert available[1][1].text == "Show me the key."

    def test_choose_option_advances_node(self, dialogue: Dialogue, player: Player) -> None:
        dialogue.start()
        continues = dialogue.choose_option(0)
        assert continues is True
        node = dialogue.get_current_node()
        assert node is not None
        assert node.id == "node_02"

    def test_choose_option_ends_dialogue(self, dialogue: Dialogue, player: Player) -> None:
        dialogue.start()
        continues = dialogue.choose_option(2)
        assert continues is False
        assert dialogue.is_ended is True
        assert dialogue.get_current_node() is None

    def test_choose_conditional_option(self, dialogue: Dialogue, player_with_key: Player) -> None:
        dialogue.start()
        continues = dialogue.choose_option(1)
        assert continues is True
        node = dialogue.get_current_node()
        assert node is not None
        assert node.id == "node_03"

    def test_get_current_node_before_start(self, dialogue: Dialogue) -> None:
        assert dialogue.get_current_node() is None

    def test_is_ended_initially_false(self, dialogue: Dialogue) -> None:
        assert dialogue.is_ended is False

    def test_choose_invalid_index(self, dialogue: Dialogue) -> None:
        dialogue.start()
        result = dialogue.choose_option(99)
        assert result is False
