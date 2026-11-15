from datetime import UTC, datetime
from typing import Any

import httpx
import pytest
import respx

from trips.clients.weatherapi import FORECAST_URL, WeatherApiClient, forecast_request
from trips.domain.geometry import LatLon
from trips.domain.weather import WeatherSample
from trips.services.ports import WeatherUnavailableError
from trips.tests.clients.fakes import FakeCache, make_fetcher

START = datetime(2026, 1, 1, 10, tzinfo=UTC)
END = datetime(2026, 1, 1, 12, tzinfo=UTC)
HOUR_10 = 1767261600
HOUR_11 = HOUR_10 + 3600


def hour(epoch: int, precip_in: float = 0.2, snow_cm: float = 0.0) -> dict[str, Any]:
    return {
        "time_epoch": epoch,
        "wind_mph": 30.0,
        "gust_mph": 40.0,
        "precip_in": precip_in,
        "snow_cm": snow_cm,
    }


def payload(*hours: dict[str, Any]) -> dict[str, Any]:
    return {"forecast": {"forecastday": [{"hour": list(hours)}]}}


def client(cache: FakeCache | None = None) -> WeatherApiClient:
    return WeatherApiClient(make_fetcher(WeatherUnavailableError, cache), "secret")


@respx.mock
def test_parses_hours_in_utc_with_rain_and_snow_split() -> None:
    respx.get(FORECAST_URL).respond(json=payload(hour(HOUR_10), hour(HOUR_11, 0.3, 5.08)))
    [forecast] = client().fetch_hourly([LatLon(40, -100)], START, END)
    assert forecast.times == (START, datetime(2026, 1, 1, 11, tzinfo=UTC))
    assert forecast.samples == (
        WeatherSample(30.0, 40.0, 0.2, 0.0),
        WeatherSample(30.0, 40.0, 0.0, pytest.approx(2.0)),
    )


@respx.mock
def test_one_request_per_point_in_order_with_key() -> None:
    route = respx.get(FORECAST_URL).mock(
        side_effect=lambda request: httpx.Response(
            200,
            json=payload(hour(HOUR_10 if request.url.params["q"].startswith("40.00") else HOUR_11)),
        )
    )
    forecasts = client().fetch_hourly([LatLon(40, -100), LatLon(41, -100)], START, END)
    assert [forecast.times[0].hour for forecast in forecasts] == [10, 11]
    assert route.call_count == 2
    assert route.calls[0].request.url.params["key"] == "secret"


def test_rounds_coordinates_and_keeps_key_out_of_cache_params() -> None:
    request = forecast_request(LatLon(40.123456, -100.987654), "secret")
    assert request.params["q"] == "40.12,-100.99"
    assert "key" not in request.params
    assert request.secrets == {"key": "secret"}


@respx.mock
def test_cached_point_is_not_requested_again() -> None:
    route = respx.get(FORECAST_URL).respond(json=payload(hour(HOUR_10)))
    weather = client(FakeCache())
    weather.fetch_hourly([LatLon(40, -100)], START, END)
    weather.fetch_hourly([LatLon(40.001, -100)], START, END)
    assert route.call_count == 1


@respx.mock
def test_provider_error_is_weather_unavailable() -> None:
    respx.get(FORECAST_URL).respond(429, json={"error": {"message": "limit"}})
    with pytest.raises(WeatherUnavailableError):
        client().fetch_hourly([LatLon(40, -100)], START, END)


@respx.mock
def test_malformed_payload_is_weather_unavailable() -> None:
    respx.get(FORECAST_URL).respond(json={"forecast": {}})
    with pytest.raises(WeatherUnavailableError):
        client().fetch_hourly([LatLon(40, -100)], START, END)
