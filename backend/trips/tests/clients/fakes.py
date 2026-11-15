from datetime import timedelta
from typing import Any

import httpx

from trips.clients.json_fetcher import JsonFetcher


class FakeCache:
    def __init__(self) -> None:
        self.entries: dict[str, tuple[Any, timedelta]] = {}

    def get(self, key: str) -> Any | None:
        entry = self.entries.get(key)
        return None if entry is None else entry[0]

    def set(self, key: str, payload: Any, ttl: timedelta) -> None:
        self.entries[key] = (payload, ttl)


def make_fetcher(error: type[Exception], cache: FakeCache | None = None) -> JsonFetcher:
    return JsonFetcher(httpx.Client(), cache or FakeCache(), error)
