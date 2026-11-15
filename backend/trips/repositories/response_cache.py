from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from django.utils import timezone

from trips.models import CachedResponse


class DatabaseResponseCache:
    def __init__(self, clock: Callable[[], datetime] = timezone.now) -> None:
        self._clock = clock

    def get(self, key: str) -> Any | None:
        CachedResponse.objects.filter(expires_at__lte=self._clock()).delete()
        row = CachedResponse.objects.filter(key=key).first()
        return None if row is None else row.payload

    def set(self, key: str, payload: Any, ttl: timedelta) -> None:
        values = {"payload": payload, "expires_at": self._clock() + ttl}
        CachedResponse.objects.update_or_create(key=key, defaults=values)
