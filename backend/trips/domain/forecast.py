from collections.abc import Sequence
from datetime import datetime, timedelta

MAX_DISTANCE_OUTSIDE_RANGE = timedelta(hours=1)


def nearest_hour_index(eta: datetime, hourly_times: Sequence[datetime]) -> int:
    if not hourly_times:
        raise ValueError("hourly_times must not be empty")
    _require_aware(eta, hourly_times)
    _require_within_range(eta, hourly_times)
    return min(range(len(hourly_times)), key=lambda index: _closeness(eta, hourly_times, index))


def _closeness(
    eta: datetime, hourly_times: Sequence[datetime], index: int
) -> tuple[timedelta, int]:
    return abs(hourly_times[index] - eta), -index


def _require_aware(eta: datetime, hourly_times: Sequence[datetime]) -> None:
    if eta.tzinfo is None or any(time.tzinfo is None for time in hourly_times):
        raise ValueError("eta and hourly_times must be timezone-aware")


def _require_within_range(eta: datetime, hourly_times: Sequence[datetime]) -> None:
    if eta < hourly_times[0] - MAX_DISTANCE_OUTSIDE_RANGE:
        raise ValueError("ETA is before the forecast range")
    if eta > hourly_times[-1] + MAX_DISTANCE_OUTSIDE_RANGE:
        raise ValueError("ETA is after the forecast range")
