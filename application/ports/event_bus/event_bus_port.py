from typing import Any, Protocol


class EventBusPort(Protocol):
    """Contract for publishing domain events."""

    def publish(self, event: Any) -> None:
        """Publish a domain event to all registered subscribers."""
        ...
