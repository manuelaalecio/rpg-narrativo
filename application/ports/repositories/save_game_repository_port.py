"""Port for save game persistence operations."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from domain.entities.save_game import SaveGame


@dataclass
class SaveMetadata:
    """Lightweight metadata for listing saves without loading full data."""

    slot: str
    save_name: str
    timestamp: datetime


class SaveGameRepositoryPort(Protocol):
    """Interface for save game persistence.

    Implementations can use JSON files, SQLite, or any other storage.
    Domain and application layers depend only on this interface.
    """

    def save(self, save_game: SaveGame, slot: str) -> None:
        """Persist a save game to the specified slot.

        Args:
            save_game: The save game data to persist
            slot: The slot identifier (e.g., "slot_1", "slot_2")

        Raises:
            SaveError: If persistence fails
        """
        ...

    def load(self, slot: str) -> SaveGame:
        """Load a save game from the specified slot.

        Args:
            slot: The slot identifier to load from

        Returns:
            The loaded SaveGame

        Raises:
            SaveNotFoundError: If the slot doesn't exist
            SaveCorruptedError: If the save data is corrupted
        """
        ...

    def list_saves(self) -> list[SaveMetadata]:
        """List all available save slots with metadata.

        Returns:
            List of SaveMetadata objects, sorted by timestamp (newest first)
        """
        ...

    def delete(self, slot: str) -> None:
        """Delete a save from the specified slot.

        Args:
            slot: The slot identifier to delete

        Raises:
            SaveNotFoundError: If the slot doesn't exist
        """
        ...
