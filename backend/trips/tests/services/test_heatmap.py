import json
from datetime import timedelta

import pytest

from trips.services.heatmap import HEATMAP_HOURS, HeatmapService
from trips.services.ports import WeatherUnavailableError
from trips.services.serialization import serialize_heatmap
from trips.tests.services.fakes import DEPARTURE, FakeWeather, calm, make_route, windy

ROUTE = make_route("a", -100.0).polyline


def test_heatmap_has_49_hours_by_point_levels():
    weather = FakeWeather(lambda *_: calm())
    heatmap = HeatmapService(weather).build([ROUTE], DEPARTURE, 10_000)
    assert len(heatmap.hours) == HEATMAP_HOURS == 49
    assert heatmap.hours[0] == DEPARTURE
    assert len(heatmap.levels) == 49
    assert all(len(row) == len(heatmap.points) > 0 for row in heatmap.levels)
    assert weather.calls == 1


def test_heatmap_levels_follow_each_hour_and_load():
    weather = FakeWeather(lambda _point, time: windy(40 if time.hour >= 5 else 0))
    light = HeatmapService(weather).build([ROUTE], DEPARTURE, 10_000)
    heavy = HeatmapService(weather).build([ROUTE], DEPARTURE, 50_000)
    assert set(light.levels[0]) == {0}
    assert set(light.levels[5]) == {2}
    assert set(heavy.levels[5]) == {3}


def test_heatmap_retries_weather_once_then_raises():
    flaky = FakeWeather(lambda *_: calm(), failures_before_success=1)
    HeatmapService(flaky).build([ROUTE], DEPARTURE, 10_000)
    dead = FakeWeather(lambda *_: calm(), failures_before_success=2)
    with pytest.raises(WeatherUnavailableError):
        HeatmapService(dead).build([ROUTE], DEPARTURE, 10_000)


def test_serialized_heatmap_is_json_compatible():
    heatmap = HeatmapService(FakeWeather(lambda *_: calm())).build([ROUTE], DEPARTURE, 10_000)
    data = json.loads(json.dumps(serialize_heatmap(heatmap)))
    assert len(data["hours"]) == 49
    assert data["hours"][0] == "2026-01-01T00:00:00+00:00"
    assert len(data["levels"][0]) == len(data["points"])


def test_heatmap_fetches_departure_through_48_hours_ahead():
    weather = FakeWeather(lambda *_: calm())
    HeatmapService(weather).build([ROUTE], DEPARTURE, 10_000)
    assert weather.windows == [(DEPARTURE, DEPARTURE + timedelta(hours=48))]


def test_heatmap_rows_match_point_count_with_one_forecast_per_point():
    heatmap = HeatmapService(FakeWeather(lambda *_: calm())).build([ROUTE], DEPARTURE, 10_000)
    assert len(heatmap.points) > 1
    assert all(len(row) == len(heatmap.points) for row in heatmap.levels)


def test_heatmap_with_no_points_skips_weather():
    weather = FakeWeather(lambda *_: calm())
    heatmap = HeatmapService(weather).build([], DEPARTURE, 10_000)
    assert weather.calls == 0
    assert heatmap.levels == [[] for _ in range(HEATMAP_HOURS)]


def test_heatmap_stops_where_the_forecast_ends():
    weather = FakeWeather(lambda *_: calm(), hours_dropped=3)
    heatmap = HeatmapService(weather).build([ROUTE], DEPARTURE, 10_000)
    assert len(heatmap.hours) == len(heatmap.levels) == HEATMAP_HOURS - 2
    assert heatmap.hours[-1] == DEPARTURE + timedelta(hours=HEATMAP_HOURS - 3)
    assert weather.calls == 1


@pytest.mark.parametrize("delta", [-1, 1])
def test_heatmap_wrong_forecast_count_raises(delta):
    weather = FakeWeather(lambda *_: calm(), forecast_count_delta=delta)
    with pytest.raises(WeatherUnavailableError):
        HeatmapService(weather).build([ROUTE], DEPARTURE, 10_000)
