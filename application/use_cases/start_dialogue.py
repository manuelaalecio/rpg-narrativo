from application.ports.event_bus.event_bus_port import EventBusPort
from application.ports.repositories.content_repository_port import ContentRepositoryPort
from application.use_cases.use_case_result import UseCaseResult
from domain.entities.player import Player
from domain.events.dialogue_started import DialogueStarted


class StartDialogueUseCase:
    """Start a dialogue with an NPC."""

    def __init__(
        self,
        content_repository: ContentRepositoryPort,
        event_bus: EventBusPort,
    ) -> None:
        self._content_repository = content_repository
        self._event_bus = event_bus

    def execute(self, player: Player, npc_id: str) -> UseCaseResult:
        """Start a dialogue with the given NPC.

        Returns the Dialogue instance in result.data if successful.
        """
        try:
            npc = self._content_repository.get_npc(npc_id)
        except KeyError:
            return UseCaseResult(success=False, message=f"NPC '{npc_id}' not found.")

        if npc.dialogue_id is None:
            return UseCaseResult(success=False, message=f"{npc.name} has nothing to say.")

        try:
            dialogue = self._content_repository.get_dialogue(npc.dialogue_id)
        except KeyError:
            return UseCaseResult(success=False, message=f"Dialogue '{npc.dialogue_id}' not found.")

        dialogue.start()

        self._event_bus.publish(DialogueStarted(npc_id=npc.id, dialogue_id=dialogue.id))

        current_node = dialogue.get_current_node()
        return UseCaseResult(
            success=True,
            message=current_node.npc_text if current_node else "",
            data={"dialogue": dialogue, "npc_name": npc.name},
        )
