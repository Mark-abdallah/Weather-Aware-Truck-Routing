"""JSON-serializable dicts for the API contract (snake_case keys).

TripPlan:
  {"notice": str | null, "routes": [Route, ...]}   (routes ordered by rank)
Route:
  {"route_id", "rank", "recommended", "has_no_travel", "length_miles",
   "duration_s", "polyline": [[lat, lon], ...],
   "metrics": {"total_miles", "average_risk", "miles_by_level": {level_name: miles}},
   "checkpoints": [Checkpoint, ...]}
Checkpoint:
  {"lat", "lon", "mile", "eta_utc" (ISO 8601), "wind_mph", "gust_mph",
   "rain_in_hr", "snow_in_hr", "level": int, "level_name": str,
   "causes": ["wind" | "rain" | "snow"], "load_rule_applied": bool}
Heatmap:
  {"points": [[lat, lon], ...], "hours": [ISO 8601, ...],
   "levels": [[int per point] per hour]}
Level names are lower-case RiskLevel names, e.g. "no_travel".
"""

from typing import Any

from trips.domain.geometry import LatLon
from trips.domain.metrics import RouteMetrics
from trips.domain.risk import RiskLevel
from trips.domain.weather import WeatherSample
from trips.services.heatmap import Heatmap
from trips.services.trip_planner import CheckpointResult, RouteResult, TripPlan


def _level_name(level: RiskLevel) -> str:
    return level.name.lower()


def _pair(point: LatLon) -> list[float]:
    return [point.lat, point.lon]


def _metrics(metrics: RouteMetrics) -> dict[str, Any]:
    return {
        "total_miles": metrics.total_miles,
        "average_risk": metrics.average_risk,
        "miles_by_level": {_level_name(lv): mi for lv, mi in metrics.miles_by_level.items()},
    }


def _weather(sample: WeatherSample) -> dict[str, Any]:
    return {
        "wind_mph": sample.wind_mph,
        "gust_mph": sample.gust_mph,
        "rain_in_hr": sample.rain_in_hr,
        "snow_in_hr": sample.snow_in_hr,
    }


def _risk(result: CheckpointResult) -> dict[str, Any]:
    return {
        "level": int(result.level),
        "level_name": _level_name(result.level),
        "causes": [cause.value for cause in result.causes],
        "load_rule_applied": result.load_rule_applied,
    }


def _checkpoint(result: CheckpointResult) -> dict[str, Any]:
    location = {"lat": result.position.lat, "lon": result.position.lon, "mile": result.mile}
    timing = {"eta_utc": result.eta_utc.isoformat()}
    return location | timing | _weather(result.sample) | _risk(result)


def _ranking(route: RouteResult) -> dict[str, Any]:
    return {
        "route_id": route.route_id,
        "rank": route.rank,
        "recommended": route.recommended,
        "has_no_travel": route.has_no_travel,
    }


def _route(route: RouteResult) -> dict[str, Any]:
    return _ranking(route) | {
        "length_miles": route.length_miles,
        "duration_s": route.duration_s,
        "polyline": [_pair(point) for point in route.polyline],
        "metrics": _metrics(route.metrics),
        "checkpoints": [_checkpoint(c) for c in route.checkpoints],
    }


def serialize_trip_plan(plan: TripPlan) -> dict[str, Any]:
    return {"notice": plan.notice, "routes": [_route(route) for route in plan.routes]}


def serialize_heatmap(heatmap: Heatmap) -> dict[str, Any]:
    return {
        "points": [_pair(point) for point in heatmap.points],
        "hours": [hour.isoformat() for hour in heatmap.hours],
        "levels": heatmap.levels,
    }
