from datetime import timedelta
from typing import Any

from trips.clients.json_fetcher import JsonFetcher, JsonRequest
from trips.domain.geometry import LatLon
from trips.services.ports import Suggestion, SuggestionsUnavailableError

AUTOSUGGEST_URL = "https://autosuggest.search.hereapi.com/v1/autosuggest"
SUGGESTION_CACHE_TTL = timedelta(hours=24)
SUGGESTION_LIMIT = 5
SEARCH_CENTER = "39.8283,-98.5795"
MALFORMED_ERRORS = (KeyError, TypeError, AttributeError)


class HereAutosuggestClient:
    def __init__(self, fetcher: JsonFetcher, api_key: str) -> None:
        self._fetcher = fetcher
        self._api_key = api_key

    def suggest(self, query: str) -> list[Suggestion]:
        params = {"q": query, "at": SEARCH_CENTER, "limit": str(SUGGESTION_LIMIT)}
        secrets = {"apiKey": self._api_key}
        request = JsonRequest(AUTOSUGGEST_URL, params, SUGGESTION_CACHE_TTL, secrets)
        return self._fetcher.get(request, _parse_suggestions)


def _parse_suggestions(payload: Any) -> list[Suggestion]:
    try:
        return [_suggestion(item) for item in payload["items"] if "position" in item]
    except MALFORMED_ERRORS:
        raise SuggestionsUnavailableError("Unexpected autosuggest response") from None


def _suggestion(item: dict[str, Any]) -> Suggestion:
    position = item["position"]
    return Suggestion(item["title"], LatLon(position["lat"], position["lng"]))
