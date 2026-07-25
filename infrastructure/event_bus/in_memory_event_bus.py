"""In-memory event bus implementation.

Publishes domain events to registered handler functions.
When a handler raises an exception, it is caught and logged to stderr,
allowing remaining handlers to still execute. This prevents a single
faulty subscriber from breaking the entire event pipeline.
"""

import sys
import traceback
from collections import defaultdict
from collections.abc import Callable
from typing import Any

EventHandler = Callable[[Any], None]


class InMemoryEventBus:
    """Simple synchronous event bus with subscribe/publish semantics."""

    def __init__(self) -> None:
        self._handlers: dict[type, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: type, handler: EventHandler) -> None:
        """Register a handler for a specific event type.

        Handlers are called in the order they were subscribed.
        """
        self._handlers[event_type].append(handler)

    def publish(self, event: Any) -> None:
        """Publish an event to all registered handlers for its type.

        If a handler raises an exception, it is printed to stderr and
        the remaining handlers still execute.
        """
        event_type = type(event)
        for handler in self._handlers.get(event_type, []):
            try:
                handler(event)
            except Exception:
                print(
                    f"[EventBus] Handler {handler.__qualname__} failed for {event_type.__name__}:",
                    file=sys.stderr,
                )
                traceback.print_exc(file=sys.stderr)
