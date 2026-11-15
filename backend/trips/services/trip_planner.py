from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta

from trips.domain.assessment import Condition
from trips.domain.checkpoints import Checkpoint, sample_checkpoints
from trips.domain.geometry import LatLon
from trips.domain.metrics import RouteMetrics, Segment, compute_metrics
from trips.domain.recommendation import RankedRoute, RouteOption, rank_routes
from trips.domain.risk import RiskLevel
from trips.domain.weather import WeatherSample
from trips.services.assessment_at import assess_at
from trips.services.ports import (
    HourlyForecast,
    NoRoutesFoundError,
    RouteData,
    RouteRequest,
    RoutingClient,
    WeatherClient,
    WeatherQuery,
)
from trips.services.weather_validation import fetch_forecasts

EXPECTED_ROUTE_COUNT = 3


@dataclass(frozen=True)
class TripRequest:
    origin: LatLon
    destination: LatLon
    departure_utc: datetime
    gross_weight_lb: float
    interval_mi: float


@dataclass(frozen=True)
class CheckpointResult:
    position: LatLon
    mile: float
    eta_utc: datetime
    sample: WeatherSample
    level: RiskLevel
    causes: tuple[Condition, ...]
    load_rule_applied: bool


@dataclass(frozen=True)
class RouteResult:
    route_id: str
    polyline: list[LatLon]
    length_miles: float
    duration_s: float
    metrics: RouteMetrics
    checkpoints: list[CheckpointResult]
    rank: int
    recommended: bool
    has_no_travel: bool


@dataclass(frozen=True)
class TripPlan:
    routes: list[RouteResult]
    notice: str | None


@dataclass(frozen=True)
class _SampledRoute:
    route: RouteData
    checkpoints: list[Checkpoint]


@dataclass(frozen=True)
class _AssessedRoute:
    route: RouteData
    metrics: RouteMetrics
    checkpoints: list[CheckpointResult]


class TripPlanner:
    def __init__(self, routing: RoutingClient, weather: WeatherClient) -> None:
        self._routing = routing
        self._weather = weather

    def plan(self, request: TripRequest) -> TripPlan:
        routes = self._fetch_routes(request)
        sampled = [_sample(route, request.interval_mi) for route in routes]
        forecasts = self._fetch_weather(sampled, request)
        results = _build_results(sampled, forecasts, request)
        return TripPlan(routes=_rank(results), notice=_notice(len(routes)))

    def _fetch_routes(self, request: TripRequest) -> list[RouteData]:
        route_request = RouteRequest(request.departure_utc, request.gross_weight_lb)
        routes = self._routing.fetch_routes(request.origin, request.destination, route_request)
        if not routes:
            raise NoRoutesFoundError("No routes found between origin and destination")
        return routes

    def _fetch_weather(
        self, sampled: list[_SampledRoute], request: TripRequest
    ) -> list[HourlyForecast]:
        points = tuple(c.position for item in sampled for c in item.checkpoints)
        end = request.departure_utc + timedelta(seconds=_longest_trip_s(sampled))
        return fetch_forecasts(self._weather, WeatherQuery(points, request.departure_utc, end))


def _sample(route: RouteData, interval_mi: float) -> _SampledRoute:
    return _SampledRoute(
        route, sample_checkpoints(list(route.polyline), interval_mi, list(route.anchors))
    )


def _longest_trip_s(sampled: Sequence[_SampledRoute]) -> float:
    return max(item.checkpoints[-1].eta_offset_s for item in sampled)


def _build_results(
    sampled: list[_SampledRoute], forecasts: list[HourlyForecast], request: TripRequest
) -> list[_AssessedRoute]:
    results = []
    start = 0
    for item in sampled:
        count = len(item.checkpoints)
        results.append(_assess_route(item, forecasts[start : start + count], request))
        start += count
    return results


def _assess_route(
    item: _SampledRoute, forecasts: list[HourlyForecast], request: TripRequest
) -> _AssessedRoute:
    checkpoints = [
        _checkpoint_result(checkpoint, forecast, request)
        for checkpoint, forecast in zip(item.checkpoints, forecasts, strict=True)
    ]
    segments = [
        Segment(source.segment_miles, result.level)
        for source, result in zip(item.checkpoints, checkpoints, strict=True)
    ]
    return _AssessedRoute(item.route, compute_metrics(segments), checkpoints)


def _checkpoint_result(
    checkpoint: Checkpoint, forecast: HourlyForecast, request: TripRequest
) -> CheckpointResult:
    eta = request.departure_utc + timedelta(seconds=checkpoint.eta_offset_s)
    assessed = assess_at(forecast, eta, request.gross_weight_lb)
    risk = assessed.assessment
    risk_fields = (risk.level, risk.causes, risk.load_rule_applied)
    return CheckpointResult(
        checkpoint.position, checkpoint.mile, eta, assessed.sample, *risk_fields
    )


def _rank(assessed: list[_AssessedRoute]) -> list[RouteResult]:
    options = [RouteOption(a.route.route_id, a.metrics, a.route.duration_s) for a in assessed]
    by_id = {item.route.route_id: item for item in assessed}
    return [_route_result(by_id[r.option.route_id], r) for r in rank_routes(options)]


def _route_result(item: _AssessedRoute, ranked: RankedRoute) -> RouteResult:
    route = item.route
    route_fields = (route.route_id, list(route.polyline), route.length_miles, route.duration_s)
    rank_fields = (ranked.rank, ranked.recommended, ranked.has_no_travel)
    return RouteResult(*route_fields, item.metrics, item.checkpoints, *rank_fields)


def _notice(route_count: int) -> str | None:
    if route_count >= EXPECTED_ROUTE_COUNT:
        return None
    return f"Only {route_count} route(s) available"
