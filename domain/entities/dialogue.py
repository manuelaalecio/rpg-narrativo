from dataclasses import dataclass, field


@dataclass
class Condition:
    """Structured condition data for dialogue options.

    Conditions are always data, never executable code.
    Supported types:
    - "requires_item": {"requires_item": "item_id"}
    - "requires_quest_completed": {"requires_quest_completed": "quest_id"} (future)
    """

    condition_type: str
    value: str


@dataclass
class DialogueOption:
    """A player choice within a dialogue node."""

    text: str
    next_node_id: str | None = None
    condition: Condition | None = None


@dataclass
class DialogueNode:
    """A single node in the dialogue graph: NPC speech + player options."""

    id: str
    npc_text: str
    options: list[DialogueOption] = field(default_factory=list)


@dataclass
class Dialogue:
    """Dialogue graph interpreted as a state machine.

    Maintains current node and provides navigation through options.
    """

    id: str
    start_node_id: str
    nodes: dict[str, DialogueNode] = field(default_factory=dict)
    _current_node_id: str | None = field(default=None, repr=False)
    _ended: bool = field(default=False, repr=False)

    def start(self) -> None:
        """Initialize dialogue at the start node."""
        self._current_node_id = self.start_node_id
        self._ended = False

    def get_current_node(self) -> DialogueNode | None:
        """Return the current dialogue node, or None if ended."""
        if self._ended or self._current_node_id is None:
            return None
        return self.nodes.get(self._current_node_id)

    def get_available_options(self, player) -> list[tuple[int, DialogueOption]]:
        """Return options whose conditions are satisfied by the player.

        Returns list of (index, option) tuples for available choices.
        """
        from domain.services.condition_evaluator import ConditionEvaluator

        node = self.get_current_node()
        if node is None:
            return []

        evaluator = ConditionEvaluator()
        available = []
        for idx, option in enumerate(node.options):
            if option.condition is None or evaluator.evaluate(option.condition, player):
                available.append((idx, option))
        return available

    def choose_option(self, option_index: int) -> bool:
        """Advance to the next node based on the chosen option.

        Returns True if dialogue continues, False if it ended.
        """
        node = self.get_current_node()
        if node is None or option_index >= len(node.options):
            return False

        option = node.options[option_index]
        if option.next_node_id is None:
            self._ended = True
            self._current_node_id = None
            return False

        self._current_node_id = option.next_node_id
        return True

    @property
    def is_ended(self) -> bool:
        """Check if the dialogue has ended."""
        return self._ended
