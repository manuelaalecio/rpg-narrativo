from dataclasses import dataclass
from enum import Enum


class EffectType(Enum):
    """Types of effects that items can apply to the player."""

    HEAL = "heal"


@dataclass
class ItemEffect:
    """Structured data describing an item's effect when used.

    Effects are always data, never executable code.
    """

    effect_type: EffectType
    value: int
