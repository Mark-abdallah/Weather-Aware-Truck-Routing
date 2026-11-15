import time

import pytest

from trips.domain.geometry import LatLon, haversine_miles
from trips.domain.grid import GridConfig, corridor_grid

CONFIG = GridConfig()
SMALL_ROUTE = [LatLon(40.0, -100.0 + 0.2 * i) for i in range(30)]
MILES_PER_DEGREE_LON_AT_40 = 53.0
LONG_ROUTE = [
    LatLon(40.0, -120.0 + 0.5 * i) for i in range(int(2000 / (0.5 * MILES_PER_DEGREE_LON_AT_40)))
]


def nearest_route_distance(point, route):
    return min(haversine_miles(point, p) for p in route)


def test_small_route_is_deterministic_and_non_empty():
    first = corridor_grid([SMALL_ROUTE], CONFIG)
    assert first and first == corridor_grid([SMALL_ROUTE], CONFIG)


def test_all_points_within_buffer():
    for point in corridor_grid([SMALL_ROUTE], CONFIG):
        assert nearest_route_distance(point, SMALL_ROUTE) <= CONFIG.buffer_mi


def test_far_points_excluded():
    grid = corridor_grid([SMALL_ROUTE], CONFIG)
    assert all(abs(point.lat - 40.0) < 1.0 for point in grid)


def test_covers_both_sides_of_route():
    grid = corridor_grid([SMALL_ROUTE], CONFIG)
    assert any(p.lat > 40.0 for p in grid) and any(p.lat < 40.0 for p in grid)


def test_multiple_routes_cover_each():
    other = [LatLon(30.0, -100.0 + 0.2 * i) for i in range(30)]
    grid = corridor_grid([SMALL_ROUTE, other], CONFIG)
    assert any(p.lat > 39 for p in grid) and any(p.lat < 31 for p in grid)


def test_empty_routes_give_empty_grid():
    assert corridor_grid([], CONFIG) == []


def test_cap_respected_for_long_route_quickly():
    config = GridConfig(max_points=300)
    started = time.perf_counter()
    grid = corridor_grid([LONG_ROUTE], config)
    assert 0 < len(grid) <= config.max_points
    assert time.perf_counter() - started < 1.0


def test_sparse_two_point_route_has_grid_near_midpoint():
    route = [LatLon(40.0, -100.0), LatLon(40.0, -96.0)]
    grid = corridor_grid([route], CONFIG)
    assert nearest_route_distance(LatLon(40.0, -98.0), grid) <= CONFIG.spacing_mi


def test_every_densified_route_point_has_nearby_grid_point():
    route = [LatLon(40.0, -100.0), LatLon(41.0, -97.0), LatLon(40.0, -94.0)]
    grid = corridor_grid([route], CONFIG)
    for start, end in zip(route, route[1:], strict=False):
        for i in range(101):
            f = i / 100
            point = LatLon(
                start.lat + (end.lat - start.lat) * f, start.lon + (end.lon - start.lon) * f
            )
            assert nearest_route_distance(point, grid) <= CONFIG.spacing_mi


@pytest.mark.parametrize("kwargs", [{"spacing_mi": 0}, {"buffer_mi": -1}, {"max_points": 0}])
def test_invalid_config_raises(kwargs):
    with pytest.raises(ValueError):
        GridConfig(**kwargs)
