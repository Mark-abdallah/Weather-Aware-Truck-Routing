from collections.abc import Sequence
from datetime import datetime

from trips.domain.forecast import MAX_DISTANCE_OUTSIDE_RANGE
from trips.services.ports import (
    HourlyForecast,
    WeatherClient,
    WeatherQuery,
    WeatherUnavailableError,
)
from trips.services.retry import retry_once


def fetch_forecasts(weather: WeatherClient, query: WeatherQuery) -> list[HourlyForecast]:
    return retry_once(lambda: _fetch_and_validate(weather, query, require_end=True))


def fetch_available_forecasts(weather: WeatherClient, query: WeatherQuery) -> list[HourlyForecast]:
    return retry_once(lambda: _fetch_and_validate(weather, query, require_end=False))


def _fetch_and_validate(
    weather: WeatherClient, query: WeatherQuery, require_end: bool
) -> list[HourlyForecast]:
    forecasts = weather.fetch_hourly(query.points, query.start, query.end)
    if len(forecasts) != len(query.points):
        raise WeatherUnavailableError("Weather provider returned a wrong forecast count")
    for forecast in forecasts:
        _validate_forecast(forecast, query.start)
        if require_end:
            _validate_end(forecast, query.end)
    return forecasts


def _validate_forecast(forecast: HourlyForecast, start: datetime) -> None:
    times = forecast.times
    if not times or len(times) != len(forecast.samples):
        raise WeatherUnavailableError("Weather forecast is empty or misaligned")
    if not _is_ordered_and_aware(times):
        raise WeatherUnavailableError("Weather forecast times are unordered or naive")
    if times[0] - MAX_DISTANCE_OUTSIDE_RANGE > start:
        raise WeatherUnavailableError("Weather forecast starts too late")


def _validate_end(forecast: HourlyForecast, end: datetime) -> None:
    if forecast.times[-1] + MAX_DISTANCE_OUTSIDE_RANGE < end:
        raise WeatherUnavailableError("Weather forecast ends too early")


def _is_ordered_and_aware(times: Sequence[datetime]) -> bool:
    ordered = all(earlier < later for earlier, later in zip(times, times[1:], strict=False))
    return ordered and all(time.tzinfo is not None for time in times)
