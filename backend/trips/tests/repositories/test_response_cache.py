from datetime import UTC, datetime, timedelta

import pytest

from trips.models import CachedResponse
from trips.repositories.response_cache import DatabaseResponseCache

NOW = datetime(2026, 1, 1, tzinfo=UTC)
TTL = timedelta(hours=1)


class Clock:
    def __init__(self) -> None:
        self.now = NOW

    def __call__(self) -> datetime:
        return self.now


@pytest.mark.django_db
def test_returns_stored_payload_until_expiry() -> None:
    clock = Clock()
    cache = DatabaseResponseCache(clock)
    cache.set("k", {"a": [1, 2]}, TTL)
    assert cache.get("k") == {"a": [1, 2]}
    clock.now = NOW + TTL
    assert cache.get("k") is None


@pytest.mark.django_db
def test_read_purges_all_expired_rows() -> None:
    clock = Clock()
    cache = DatabaseResponseCache(clock)
    cache.set("old", 1, TTL)
    cache.set("fresh", 2, TTL * 3)
    clock.now = NOW + TTL * 2
    assert cache.get("missing") is None
    assert list(CachedResponse.objects.values_list("key", flat=True)) == ["fresh"]


@pytest.mark.django_db
def test_set_overwrites_existing_key() -> None:
    cache = DatabaseResponseCache(Clock())
    cache.set("k", 1, TTL)
    cache.set("k", 2, TTL)
    assert cache.get("k") == 2
    assert CachedResponse.objects.count() == 1
