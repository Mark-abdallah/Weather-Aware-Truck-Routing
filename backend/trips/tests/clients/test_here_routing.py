from datetime import UTC, datetime
from typing import Any

import pytest
import respx

from trips.clients.here_routing import ROUTES_URL, HereRoutingClient
from trips.domain.geometry import LatLon, cumulative_miles
from trips.services.ports import RouteRequest, RoutingUnavailableError
from trips.tests.clients.fakes import make_fetcher

POLYLINE = "BFoz5xJ67i1B1B7PzIhaxL7Y"  # 4 points
ORIGIN = LatLon(50.10228, 8.69821)
DESTINATION = LatLon(50.09878, 8.68752)
REQUEST = RouteRequest(datetime(2026, 1, 1, 12, tzinfo=UTC), gross_weight_lb=40000)


def section(spans: list[dict[str, float]]) -> dict[str, Any]:
    return {"polyline": POLYLINE, "spans": spans, "summary": {"length": 1609.344, "duration": 60}}


def payload(*sections: dict[str, Any]) -> dict[str, Any]:
    return {"routes": [{"id": "r1", "sections": list(sections)}]}


def fetch(body: Any) -> list[Any]:
    respx.get(ROUTES_URL).respond(json=body)
    client = HereRoutingClient(make_fetcher(RoutingUnavailableError), "key")
    return client.fetch_routes(ORIGIN, DESTINATION, REQUEST)


@respx.mock
def test_sends_truck_request_with_weight_in_kg() -> None:
    route = respx.get(ROUTES_URL).respond(json={"routes": []})
    HereRoutingClient(make_fetcher(RoutingUnavailableError), "key").fetch_routes(
        ORIGIN, DESTINATION, REQUEST
    )
    params = route.calls.last.request.url.params
    assert params["transportMode"] == "truck"
    assert params["alternatives"] == "2"
    assert params["vehicle[grossWeight]"] == "18144"
    assert params["origin"] == "50.10228,8.69821"
    assert params["apiKey"] == "key"


@respx.mock
def test_parses_route_with_span_anchors() -> None:
    spans = [{"offset": 0, "duration": 20}, {"offset": 2, "duration": 40}]
    [route] = fetch(payload(section(spans)))
    miles = cumulative_miles(list(route.polyline))
    assert route.route_id == "r1"
    assert len(route.polyline) == 4
    assert route.length_miles == pytest.approx(1.0)
    assert route.duration_s == 60
    assert [(a.miles, a.seconds) for a in route.anchors] == [
        (0.0, 0.0),
        (miles[2], 20.0),
        (miles[3], 60.0),
    ]


@respx.mock
def test_joins_sections_with_offsets_relative_to_each_section() -> None:
    spans = [{"offset": 0, "duration": 30}]
    [route] = fetch(payload(section(spans), section(spans)))
    assert len(route.polyline) == 8
    assert [a.seconds for a in route.anchors] == [0.0, 30.0, 60.0]
    assert route.duration_s == 120


@respx.mock
def test_no_routes_returns_empty_list() -> None:
    assert fetch({"routes": [], "notices": [{"code": "noRouteFound"}]}) == []


@respx.mock
@pytest.mark.parametrize(
    "body", [[], {"routes": [{"id": "r1"}]}, payload({"polyline": "!", "spans": []})]
)
def test_malformed_response_raises(body: Any) -> None:
    with pytest.raises(RoutingUnavailableError):
        fetch(body)


@respx.mock
def test_route_with_single_point_polyline_is_dropped() -> None:
    single_point = {"polyline": "BFoz5xJ67i1B", "spans": [], "summary": section([])["summary"]}
    assert fetch(payload(single_point)) == []
