from collections.abc import Sequence
from datetime import timedelta
from typing import Any

from trips.clients.flexible_polyline import decode
from trips.clients.json_fetcher import JsonFetcher, JsonRequest
from trips.domain.checkpoints import TimeAnchor
from trips.domain.geometry import LatLon, cumulative_miles
from trips.services.ports import RouteData, RouteRequest, RoutingUnavailableError

ROUTES_URL = "https://router.hereapi.com/v8/routes"
ROUTE_CACHE_TTL = timedelta(hours=24)
ALTERNATIVE_COUNT = 2
METERS_PER_MILE = 1609.344
KG_PER_LB = 0.45359237
MIN_POLYLINE_POINTS = 2
MALFORMED_ERRORS = (KeyError, TypeError, ValueError, IndexError, AttributeError)


class HereRoutingClient:
    def __init__(self, fetcher: JsonFetcher, api_key: str) -> None:
        self._fetcher = fetcher
        self._api_key = api_key

    def fetch_routes(
        self, origin: LatLon, destination: LatLon, request: RouteRequest
    ) -> list[RouteData]:
        params = route_params(origin, destination, request)
        secrets = {"apiKey": self._api_key}
        route_request = JsonRequest(ROUTES_URL, params, ROUTE_CACHE_TTL, secrets)
        return self._fetcher.get(route_request, _parse_routes)


def _parse_routes(payload: Any) -> list[RouteData]:
    try:
        routes = [_parse_route(route) for route in payload.get("routes", [])]
        return [route for route in routes if len(route.polyline) >= MIN_POLYLINE_POINTS]
    except MALFORMED_ERRORS:
        raise RoutingUnavailableError("Unexpected routing response") from None


def route_params(origin: LatLon, destination: LatLon, request: RouteRequest) -> dict[str, str]:
    return {
        "transportMode": "truck",
        "origin": _coordinate(origin),
        "destination": _coordinate(destination),
        "departureTime": request.departure_utc.isoformat(),
        "vehicle[grossWeight]": str(round(request.gross_weight_lb * KG_PER_LB)),
        "alternatives": str(ALTERNATIVE_COUNT),
        "return": "polyline,summary",
        "spans": "duration",
    }


def _coordinate(point: LatLon) -> str:
    return f"{point.lat},{point.lon}"


def _parse_route(route: dict[str, Any]) -> RouteData:
    sections = route["sections"]
    polyline, anchors = _join_sections(sections)
    meters = sum(section["summary"]["length"] for section in sections)
    seconds = sum(section["summary"]["duration"] for section in sections)
    miles = meters / METERS_PER_MILE
    return RouteData(route["id"], tuple(polyline), tuple(anchors), miles, seconds)


def _join_sections(sections: Sequence[dict[str, Any]]) -> tuple[list[LatLon], list[TimeAnchor]]:
    polyline: list[LatLon] = []
    timings: list[tuple[int, float]] = []
    elapsed_s = 0.0
    for section in sections:
        for span in section["spans"]:
            timings.append((len(polyline) + span["offset"], elapsed_s))
            elapsed_s += span["duration"]
        polyline.extend(decode(section["polyline"]))
    timings.append((len(polyline) - 1, elapsed_s))
    return polyline, _anchors(polyline, timings)


def _anchors(polyline: list[LatLon], timings: list[tuple[int, float]]) -> list[TimeAnchor]:
    miles = cumulative_miles(polyline)
    return [TimeAnchor(miles[index], seconds) for index, seconds in timings]
