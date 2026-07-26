"""Fake save game repository for testing."""

from datetime import datetime

from application.ports.repositories.save_game_repository_port import (
    SaveGameRepositoryPort,
    SaveMetadata,
)
from domain.entities.save_game import SaveGame
from infrastructure.exceptions import SaveCorruptedError, SaveNotFoundError


class FakeSaveGameRepository:
    """In-memory fake save game repository for testing."""

    def __init__(self) -> None:
        self._saves: dict[str, SaveGame] = {}
        self._corrupted_slots: set[str] = set()

    def save(self, save_game: SaveGame, slot: str) -> None:
        """Save to in-memory storage."""
        self._saves[slot] = save_game

    def load(self, slot: str) -> SaveGame:
        """Load from in-memory storage."""
        if slot in self._corrupted_slots:
            raise SaveCorruptedError(slot, "Simulated corruption")
        if slot not in self._saves:
            raise SaveNotFoundError(slot)
        return self._saves[slot]

    def list_saves(self) -> list[SaveMetadata]:
        """List all saves with metadata."""
        saves = []
        for slot, save_game in self._saves.items():
            metadata = SaveMetadata(
                slot=slot,
                save_name=save_game.save_name,
                timestamp=save_game.timestamp,
            )
            saves.append(metadata)
        saves.sort(key=lambda m: m.timestamp, reverse=True)
        return saves

    def delete(self, slot: str) -> None:
        """Delete from in-memory storage."""
        if slot not in self._saves:
            raise SaveNotFoundError(slot)
        del self._saves[slot]

    def mark_corrupted(self, slot: str) -> None:
        """Mark a slot as corrupted for testing."""
        self._corrupted_slots.add(slot)
