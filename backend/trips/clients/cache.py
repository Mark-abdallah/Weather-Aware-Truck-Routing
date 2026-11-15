from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from threading import Lock
from typing import Any, Protocol


class ResponseCache(Protocol):
    def get(self, key: str) -> Any | None: ...

    def set(self, key: str, payload: Any, ttl: timedelta) -> None: ...


def _utc_now() -> datetime:
    return datetime.now(UTC)


class MemoryResponseCache:
    def __init__(self, clock: Callable[[], datetime] = _utc_now) -> None:
        self._clock = clock
        self._entries: dict[str, tuple[Any, datetime]] = {}
        self._lock = Lock()

    def get(self, key: str) -> Any | None:
        with self._lock:
            now = self._clock()
            self._entries = {k: v for k, v in self._entries.items() if v[1] > now}
            entry = self._entries.get(key)
        return None if entry is None else entry[0]

    def set(self, key: str, payload: Any, ttl: timedelta) -> None:
        with self._lock:
            self._entries[key] = (payload, self._clock() + ttl)
