from datetime import UTC, datetime, timedelta

from trips.clients.cache import MemoryResponseCache

NOW = datetime(2026, 1, 1, tzinfo=UTC)
TTL = timedelta(hours=1)


class Clock:
    def __init__(self) -> None:
        self.now = NOW

    def __call__(self) -> datetime:
        return self.now


def test_returns_payload_until_expiry() -> None:
    clock = Clock()
    cache = MemoryResponseCache(clock)
    cache.set("k", {"a": [1, 2]}, TTL)
    assert cache.get("k") == {"a": [1, 2]}
    clock.now = NOW + TTL
    assert cache.get("k") is None


def test_set_overwrites_existing_key() -> None:
    cache = MemoryResponseCache(Clock())
    cache.set("k", 1, TTL)
    cache.set("k", 2, TTL)
    assert cache.get("k") == 2
