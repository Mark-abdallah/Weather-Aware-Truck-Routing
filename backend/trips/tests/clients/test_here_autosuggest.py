from typing import Any

import pytest
import respx

from trips.clients.here_autosuggest import AUTOSUGGEST_URL, HereAutosuggestClient
from trips.domain.geometry import LatLon
from trips.services.ports import Suggestion, SuggestionsUnavailableError
from trips.tests.clients.fakes import make_fetcher


def suggest(body: Any) -> list[Suggestion]:
    respx.get(AUTOSUGGEST_URL).respond(json=body)
    client = HereAutosuggestClient(make_fetcher(SuggestionsUnavailableError), "key")
    return client.suggest("Denver")


@respx.mock
def test_returns_only_items_with_positions() -> None:
    items = [
        {"title": "Denver, CO, United States", "position": {"lat": 39.74, "lng": -104.99}},
        {"title": "denver restaurants"},
    ]
    assert suggest({"items": items}) == [
        Suggestion("Denver, CO, United States", LatLon(39.74, -104.99))
    ]


@respx.mock
def test_sends_query_and_key() -> None:
    route = respx.get(AUTOSUGGEST_URL).respond(json={"items": []})
    HereAutosuggestClient(make_fetcher(SuggestionsUnavailableError), "key").suggest("Denver")
    params = route.calls.last.request.url.params
    assert params["q"] == "Denver"
    assert params["apiKey"] == "key"
    assert "at" in params


@respx.mock
@pytest.mark.parametrize("body", [{}, [], {"items": [{"position": {"lat": 1, "lng": 2}}]}])
def test_malformed_response_raises(body: Any) -> None:
    with pytest.raises(SuggestionsUnavailableError):
        suggest(body)
