"""Open-Meteo hourly forecast client: batched multi-location requests."""

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from itertools import batched
from typing import Any

from trips.clients.json_fetcher import JsonFetcher, JsonRequest
from trips.domain.geometry import LatLon
from trips.domain.weather import WeatherSample, cm_to_inches, mm_to_inches
from trips.services.ports import HourlyForecast, WeatherUnavailableError

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_CACHE_TTL = timedelta(hours=1)
MAX_POINTS_PER_REQUEST = 100
HOURLY_VARIABLES = ("wind_speed_10m", "wind_gusts_10m", "rain", "snowfall")
HOUR_FORMAT = "%Y-%m-%dT%H:%M"
ONE_HOUR = timedelta(hours=1)
FIXED_PARAMS = {
    "hourly": ",".join(HOURLY_VARIABLES),
    "wind_speed_unit": "mph",
    "timezone": "GMT",
    "timeformat": "unixtime",
}
MALFORMED_ERRORS = (KeyError, TypeError, ValueError, AttributeError)


class OpenMeteoClient:
    def __init__(self, fetcher: JsonFetcher) -> None:
        self._fetcher = fetcher

    def fetch_hourly(
        self, points: Sequence[LatLon], start: datetime, end: datetime
    ) -> list[HourlyForecast]:
        forecasts: list[HourlyForecast] = []
        for batch in batched(points, MAX_POINTS_PER_REQUEST, strict=False):
            forecasts.extend(self._fetch_batch(batch, start, end))
        return forecasts

    def _fetch_batch(
        self, batch: Sequence[LatLon], start: datetime, end: datetime
    ) -> list[HourlyForecast]:
        return self._fetcher.get(forecast_request(batch, start, end), _parse_locations)


def _parse_locations(payload: Any) -> list[HourlyForecast]:
    locations = payload if isinstance(payload, list) else [payload]
    try:
        return [_parse_location(location) for location in locations]
    except MALFORMED_ERRORS:
        raise WeatherUnavailableError("Unexpected weather response") from None


def forecast_request(batch: Sequence[LatLon], start: datetime, end: datetime) -> JsonRequest:
    params = {
        "latitude": ",".join(str(point.lat) for point in batch),
        "longitude": ",".join(str(point.lon) for point in batch),
        **FIXED_PARAMS,
        "start_hour": _floor_hour(start).strftime(HOUR_FORMAT),
        "end_hour": _ceil_hour(end).strftime(HOUR_FORMAT),
    }
    return JsonRequest(FORECAST_URL, params, WEATHER_CACHE_TTL)


def _floor_hour(moment: datetime) -> datetime:
    return moment.astimezone(UTC).replace(minute=0, second=0, microsecond=0)


def _ceil_hour(moment: datetime) -> datetime:
    floored = _floor_hour(moment)
    return floored if floored == moment else floored + ONE_HOUR


def _parse_location(location: dict[str, Any]) -> HourlyForecast:
    hourly = location["hourly"]
    times = tuple(datetime.fromtimestamp(stamp, UTC) for stamp in hourly["time"])
    rows = zip(*(hourly[name] for name in HOURLY_VARIABLES), strict=True)
    return HourlyForecast(times, tuple(_sample(row) for row in rows))


def _sample(row: tuple[float | None, ...]) -> WeatherSample:
    """Row order follows HOURLY_VARIABLES: wind mph, gust mph, rain mm, snowfall cm."""
    if any(value is None for value in row):
        raise ValueError("Weather row has missing values")
    wind_mph, gust_mph, rain_mm, snow_cm = row
    return WeatherSample(wind_mph, gust_mph, mm_to_inches(rain_mm), cm_to_inches(snow_cm))
