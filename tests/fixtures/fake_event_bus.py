from typing import Any

from application.ports.event_bus.event_bus_port import EventBusPort


class FakeEventBus:
    """In-memory fake event bus for testing."""

    def __init__(self) -> None:
        self.published_events: list[Any] = []

    def publish(self, event: Any) -> None:
        self.published_events.append(event)

    def assert_event_published(self, event_type: type) -> None:
        """Helper to assert that an event of the given type was published."""
        for event in self.published_events:
            if isinstance(event, event_type):
                return
        raise AssertionError(f"No event of type {event_type.__name__} was published")

    def clear(self) -> None:
        self.published_events.clear()


# Type assertion: FakeEventBus satisfies EventBusPort
_: EventBusPort = FakeEventBus()
