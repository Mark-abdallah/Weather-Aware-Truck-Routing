from trips.services.heatmap import HEATMAP_HOURS, HeatmapService
from trips.services.trip_planner import TripPlanner, TripRequest
from trips.services.trip_service import TripService
from trips.tests.services.fakes import (
    DEPARTURE,
    DESTINATION,
    ORIGIN,
    FakeRouting,
    FakeWeather,
    calm,
    make_route,
)

INPUTS = {"echo": "inputs"}


def make_service() -> TripService:
    weather = FakeWeather(lambda point, when: calm())
    planner = TripPlanner(FakeRouting([make_route("a", -100.0)]), weather)
    return TripService(planner, HeatmapService(weather), lambda: DEPARTURE)


def test_create_returns_inputs_with_serialized_plan_and_heatmap() -> None:
    request = TripRequest(ORIGIN, DESTINATION, DEPARTURE, 30_000, 25)
    trip = make_service().create(request, INPUTS)
    assert trip.computed_at == DEPARTURE
    assert trip.inputs == INPUTS
    assert [route["route_id"] for route in trip.result["plan"]["routes"]] == ["a"]
    assert len(trip.result["heatmap"]["hours"]) == HEATMAP_HOURS
