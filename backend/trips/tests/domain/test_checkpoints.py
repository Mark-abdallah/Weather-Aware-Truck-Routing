import pytest

from trips.domain.checkpoints import TimeAnchor, point_at_mile, sample_checkpoints, seconds_at_mile
from trips.domain.geometry import LatLon, cumulative_miles

DEGREE = 69.09
SECONDS_PER_MILE = 60.0


def line(degrees: float) -> list[LatLon]:
    return [LatLon(0, 0), LatLon(degrees / 2, 0), LatLon(degrees, 0)]


def anchors_for(polyline: list[LatLon]) -> list[TimeAnchor]:
    total = cumulative_miles(polyline)[-1]
    return [TimeAnchor(0, 0), TimeAnchor(total, total * SECONDS_PER_MILE)]


def sample(polyline: list[LatLon], interval: float):
    return sample_checkpoints(polyline, interval, anchors_for(polyline))


def test_straight_line_sampling_with_remainder():
    polyline = line(1)
    result = sample(polyline, 25)
    assert [round(c.mile, 2) for c in result] == [25, 50, round(DEGREE, 2)]
    assert result[-1].segment_miles == pytest.approx(cumulative_miles(polyline)[-1] - 50)
    assert result[-1].position == LatLon(1, 0)


def test_exact_multiple_has_no_duplicate_destination():
    polyline = line(1)
    total = cumulative_miles(polyline)[-1]
    result = sample(polyline, total / 2)
    assert len(result) == 2
    assert result[-1].mile == pytest.approx(total)


def test_shorter_than_interval_returns_only_destination():
    result = sample(line(1), 500)
    assert len(result) == 1
    assert result[0].position == LatLon(1, 0)


def test_zero_length_route_single_checkpoint():
    polyline = [LatLon(5, 5), LatLon(5, 5)]
    result = sample_checkpoints(polyline, 25, [TimeAnchor(0, 0)])
    assert len(result) == 1
    assert result[0].segment_miles == 0
    assert result[0].position == LatLon(5, 5)


def test_segment_miles_sum_to_total():
    polyline = line(3)
    result = sample(polyline, 40)
    assert sum(c.segment_miles for c in result) == pytest.approx(cumulative_miles(polyline)[-1])


def test_etas_monotonic_and_indexed():
    result = sample(line(3), 40)
    etas = [c.eta_offset_s for c in result]
    assert etas == sorted(etas)
    assert [c.index for c in result] == list(range(len(result)))


def test_seconds_interpolated_between_anchors():
    anchors = [TimeAnchor(0, 0), TimeAnchor(10, 100), TimeAnchor(20, 400)]
    assert seconds_at_mile(anchors, 5) == 50
    assert seconds_at_mile(anchors, 15) == 250


def test_seconds_clamped_to_ends():
    anchors = [TimeAnchor(0, 0), TimeAnchor(10, 100)]
    assert seconds_at_mile(anchors, -5) == 0
    assert seconds_at_mile(anchors, 99) == 100


def test_point_at_mile_clamps_and_interpolates():
    polyline = line(2)
    cumulative = cumulative_miles(polyline)
    assert point_at_mile(polyline, cumulative, cumulative[-1] / 4) == LatLon(0.5, 0)
    assert point_at_mile(polyline, cumulative, 10_000) == LatLon(2, 0)


@pytest.mark.parametrize(
    ("polyline", "interval"),
    [([LatLon(0, 0)], 10), (line(1), 0), (line(1), -5)],
)
def test_invalid_inputs_raise(polyline, interval):
    with pytest.raises(ValueError):
        sample_checkpoints(polyline, interval, [TimeAnchor(0, 0)])
