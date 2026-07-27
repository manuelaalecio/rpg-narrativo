"""Composition root: manual dependency injection wiring all layers together.

This is the ONLY place in the project where infrastructure/, application/,
domain/, presentation/, and ui/ can all be imported together — it's the
composition root that assembles the object graph before starting the app.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from application.use_cases.accept_quest import AcceptQuestUseCase
from application.use_cases.check_quest_progress import CheckQuestProgressUseCase
from application.use_cases.choose_dialogue_option import ChooseDialogueOptionUseCase
from application.use_cases.complete_quest import CompleteQuestUseCase
from application.use_cases.load_game import LoadGameUseCase
from application.use_cases.look_at_room import LookAtRoomUseCase
from application.use_cases.move_to_room import MoveToRoomUseCase
from application.use_cases.pick_up_item import PickUpItemUseCase
from application.use_cases.save_game import SaveGameUseCase
from application.use_cases.start_dialogue import StartDialogueUseCase
from application.use_cases.use_item import UseItemUseCase
from domain.entities.player import Player
from infrastructure.content_loader.json_content_repository import JsonContentRepository
from infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus
from infrastructure.persistence.in_memory_quest_repository import InMemoryQuestRepository
from infrastructure.persistence.json_save_game_repository import JsonSaveGameRepository
from presentation.state_machine.game_state import GameState
from presentation.state_machine.game_state_machine import GameStateMachine
from presentation.viewmodels.dialogue_viewmodel import DialogueViewModel
from presentation.viewmodels.exploration_viewmodel import ExplorationViewModel
from presentation.viewmodels.inventory_viewmodel import InventoryViewModel
from presentation.viewmodels.menu_viewmodel import MenuViewModel
from ui.screens.combat_screen import CombatScreen
from ui.screens.dialogue_screen import DialogueScreen
from ui.screens.exploration_screen import ExplorationScreen
from ui.screens.inventory_screen import InventoryScreen
from ui.screens.loading_screen import LoadingScreen
from ui.screens.main_menu_screen import MainMenuScreen
from ui.screens.pause_screen import PauseScreen
from ui.windows.main_window import MainWindow


def main() -> None:
    data_path = Path(__file__).parent / "data"
    save_path = Path(__file__).parent / "save"

    content_repo = JsonContentRepository(data_path)
    save_repo = JsonSaveGameRepository(save_path)
    quest_repo = InMemoryQuestRepository()
    event_bus = InMemoryEventBus()

    move_uc = MoveToRoomUseCase(content_repo, event_bus)
    look_uc = LookAtRoomUseCase(content_repo)
    pick_up_uc = PickUpItemUseCase(content_repo, event_bus)
    start_dialogue_uc = StartDialogueUseCase(content_repo, event_bus)
    choose_option_uc = ChooseDialogueOptionUseCase(event_bus)
    use_item_uc = UseItemUseCase(content_repo, event_bus)
    # Quest use cases (will be wired to UI in Phase 2)
    _accept_quest_uc = AcceptQuestUseCase(content_repo, quest_repo, event_bus)
    _complete_quest_uc = CompleteQuestUseCase(content_repo, quest_repo, event_bus)
    _check_quest_progress_uc = CheckQuestProgressUseCase(content_repo, quest_repo)
    save_game_uc = SaveGameUseCase(save_repo, quest_repo, event_bus)
    load_game_uc = LoadGameUseCase(save_repo, quest_repo, event_bus)

    game_map = content_repo.get_map()
    first_room_id = game_map.room_ids[0] if game_map.room_ids else "room_01"
    player = Player(id="player_01", name="Hero", current_room_id=first_room_id)

    exploration_vm = ExplorationViewModel(player, move_uc, look_uc, pick_up_uc)
    dialogue_vm = DialogueViewModel(player, start_dialogue_uc, choose_option_uc)
    inventory_vm = InventoryViewModel(player, use_item_uc, content_repo)
    menu_vm = MenuViewModel(save_repo, save_game_uc, load_game_uc)

    state_machine = GameStateMachine(initial_state=GameState.MAIN_MENU)

    app = QApplication(sys.argv)

    main_window = MainWindow(state_machine)

    # Create all screens
    main_menu_screen = MainMenuScreen(state_machine)
    loading_screen = LoadingScreen()
    exploration_screen = ExplorationScreen(exploration_vm, state_machine)
    dialogue_screen = DialogueScreen(dialogue_vm, state_machine)
    combat_screen = CombatScreen(state_machine)
    inventory_screen = InventoryScreen(inventory_vm, state_machine)
    pause_screen = PauseScreen(state_machine)

    # Wire NPC interaction
    def on_talk_to_npc(npc_id: str) -> None:
        dialogue_vm.start_dialogue(npc_id)
        state_machine.transition_to(GameState.DIALOGUE)

    exploration_screen.talk_to_npc_requested.connect(on_talk_to_npc)

    # Wire save/load interactions
    def on_save_game() -> None:
        menu_vm.save_game(player, "autosave")
        state_machine.transition_to(GameState.EXPLORATION)

    pause_screen.save_game_requested.connect(on_save_game)

    def on_load_game(slot: str) -> None:
        menu_vm.load_game(slot)

    main_menu_screen.load_game_requested.connect(on_load_game)

    def on_game_loaded(loaded_player: Player) -> None:
        nonlocal player
        player = loaded_player
        # Update all ViewModels with the new player
        exploration_vm._player = player
        dialogue_vm._player = player
        inventory_vm._player = player
        exploration_vm.look()
        state_machine.transition_to(GameState.EXPLORATION)

    menu_vm.game_loaded.connect(on_game_loaded)

    # Refresh saves list when showing main menu
    def on_state_change(new_state: GameState) -> None:
        if new_state == GameState.MAIN_MENU:
            menu_vm.refresh_saves_list()

    state_machine.on_state_change(on_state_change)
    menu_vm.refresh_saves_list()

    # Connect MenuViewModel signals to UI
    menu_vm.saves_list_updated.connect(main_menu_screen.update_saves_list)

    # Register all screens with the MainWindow
    main_window.register_screen(GameState.MAIN_MENU, main_menu_screen)
    main_window.register_screen(GameState.LOADING, loading_screen)
    main_window.register_screen(GameState.EXPLORATION, exploration_screen)
    main_window.register_screen(GameState.DIALOGUE, dialogue_screen)
    main_window.register_screen(GameState.COMBAT, combat_screen)
    main_window.register_screen(GameState.INVENTORY, inventory_screen)
    main_window.register_screen(GameState.PAUSED, pause_screen)

    main_window.show_initial_screen()
    main_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
