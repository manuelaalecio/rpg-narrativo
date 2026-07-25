from application.ports.repositories.content_repository_port import ContentRepositoryPort
from domain.entities.item import Item
from domain.entities.map import GameMap


class FakeContentRepository:
    """In-memory fake content repository for testing."""

    def __init__(self, game_map: GameMap, items: dict[str, Item] | None = None) -> None:
        self._game_map = game_map
        self._items = items or {}

    def get_map(self) -> GameMap:
        return self._game_map

    def get_item(self, item_id: str) -> Item:
        return self._items[item_id]


# Type assertion: FakeContentRepository satisfies ContentRepositoryPort
_: ContentRepositoryPort = FakeContentRepository(GameMap())
