from datetime import UTC, datetime, timedelta

import pytest

from trips.domain.forecast import nearest_hour_index

HOURS = [datetime(2026, 1, 1, h, tzinfo=UTC) for h in range(6, 12)]


def at(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 1, 1, hour, minute, tzinfo=UTC)


def test_exact_hour():
    assert nearest_hour_index(at(8), HOURS) == 2


def test_29_minutes_rounds_down():
    assert nearest_hour_index(at(8, 29), HOURS) == 2


def test_30_minutes_rounds_to_later_hour():
    assert nearest_hour_index(at(8, 30), HOURS) == 3


def test_before_range_within_one_hour_uses_first():
    assert nearest_hour_index(at(5), HOURS) == 0


def test_after_range_within_one_hour_uses_last():
    assert nearest_hour_index(at(12), HOURS) == 5


def test_before_range_over_one_hour_raises():
    with pytest.raises(ValueError):
        nearest_hour_index(at(5) - timedelta(minutes=1), HOURS)


def test_after_range_over_one_hour_raises():
    with pytest.raises(ValueError):
        nearest_hour_index(at(12, 1), HOURS)


def test_empty_raises():
    with pytest.raises(ValueError):
        nearest_hour_index(at(8), [])


def test_naive_eta_raises():
    with pytest.raises(ValueError):
        nearest_hour_index(datetime(2026, 1, 1, 8), HOURS)


def test_naive_hourly_times_raise():
    with pytest.raises(ValueError):
        nearest_hour_index(at(8), [datetime(2026, 1, 1, 8)])
