from collections.abc import Callable, Sequence
from datetime import UTC, datetime, timedelta

from trips.domain.checkpoints import TimeAnchor
from trips.domain.geometry import LatLon
from trips.domain.weather import WeatherSample
from trips.services.ports import (
    HourlyForecast,
    RouteData,
    RouteRequest,
    WeatherUnavailableError,
)

DEPARTURE = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
ORIGIN = LatLon(40.0, -100.0)
DESTINATION = LatLon(41.0, -100.0)
SECONDS_PER_HOUR = 3600

SampleFn = Callable[[LatLon, datetime], WeatherSample]


def calm() -> WeatherSample:
    return WeatherSample(0, 0, 0, 0)


def windy(mph: float) -> WeatherSample:
    return WeatherSample(mph, mph, 0, 0)


def make_route(route_id: str, lon: float, duration_s: float = 3600) -> RouteData:
    polyline = (LatLon(40.0, lon), LatLon(41.0, lon))
    length_miles = 69.0
    anchors = (TimeAnchor(0, 0), TimeAnchor(length_miles, duration_s))
    return RouteData(route_id, polyline, anchors, length_miles, duration_s)


class FakeRouting:
    def __init__(self, routes: list[RouteData]) -> None:
        self._routes = routes

    def fetch_routes(
        self, origin: LatLon, destination: LatLon, request: RouteRequest
    ) -> list[RouteData]:
        return self._routes


class FakeWeather:
    """Returns hourly forecasts for exactly [start, end]; records every call.

    Faults: `failures_before_success` raises WeatherUnavailableError first;
    `hours_dropped` truncates the window's end; `forecast_count_delta` adds or
    removes forecasts relative to the points requested.
    """

    def __init__(
        self,
        sample_at: SampleFn,
        failures_before_success: int = 0,
        hours_dropped: int = 0,
        forecast_count_delta: int = 0,
    ) -> None:
        self._sample_at = sample_at
        self._failures_left = failures_before_success
        self._hours_dropped = hours_dropped
        self._count_delta = forecast_count_delta
        self.windows: list[tuple[datetime, datetime]] = []

    @property
    def calls(self) -> int:
        return len(self.windows)

    def fetch_hourly(
        self, points: Sequence[LatLon], start: datetime, end: datetime
    ) -> list[HourlyForecast]:
        self.windows.append((start, end))
        if self._failures_left > 0:
            self._failures_left -= 1
            raise WeatherUnavailableError("down")
        forecasts = [self._forecast(point, start, end) for point in points]
        return _adjust_count(forecasts, self._count_delta)

    def _forecast(self, point: LatLon, start: datetime, end: datetime) -> HourlyForecast:
        hours = int((end - start).total_seconds() // SECONDS_PER_HOUR) + 1 - self._hours_dropped
        times = tuple(start + timedelta(hours=h) for h in range(hours))
        return HourlyForecast(times, tuple(self._sample_at(point, time) for time in times))


def _adjust_count(forecasts: list[HourlyForecast], delta: int) -> list[HourlyForecast]:
    if delta < 0:
        return forecasts[:delta]
    return forecasts + forecasts[:1] * delta
