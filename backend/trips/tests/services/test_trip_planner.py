import json
from datetime import timedelta

import pytest

from trips.domain.risk import RiskLevel
from trips.services.ports import NoRoutesFoundError, WeatherUnavailableError
from trips.services.serialization import serialize_trip_plan
from trips.services.trip_planner import TripPlanner, TripRequest
from trips.tests.services.fakes import (
    DEPARTURE,
    DESTINATION,
    ORIGIN,
    FakeRouting,
    FakeWeather,
    calm,
    make_route,
    windy,
)

HEAVY_LOAD_LB = 50_000
LIGHT_LOAD_LB = 10_000
INTERVAL_MI = 25


def request(load_lb: float = LIGHT_LOAD_LB, interval_mi: float = INTERVAL_MI) -> TripRequest:
    return TripRequest(ORIGIN, DESTINATION, DEPARTURE, load_lb, interval_mi)


def wind_by_longitude(winds: dict[float, float]):
    return lambda point, _time: windy(winds[point.lon])


def three_routes():
    return [make_route("a", -100.0), make_route("b", -101.0), make_route("c", -102.0)]


def test_routes_are_ranked_with_recommended_first():
    weather = FakeWeather(wind_by_longitude({-100.0: 60, -101.0: 40, -102.0: 0}))
    plan = TripPlanner(FakeRouting(three_routes()), weather).plan(request())
    assert [r.route_id for r in plan.routes] == ["c", "b", "a"]
    assert [r.recommended for r in plan.routes] == [True, False, False]
    assert [r.has_no_travel for r in plan.routes] == [False, False, True]
    assert plan.notice is None


def test_weather_is_fetched_once_for_all_routes():
    weather = FakeWeather(wind_by_longitude({-100.0: 0, -101.0: 0, -102.0: 0}))
    TripPlanner(FakeRouting(three_routes()), weather).plan(request())
    assert weather.calls == 1


def test_fewer_than_three_routes_adds_notice():
    routing = FakeRouting([make_route("a", -100.0), make_route("b", -101.0)])
    plan = TripPlanner(routing, FakeWeather(lambda *_: calm())).plan(request())
    assert plan.notice == "Only 2 route(s) available"


def test_no_routes_raises():
    planner = TripPlanner(FakeRouting([]), FakeWeather(lambda *_: calm()))
    with pytest.raises(NoRoutesFoundError):
        planner.plan(request())


def test_weather_failing_once_is_retried():
    weather = FakeWeather(lambda *_: calm(), failures_before_success=1)
    plan = TripPlanner(FakeRouting([make_route("a", -100.0)]), weather).plan(request())
    assert weather.calls == 2
    assert len(plan.routes) == 1


def test_weather_failing_twice_raises():
    weather = FakeWeather(lambda *_: calm(), failures_before_success=2)
    planner = TripPlanner(FakeRouting([make_route("a", -100.0)]), weather)
    with pytest.raises(WeatherUnavailableError):
        planner.plan(request())
    assert weather.calls == 2


def test_eta_uses_nearest_forecast_hour():
    weather = FakeWeather(lambda _point, time: windy(time.hour * 10))
    routing = FakeRouting([make_route("a", -100.0, duration_s=3.4 * 3600)])
    final = TripPlanner(routing, weather).plan(request(interval_mi=100)).routes[0].checkpoints[-1]
    assert final.sample.wind_mph == 30
    assert final.level == RiskLevel.MODERATE


def test_checkpoints_report_causes_and_load_rule():
    weather = FakeWeather(lambda *_: windy(50))
    routing = FakeRouting([make_route("a", -100.0)])
    first = TripPlanner(routing, weather).plan(request(HEAVY_LOAD_LB)).routes[0].checkpoints[0]
    assert first.level == RiskLevel.NO_TRAVEL
    assert first.load_rule_applied
    assert [c.value for c in first.causes] == ["wind"]


def test_serialized_plan_is_json_compatible():
    weather = FakeWeather(wind_by_longitude({-100.0: 60, -101.0: 40, -102.0: 0}))
    plan = TripPlanner(FakeRouting(three_routes()), weather).plan(request())
    data = json.loads(json.dumps(serialize_trip_plan(plan)))
    assert data["routes"][0]["route_id"] == "c"
    assert data["routes"][2]["checkpoints"][0]["level_name"] == "no_travel"
    assert data["routes"][0]["polyline"][0] == [40.0, -102.0]


def test_weather_window_spans_departure_to_longest_eta():
    weather = FakeWeather(lambda *_: calm())
    routing = FakeRouting([make_route("a", -100.0), make_route("b", -101.0, duration_s=7200)])
    TripPlanner(routing, weather).plan(request())
    assert weather.windows == [(DEPARTURE, DEPARTURE + timedelta(hours=2))]


def test_short_forecast_window_raises_after_retry():
    weather = FakeWeather(lambda *_: calm(), hours_dropped=3)
    routing = FakeRouting([make_route("a", -100.0, duration_s=5 * 3600)])
    with pytest.raises(WeatherUnavailableError):
        TripPlanner(routing, weather).plan(request())
    assert weather.calls == 2


@pytest.mark.parametrize("delta", [-1, 1])
def test_wrong_forecast_count_raises(delta):
    weather = FakeWeather(lambda *_: calm(), forecast_count_delta=delta)
    with pytest.raises(WeatherUnavailableError):
        TripPlanner(FakeRouting([make_route("a", -100.0)]), weather).plan(request())
