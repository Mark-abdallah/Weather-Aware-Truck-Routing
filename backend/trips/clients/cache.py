from datetime import timedelta
from typing import Any, Protocol


class ResponseCache(Protocol):
    def get(self, key: str) -> Any | None:
        """The cached payload, or None when missing or expired."""
        ...

    def set(self, key: str, payload: Any, ttl: timedelta) -> None: ...
