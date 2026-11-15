"""Ports (interfaces) and DTOs the application services depend on."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from trips.domain.checkpoints import TimeAnchor
from trips.domain.geometry import LatLon
from trips.domain.weather import WeatherSample


class WeatherUnavailableError(Exception):
    """The weather provider failed or returned unusable data."""


class RoutingUnavailableError(Exception):
    """The routing provider failed or returned unusable data."""


class SuggestionsUnavailableError(Exception):
    """The address suggestion provider failed or returned unusable data."""


class NoRoutesFoundError(Exception):
    """The routing provider found no route between the two points."""


@dataclass(frozen=True)
class RouteRequest:
    departure_utc: datetime
    gross_weight_lb: float


@dataclass(frozen=True)
class RouteData:
    route_id: str
    polyline: tuple[LatLon, ...]
    anchors: tuple[TimeAnchor, ...]
    length_miles: float
    duration_s: float


@dataclass(frozen=True)
class Suggestion:
    label: str
    position: LatLon


@dataclass(frozen=True)
class HourlyForecast:
    times: tuple[datetime, ...]
    samples: tuple[WeatherSample, ...]


@dataclass(frozen=True)
class WeatherQuery:
    points: tuple[LatLon, ...]
    start: datetime
    end: datetime


class RoutingClient(Protocol):
    def fetch_routes(
        self, origin: LatLon, destination: LatLon, request: RouteRequest
    ) -> list[RouteData]: ...


class WeatherClient(Protocol):
    def fetch_hourly(
        self, points: Sequence[LatLon], start: datetime, end: datetime
    ) -> list[HourlyForecast]:
        """One forecast per point, in the same order as points."""
        ...


class AddressSuggester(Protocol):
    def suggest(self, query: str) -> list[Suggestion]: ...


@dataclass(frozen=True)
class StoredTrip:
    trip_id: UUID
    computed_at: datetime
    inputs: dict[str, Any]
    result: dict[str, Any]


class TripStore(Protocol):
    def save(self, inputs: dict[str, Any], result: dict[str, Any]) -> StoredTrip: ...

    def get(self, trip_id: UUID) -> StoredTrip | None: ...
