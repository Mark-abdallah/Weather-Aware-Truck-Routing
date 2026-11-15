from typing import Any
from uuid import UUID, uuid4

from trips.services.heatmap import HEATMAP_HOURS, HeatmapService
from trips.services.ports import StoredTrip
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


class FakeStore:
    def __init__(self) -> None:
        self.trips: dict[UUID, StoredTrip] = {}

    def save(self, inputs: dict[str, Any], result: dict[str, Any]) -> StoredTrip:
        trip = StoredTrip(uuid4(), DEPARTURE, inputs, result)
        self.trips[trip.trip_id] = trip
        return trip

    def get(self, trip_id: UUID) -> StoredTrip | None:
        return self.trips.get(trip_id)


def make_service(store: FakeStore) -> TripService:
    weather = FakeWeather(lambda point, when: calm())
    planner = TripPlanner(FakeRouting([make_route("a", -100.0)]), weather)
    return TripService(planner, HeatmapService(weather), store)


def test_create_stores_inputs_with_serialized_plan_and_heatmap() -> None:
    store = FakeStore()
    request = TripRequest(ORIGIN, DESTINATION, DEPARTURE, 30_000, 25)
    trip = make_service(store).create(request, INPUTS)
    assert store.trips[trip.trip_id] == trip
    assert trip.inputs == INPUTS
    assert [route["route_id"] for route in trip.result["plan"]["routes"]] == ["a"]
    assert len(trip.result["heatmap"]["hours"]) == HEATMAP_HOURS


def test_get_returns_stored_trip_or_none() -> None:
    store = FakeStore()
    trip = store.save(INPUTS, {})
    service = make_service(store)
    assert service.get(trip.trip_id) == trip
    assert service.get(uuid4()) is None
