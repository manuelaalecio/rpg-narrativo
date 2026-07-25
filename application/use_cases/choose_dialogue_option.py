from application.ports.event_bus.event_bus_port import EventBusPort
from application.use_cases.use_case_result import UseCaseResult
from domain.entities.dialogue import Dialogue
from domain.entities.player import Player
from domain.events.dialogue_ended import DialogueEnded


class ChooseDialogueOptionUseCase:
    """Choose an option in an ongoing dialogue."""

    def __init__(self, event_bus: EventBusPort) -> None:
        self._event_bus = event_bus

    def execute(
        self,
        dialogue: Dialogue,
        option_index: int,
        player: Player,
        npc_id: str,
    ) -> UseCaseResult:
        """Choose a dialogue option by index.

        Returns the next node text and whether the dialogue continues.
        """
        if dialogue.is_ended:
            return UseCaseResult(success=False, message="Dialogue has already ended.")

        node = dialogue.get_current_node()
        if node is None:
            return UseCaseResult(success=False, message="No active dialogue node.")

        if option_index < 0 or option_index >= len(node.options):
            return UseCaseResult(success=False, message="Invalid option index.")

        continues = dialogue.choose_option(option_index)

        if not continues:
            self._event_bus.publish(DialogueEnded(npc_id=npc_id, dialogue_id=dialogue.id))
            return UseCaseResult(
                success=True,
                message="The conversation ends.",
                data={"ended": True, "npc_text": ""},
            )

        next_node = dialogue.get_current_node()
        return UseCaseResult(
            success=True,
            message=next_node.npc_text if next_node else "",
            data={"ended": False, "npc_text": next_node.npc_text if next_node else ""},
        )
