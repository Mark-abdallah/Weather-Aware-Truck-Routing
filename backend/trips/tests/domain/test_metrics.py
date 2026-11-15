import pytest

from trips.domain.metrics import Segment, compute_metrics
from trips.domain.risk import RiskLevel


def test_mixed_example_hand_computed():
    metrics = compute_metrics(
        [
            Segment(10, RiskLevel.LOW),
            Segment(20, RiskLevel.HIGH),
            Segment(5, RiskLevel.NO_TRAVEL),
        ]
    )
    assert metrics.total_miles == 35
    assert metrics.average_risk == pytest.approx((0 * 10 + 2 * 20 + 4 * 5) / 35)
    assert metrics.high_miles == 20
    assert metrics.no_travel_miles == 5
    assert metrics.severe_miles == 0


def test_single_segment():
    metrics = compute_metrics([Segment(12.5, RiskLevel.SEVERE)])
    assert metrics.average_risk == 3
    assert metrics.severe_miles == 12.5


def test_all_five_levels_always_present():
    metrics = compute_metrics([Segment(1, RiskLevel.LOW)])
    assert set(metrics.miles_by_level) == set(RiskLevel)


def test_all_five_levels_used():
    segments = [Segment(10, level) for level in RiskLevel]
    metrics = compute_metrics(segments)
    assert all(metrics.miles_by_level[level] == 10 for level in RiskLevel)
    assert metrics.average_risk == 2


@pytest.mark.parametrize("segments", [[], [Segment(0, RiskLevel.HIGH)]])
def test_zero_distance_gives_zero_average(segments):
    metrics = compute_metrics(segments)
    assert metrics.total_miles == 0
    assert metrics.average_risk == 0.0


def test_level_miles_sum_to_total():
    segments = [
        Segment(3.5, RiskLevel.LOW),
        Segment(4.25, RiskLevel.LOW),
        Segment(1, RiskLevel.HIGH),
    ]
    metrics = compute_metrics(segments)
    assert sum(metrics.miles_by_level.values()) == pytest.approx(metrics.total_miles)
    assert metrics.miles_by_level[RiskLevel.LOW] == 7.75


def test_negative_miles_raises():
    with pytest.raises(ValueError):
        compute_metrics([Segment(-1, RiskLevel.LOW)])


def test_nan_miles_raises():
    with pytest.raises(ValueError):
        compute_metrics([Segment(float("nan"), RiskLevel.LOW)])


def test_miles_by_level_is_read_only():
    metrics = compute_metrics([Segment(1, RiskLevel.LOW)])
    with pytest.raises(TypeError):
        metrics.miles_by_level[RiskLevel.LOW] = 5
