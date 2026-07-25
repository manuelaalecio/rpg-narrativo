import pytest

from domain.events.item_picked_up import ItemPickedUp
from domain.events.player_moved import PlayerMoved
from infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus


@pytest.fixture
def bus() -> InMemoryEventBus:
    return InMemoryEventBus()


class TestInMemoryEventBus:
    def test_publish_to_subscriber(self, bus: InMemoryEventBus) -> None:
        received: list[PlayerMoved] = []
        bus.subscribe(PlayerMoved, lambda e: received.append(e))

        event = PlayerMoved(from_room_id="r1", to_room_id="r2")
        bus.publish(event)

        assert len(received) == 1
        assert received[0] is event

    def test_multiple_handlers_called_in_order(self, bus: InMemoryEventBus) -> None:
        order: list[int] = []
        bus.subscribe(PlayerMoved, lambda _: order.append(1))
        bus.subscribe(PlayerMoved, lambda _: order.append(2))
        bus.subscribe(PlayerMoved, lambda _: order.append(3))

        bus.publish(PlayerMoved(from_room_id="r1", to_room_id="r2"))

        assert order == [1, 2, 3]

    def test_handler_exception_does_not_stop_others(self, bus: InMemoryEventBus) -> None:
        received: list[str] = []

        def bad_handler(_: PlayerMoved) -> None:
            raise RuntimeError("boom")

        def good_handler(_: PlayerMoved) -> None:
            received.append("ok")

        bus.subscribe(PlayerMoved, bad_handler)
        bus.subscribe(PlayerMoved, good_handler)

        bus.publish(PlayerMoved(from_room_id="r1", to_room_id="r2"))

        assert received == ["ok"]

    def test_no_handlers_does_nothing(self, bus: InMemoryEventBus) -> None:
        bus.publish(PlayerMoved(from_room_id="r1", to_room_id="r2"))

    def test_different_event_types_are_isolated(self, bus: InMemoryEventBus) -> None:
        moved: list[PlayerMoved] = []
        picked: list[ItemPickedUp] = []

        bus.subscribe(PlayerMoved, lambda e: moved.append(e))
        bus.subscribe(ItemPickedUp, lambda e: picked.append(e))

        bus.publish(PlayerMoved(from_room_id="r1", to_room_id="r2"))

        assert len(moved) == 1
        assert len(picked) == 0

    def test_unsubscribed_event_type_not_called(self, bus: InMemoryEventBus) -> None:
        received: list[ItemPickedUp] = []
        bus.subscribe(ItemPickedUp, lambda e: received.append(e))

        bus.publish(PlayerMoved(from_room_id="r1", to_room_id="r2"))

        assert len(received) == 0
