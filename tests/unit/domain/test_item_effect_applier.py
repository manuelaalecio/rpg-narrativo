import pytest

from domain.entities.player import Player
from domain.services.item_effect_applier import ItemEffectApplier
from domain.value_objects.item_effect import EffectType, ItemEffect


@pytest.fixture
def applier() -> ItemEffectApplier:
    return ItemEffectApplier()


@pytest.fixture
def wounded_player() -> Player:
    return Player(id="p1", name="Hero", current_room_id="room_01", health=50, max_health=100)


@pytest.fixture
def full_health_player() -> Player:
    return Player(id="p1", name="Hero", current_room_id="room_01", health=100, max_health=100)


class TestItemEffectApplier:
    def test_heal_restores_health(self, applier: ItemEffectApplier, wounded_player: Player) -> None:
        effect = ItemEffect(effect_type=EffectType.HEAL, value=30)
        message = applier.apply(effect, wounded_player)
        assert wounded_player.health == 80
        assert "30" in message

    def test_heal_capped_at_max_health(self, applier: ItemEffectApplier, wounded_player: Player) -> None:
        effect = ItemEffect(effect_type=EffectType.HEAL, value=999)
        message = applier.apply(effect, wounded_player)
        assert wounded_player.health == 100
        assert "50" in message

    def test_heal_at_full_health(self, applier: ItemEffectApplier, full_health_player: Player) -> None:
        effect = ItemEffect(effect_type=EffectType.HEAL, value=30)
        message = applier.apply(effect, full_health_player)
        assert full_health_player.health == 100
        assert "full health" in message.lower()

    def test_unknown_effect_type(self, applier: ItemEffectApplier, wounded_player: Player) -> None:
        effect = ItemEffect(effect_type=EffectType.HEAL, value=10)
        # Simulate an unknown effect type by monkey-patching the enum value
        effect.effect_type = type("FakeEnum", (), {"value": "unknown"})()  # type: ignore[assignment]
        message = applier.apply(effect, wounded_player)
        assert "nothing" in message.lower()
