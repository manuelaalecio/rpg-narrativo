class InfrastructureError(Exception):
    """Base exception for infrastructure layer errors."""


class ContentLoadError(InfrastructureError):
    """Raised when game content cannot be loaded from disk."""

    def __init__(self, file_path: str, reason: str) -> None:
        self.file_path = file_path
        self.reason = reason
        super().__init__(f"Failed to load content from '{file_path}': {reason}")


class SaveError(InfrastructureError):
    """Base exception for save game operations."""


class SaveNotFoundError(SaveError):
    """Raised when a save slot doesn't exist."""

    def __init__(self, slot: str) -> None:
        super().__init__(f"Save slot not found: {slot}")
        self.slot = slot


class SaveCorruptedError(SaveError):
    """Raised when a save file is corrupted or invalid."""

    def __init__(self, slot: str, reason: str) -> None:
        super().__init__(f"Save slot '{slot}' is corrupted: {reason}")
        self.slot = slot
        self.reason = reason
