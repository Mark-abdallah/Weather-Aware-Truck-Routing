from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from trips.api import dependencies
from trips.domain.geometry import LatLon
from trips.services.heatmap import HeatmapService
from trips.services.ports import (
    RoutingUnavailableError,
    Suggestion,
    SuggestionsUnavailableError,
)
from trips.services.trip_planner import TripPlanner
from trips.services.trip_service import TripService
from trips.tests.services.fakes import FakeRouting, FakeWeather, calm, make_route
from trips.tests.services.test_trip_service import FakeStore

WEATHER_DOWN = 2


def trip_body(**overrides: Any) -> dict[str, Any]:
    body = {
        "origin": {"label": "A", "lat": 40.0, "lon": -100.0},
        "destination": {"label": "B", "lat": 41.0, "lon": -100.0},
        "departure": (timezone.now() + timedelta(hours=1)).isoformat(),
        "gross_weight_lb": 30000,
        "interval_mi": 25,
    }
    return body | overrides


def use_service(monkeypatch: pytest.MonkeyPatch, routing: Any, weather: Any) -> FakeStore:
    store = FakeStore()
    service = TripService(TripPlanner(routing, weather), HeatmapService(weather), store)
    monkeypatch.setattr(dependencies, "trip_service", lambda: service)
    return store


@pytest.fixture
def store(monkeypatch: pytest.MonkeyPatch) -> FakeStore:
    weather = FakeWeather(lambda point, when: calm())
    return use_service(monkeypatch, FakeRouting([make_route("a", -100.0)]), weather)


def post(body: dict[str, Any]) -> Any:
    return APIClient().post("/api/trips", body, format="json")


def test_create_then_fetch_trip(store: FakeStore) -> None:
    created = post(trip_body())
    assert created.status_code == 201
    fetched = APIClient().get(f"/api/trips/{created.json()['id']}")
    assert fetched.status_code == 200
    body = fetched.json()
    assert body == created.json()
    assert set(body) == {"id", "computed_at", "inputs", "plan", "heatmap"}
    assert body["inputs"]["origin"]["label"] == "A"


def test_departure_is_stored_in_utc(store: FakeStore) -> None:
    departure = "2026-01-01T07:00:00-05:00"
    now = datetime(2026, 1, 1, 12, tzinfo=UTC)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(timezone, "now", lambda: now)
        body = post(trip_body(departure=departure)).json()
    assert body["inputs"]["departure"] == "2026-01-01T12:00:00Z"


def test_unknown_trip_is_404(store: FakeStore) -> None:
    response = APIClient().get("/api/trips/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.parametrize(
    "overrides",
    [
        {"gross_weight_lb": 0},
        {"gross_weight_lb": 80_001},
        {"gross_weight_lb": "NaN"},
        {"interval_mi": 30},
        {"departure": "2026-01-01T12:00:00"},
        {"departure": (timezone.now() - timedelta(hours=2)).isoformat()},
        {"departure": (timezone.now() + timedelta(days=8)).isoformat()},
        {"origin": {"label": "A", "lat": 91, "lon": 0}},
        {"destination": {"label": "B", "lat": 40.0, "lon": -100.0}},
    ],
)
def test_invalid_input_is_400(store: FakeStore, overrides: dict[str, Any]) -> None:
    response = post(trip_body(**overrides))
    assert response.status_code == 400
    assert store.trips == {}


def test_interval_defaults_to_25(store: FakeStore) -> None:
    body = trip_body()
    del body["interval_mi"]
    assert post(body).json()["inputs"]["interval_mi"] == 25


def test_no_routes_is_422(monkeypatch: pytest.MonkeyPatch) -> None:
    use_service(monkeypatch, FakeRouting([]), FakeWeather(lambda point, when: calm()))
    assert post(trip_body()).status_code == 422


def test_weather_failure_is_502_and_nothing_stored(monkeypatch: pytest.MonkeyPatch) -> None:
    weather = FakeWeather(lambda point, when: calm(), failures_before_success=WEATHER_DOWN)
    store = use_service(monkeypatch, FakeRouting([make_route("a", -100.0)]), weather)
    response = post(trip_body())
    assert response.status_code == 502
    assert response.json() == {"detail": "Weather service unavailable, try again"}
    assert store.trips == {}


class FailingRouting:
    def fetch_routes(self, *args: Any) -> list[Any]:
        raise RoutingUnavailableError("down")


def test_routing_failure_is_502(monkeypatch: pytest.MonkeyPatch) -> None:
    use_service(monkeypatch, FailingRouting(), FakeWeather(lambda point, when: calm()))
    assert post(trip_body()).status_code == 502


class FakeSuggester:
    def __init__(self, error: Exception | None = None) -> None:
        self._error = error

    def suggest(self, query: str) -> list[Suggestion]:
        if self._error:
            raise self._error
        return [Suggestion(f"{query}, CO", LatLon(39.7, -105.0))]


def test_autosuggest_returns_labels_with_coordinates(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dependencies, "address_suggester", FakeSuggester)
    response = APIClient().get("/api/autosuggest", {"q": "Denver"})
    assert response.status_code == 200
    assert response.json() == [{"label": "Denver, CO", "lat": 39.7, "lon": -105.0}]


def test_autosuggest_requires_query(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dependencies, "address_suggester", FakeSuggester)
    assert APIClient().get("/api/autosuggest").status_code == 400


def test_autosuggest_provider_failure_is_502(monkeypatch: pytest.MonkeyPatch) -> None:
    failing = FakeSuggester(SuggestionsUnavailableError("down"))
    monkeypatch.setattr(dependencies, "address_suggester", lambda: failing)
    assert APIClient().get("/api/autosuggest", {"q": "Denver"}).status_code == 502
