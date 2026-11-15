import pytest

from trips.domain.geometry import LatLon, cumulative_miles, haversine_miles, interpolate_point

ONE_DEGREE_MILES = 69.09


def test_one_degree_latitude_is_about_69_miles():
    distance = haversine_miles(LatLon(0, 0), LatLon(1, 0))
    assert distance == pytest.approx(ONE_DEGREE_MILES, abs=0.05)


def test_same_point_is_zero():
    assert haversine_miles(LatLon(10, 20), LatLon(10, 20)) == 0


def test_cumulative_miles_starts_at_zero_and_adds_up():
    line = [LatLon(0, 0), LatLon(1, 0), LatLon(2, 0)]
    totals = cumulative_miles(line)
    assert totals[0] == 0
    assert totals[2] == pytest.approx(2 * totals[1])


def test_interpolate_point_midway():
    assert interpolate_point(LatLon(0, 0), LatLon(2, 4), 0.5) == LatLon(1, 2)
