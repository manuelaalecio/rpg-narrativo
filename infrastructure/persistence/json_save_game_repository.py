"""JSON-based implementation of SaveGameRepositoryPort."""

import json
from datetime import datetime
from pathlib import Path

from application.ports.repositories.save_game_repository_port import (
    SaveMetadata,
)
from domain.entities.save_game import SaveGame
from infrastructure.exceptions import SaveCorruptedError, SaveError, SaveNotFoundError


class JsonSaveGameRepository:
    """Save game repository using JSON files.

    Each save slot is stored as a separate JSON file in the save directory.
    File format: save/<slot>.json
    """

    def __init__(self, save_dir: Path) -> None:
        """Initialize repository with save directory.

        Args:
            save_dir: Directory where save files will be stored
        """
        self._save_dir = save_dir
        self._save_dir.mkdir(exist_ok=True)

    def save(self, save_game: SaveGame, slot: str) -> None:
        """Persist a save game to the specified slot."""
        file_path = self._save_dir / f"{slot}.json"
        data = save_game.to_dict()

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError as e:
            raise SaveError(f"Failed to write save file: {e}") from e

    def load(self, slot: str) -> SaveGame:
        """Load a save game from the specified slot."""
        file_path = self._save_dir / f"{slot}.json"

        if not file_path.exists():
            raise SaveNotFoundError(slot)

        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise SaveCorruptedError(slot, f"Invalid JSON: {e}") from e
        except OSError as e:
            raise SaveError(f"Failed to read save file: {e}") from e

        try:
            return SaveGame.from_dict(data)
        except (KeyError, ValueError, TypeError) as e:
            raise SaveCorruptedError(slot, f"Invalid save data: {e}") from e

    def list_saves(self) -> list[SaveMetadata]:
        """List all available save slots with metadata."""
        saves = []

        for file_path in self._save_dir.glob("*.json"):
            slot = file_path.stem

            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)

                metadata = SaveMetadata(
                    slot=slot,
                    save_name=data.get("save_name", "Unknown"),
                    timestamp=datetime.fromisoformat(data["timestamp"]),
                )
                saves.append(metadata)
            except (json.JSONDecodeError, KeyError, ValueError, OSError):
                # Skip corrupted or invalid save files
                continue

        # Sort by timestamp, newest first
        saves.sort(key=lambda m: m.timestamp, reverse=True)
        return saves

    def delete(self, slot: str) -> None:
        """Delete a save from the specified slot."""
        file_path = self._save_dir / f"{slot}.json"

        if not file_path.exists():
            raise SaveNotFoundError(slot)

        try:
            file_path.unlink()
        except OSError as e:
            raise SaveError(f"Failed to delete save file: {e}") from e
