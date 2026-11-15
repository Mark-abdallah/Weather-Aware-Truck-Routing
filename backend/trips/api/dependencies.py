from functools import cache

import httpx
from django.conf import settings

from trips.clients.here_autosuggest import HereAutosuggestClient
from trips.clients.here_routing import HereRoutingClient
from trips.clients.json_fetcher import JsonFetcher
from trips.clients.open_meteo import OpenMeteoClient
from trips.repositories.response_cache import DatabaseResponseCache
from trips.repositories.trip_repository import TripRepository
from trips.services.heatmap import HeatmapService
from trips.services.ports import (
    AddressSuggester,
    RoutingUnavailableError,
    SuggestionsUnavailableError,
    WeatherUnavailableError,
)
from trips.services.trip_planner import TripPlanner
from trips.services.trip_service import TripService

HTTP_TIMEOUT_S = 15.0


@cache
def _http() -> httpx.Client:
    return httpx.Client(timeout=HTTP_TIMEOUT_S)


def _fetcher(error: type[Exception]) -> JsonFetcher:
    return JsonFetcher(_http(), DatabaseResponseCache(), error)


def trip_service() -> TripService:
    routing = HereRoutingClient(_fetcher(RoutingUnavailableError), settings.HERE_API_KEY)
    weather = OpenMeteoClient(_fetcher(WeatherUnavailableError))
    planner = TripPlanner(routing, weather)
    return TripService(planner, HeatmapService(weather), TripRepository())


def address_suggester() -> AddressSuggester:
    fetcher = _fetcher(SuggestionsUnavailableError)
    return HereAutosuggestClient(fetcher, settings.HERE_API_KEY)
