from dataclasses import dataclass
from typing import Any


@dataclass
class UseCaseResult:
    """Standard result returned by all use cases."""

    success: bool
    message: str = ""
    data: dict[str, Any] | None = None
