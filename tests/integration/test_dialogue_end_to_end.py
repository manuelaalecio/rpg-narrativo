"""End-to-end integration test for the dialogue system using real JsonContentRepository."""

from pathlib import Path

from application.use_cases.choose_dialogue_option import ChooseDialogueOptionUseCase
from application.use_cases.move_to_room import MoveToRoomUseCase
from application.use_cases.pick_up_item import PickUpItemUseCase
from application.use_cases.start_dialogue import StartDialogueUseCase
from domain.entities.player import Player
from domain.events.dialogue_ended import DialogueEnded
from domain.events.dialogue_started import DialogueStarted
from infrastructure.content_loader.json_content_repository import JsonContentRepository
from infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus

DATA_PATH = Path(__file__).parent.parent.parent / "data"


class TestDialogueEndToEnd:
    def test_dialogue_without_item(self) -> None:
        content_repo = JsonContentRepository(DATA_PATH)
        event_bus = InMemoryEventBus()

        published_events: list = []
        event_bus.subscribe(DialogueStarted, lambda e: published_events.append(e))
        event_bus.subscribe(DialogueEnded, lambda e: published_events.append(e))

        start_uc = StartDialogueUseCase(content_repo, event_bus)
        choose_uc = ChooseDialogueOptionUseCase(event_bus)

        player = Player(id="p1", name="Hero", current_room_id="room_02")

        result = start_uc.execute(player, "npc_tavern_keeper")
        assert result.success is True
        assert result.data is not None
        dialogue = result.data["dialogue"]
        assert result.data["npc_name"] == "Tavern Keeper"

        available = dialogue.get_available_options(player)
        option_texts = [opt.text for _, opt in available]
        assert "Just passing through. Nice place you have here." in option_texts
        assert "Goodbye." in option_texts
        assert "I found this old key. Do you know anything about it?" not in option_texts

        goodbye_original_idx = next(orig_idx for orig_idx, opt in available if opt.text == "Goodbye.")
        result = choose_uc.execute(dialogue, goodbye_original_idx, player, "npc_tavern_keeper")
        assert result.success is True
        assert result.data is not None
        assert result.data["ended"] is True

        assert len(published_events) == 2
        assert isinstance(published_events[0], DialogueStarted)
        assert isinstance(published_events[1], DialogueEnded)

    def test_dialogue_with_item(self) -> None:
        content_repo = JsonContentRepository(DATA_PATH)
        event_bus = InMemoryEventBus()

        start_uc = StartDialogueUseCase(content_repo, event_bus)
        choose_uc = ChooseDialogueOptionUseCase(event_bus)
        pick_up_uc = PickUpItemUseCase(content_repo, event_bus)
        move_uc = MoveToRoomUseCase(content_repo, event_bus)

        player = Player(id="p1", name="Hero", current_room_id="room_01")

        pick_result = pick_up_uc.execute(player, "item_old_key")
        assert pick_result.success is True
        assert player.inventory.has_item("item_old_key")

        move_result = move_uc.execute(player, "north")
        assert move_result.success is True
        assert player.current_room_id == "room_02"

        result = start_uc.execute(player, "npc_tavern_keeper")
        assert result.success is True
        dialogue = result.data["dialogue"]

        available = dialogue.get_available_options(player)
        option_texts = [opt.text for _, opt in available]
        assert "I found this old key. Do you know anything about it?" in option_texts

        key_original_idx = next(orig_idx for orig_idx, opt in available if "key" in opt.text.lower())
        result = choose_uc.execute(dialogue, key_original_idx, player, "npc_tavern_keeper")
        assert result.success is True
        assert result.data is not None
        assert result.data["ended"] is False
        assert "cellar" in result.data["npc_text"].lower()
