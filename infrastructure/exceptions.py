class InfrastructureError(Exception):
    """Base exception for infrastructure layer errors."""


class ContentLoadError(InfrastructureError):
    """Raised when game content cannot be loaded from disk."""

    def __init__(self, file_path: str, reason: str) -> None:
        self.file_path = file_path
        self.reason = reason
        super().__init__(f"Failed to load content from '{file_path}': {reason}")
