"""Allowed trip inputs (confirmed in docs/SPEC.md)."""

from datetime import datetime, timedelta

MAX_GROSS_WEIGHT_LB = 80_000
SAMPLING_INTERVALS_MI = (10, 25, 50)
DEFAULT_INTERVAL_MI = 25
EARLIEST_DEPARTURE_BEFORE_NOW = timedelta(hours=1)
LATEST_DEPARTURE_AFTER_NOW = timedelta(days=7)


def departure_window(now: datetime) -> tuple[datetime, datetime]:
    return now - EARLIEST_DEPARTURE_BEFORE_NOW, now + LATEST_DEPARTURE_AFTER_NOW
