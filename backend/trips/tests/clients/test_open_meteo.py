from datetime import UTC, datetime
from typing import Any

import httpx
import pytest
import respx

from trips.clients.open_meteo import FORECAST_URL, MAX_POINTS_PER_REQUEST, OpenMeteoClient
from trips.domain.geometry import LatLon
from trips.domain.weather import WeatherSample
from trips.services.ports import HourlyForecast, WeatherQuery, WeatherUnavailableError
from trips.services.weather_validation import fetch_forecasts
from trips.tests.clients.fakes import make_fetcher

START = datetime(2026, 1, 1, 10, 30, tzinfo=UTC)
END = datetime(2026, 1, 1, 12, 15, tzinfo=UTC)
HOUR_10 = 1767261600  # 2026-01-01T10:00Z


def location(rain_mm: float | None = 2.54) -> dict[str, Any]:
    hourly = {
        "time": [HOUR_10],
        "wind_speed_10m": [30.0],
        "wind_gusts_10m": [40.0],
        "rain": [rain_mm],
        "snowfall": [5.08],
    }
    return {"hourly": hourly}


def fetch(points: list[LatLon]) -> list[HourlyForecast]:
    return OpenMeteoClient(make_fetcher(WeatherUnavailableError)).fetch_hourly(points, START, END)


@respx.mock
def test_converts_units_and_times() -> None:
    respx.get(FORECAST_URL).respond(json=location())
    [forecast] = fetch([LatLon(40, -100)])
    assert forecast.times == (datetime(2026, 1, 1, 10, tzinfo=UTC),)
    assert forecast.samples == (WeatherSample(30.0, 40.0, pytest.approx(0.1), pytest.approx(2.0)),)


@respx.mock
def test_requests_whole_hours_covering_range_in_mph_utc() -> None:
    route = respx.get(FORECAST_URL).respond(json=location())
    fetch([LatLon(40, -100)])
    params = route.calls.last.request.url.params
    assert params["start_hour"] == "2026-01-01T10:00"
    assert params["end_hour"] == "2026-01-01T13:00"
    assert params["wind_speed_unit"] == "mph"
    assert params["timezone"] == "GMT"


@respx.mock
def test_batches_points_into_requests() -> None:
    route = respx.get(FORECAST_URL).mock(side_effect=_respond_per_point)
    points = [LatLon(40, -100 + i * 0.01) for i in range(MAX_POINTS_PER_REQUEST + 1)]
    forecasts = fetch(points)
    assert route.call_count == 2
    assert len(forecasts) == len(points)


def _respond_per_point(request: Any) -> Any:
    count = len(request.url.params["latitude"].split(","))
    return httpx.Response(200, json=[location() for _ in range(count)])


@respx.mock
@pytest.mark.parametrize("body", [location(rain_mm=None), {"hourly": {}}, {"error": True}])
def test_malformed_response_raises(body: Any) -> None:
    respx.get(FORECAST_URL).respond(json=body)
    with pytest.raises(WeatherUnavailableError):
        fetch([LatLon(40, -100)])


@respx.mock
def test_retry_after_bad_payload_downloads_again() -> None:
    route = respx.get(FORECAST_URL)
    route.side_effect = [
        httpx.Response(200, json=location(rain_mm=None)),
        httpx.Response(200, json=location()),
    ]
    client = OpenMeteoClient(make_fetcher(WeatherUnavailableError))
    query = WeatherQuery((LatLon(40, -100),), START, START)
    assert len(fetch_forecasts(client, query)) == 1
    assert route.call_count == 2
