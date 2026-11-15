from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from typing import Any

from trips.clients.json_fetcher import JsonFetcher, JsonRequest
from trips.domain.geometry import LatLon
from trips.domain.weather import WeatherSample, cm_to_inches
from trips.services.ports import HourlyForecast, WeatherUnavailableError

FORECAST_URL = "https://api.weatherapi.com/v1/forecast.json"
WEATHER_CACHE_TTL = timedelta(hours=1)
FORECAST_DAYS = 3
COORDINATE_DECIMALS = 2
MAX_PARALLEL_REQUESTS = 8
FIXED_PARAMS = {"days": str(FORECAST_DAYS), "aqi": "no", "alerts": "no"}
MALFORMED_ERRORS = (KeyError, TypeError, ValueError, AttributeError)


class WeatherApiClient:
    def __init__(self, fetcher: JsonFetcher, api_key: str) -> None:
        self._fetcher = fetcher
        self._api_key = api_key

    def fetch_hourly(
        self, points: Sequence[LatLon], start: datetime, end: datetime
    ) -> list[HourlyForecast]:
        with ThreadPoolExecutor(MAX_PARALLEL_REQUESTS) as pool:
            return list(pool.map(self._fetch_point, points))

    def _fetch_point(self, point: LatLon) -> HourlyForecast:
        request = forecast_request(point, self._api_key)
        return self._fetcher.get(request, parse_forecast)


def forecast_request(point: LatLon, api_key: str) -> JsonRequest:
    location = f"{point.lat:.{COORDINATE_DECIMALS}f},{point.lon:.{COORDINATE_DECIMALS}f}"
    params = {"q": location, **FIXED_PARAMS}
    return JsonRequest(FORECAST_URL, params, WEATHER_CACHE_TTL, {"key": api_key})


def parse_forecast(payload: Any) -> HourlyForecast:
    try:
        hours = [hour for day in payload["forecast"]["forecastday"] for hour in day["hour"]]
        times = tuple(datetime.fromtimestamp(hour["time_epoch"], UTC) for hour in hours)
        return HourlyForecast(times, tuple(_sample(hour) for hour in hours))
    except MALFORMED_ERRORS:
        raise WeatherUnavailableError("Unexpected weather response") from None


def _sample(hour: dict[str, Any]) -> WeatherSample:
    snow_in = cm_to_inches(float(hour["snow_cm"]))
    precip_in = float(hour["precip_in"])
    rain_in = 0.0 if snow_in > 0 else precip_in
    return WeatherSample(float(hour["wind_mph"]), float(hour["gust_mph"]), rain_in, snow_in)
