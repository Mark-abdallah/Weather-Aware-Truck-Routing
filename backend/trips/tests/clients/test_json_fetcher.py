from datetime import timedelta
from typing import Any

import httpx
import pytest
import respx

from trips.clients.json_fetcher import JsonRequest, cache_key
from trips.tests.clients.fakes import FakeCache, make_fetcher

URL = "https://api.example.test/data"
TTL = timedelta(hours=1)
REQUEST = JsonRequest(URL, {"q": "x"}, TTL, {"apiKey": "secret"})


class ProviderError(Exception):
    pass


def identity(payload: Any) -> Any:
    return payload


def reject(payload: Any) -> Any:
    raise ProviderError("unusable payload")


@respx.mock
def test_downloads_sends_secrets_and_caches_with_ttl() -> None:
    route = respx.get(URL, params={"q": "x", "apiKey": "secret"}).respond(json={"a": 1})
    cache = FakeCache()
    assert make_fetcher(ProviderError, cache).get(REQUEST, identity) == {"a": 1}
    assert route.called
    assert cache.entries[cache_key(REQUEST)] == ({"a": 1}, TTL)


@respx.mock
def test_cache_hit_skips_http() -> None:
    route = respx.get(URL).respond(json={"fresh": True})
    cache = FakeCache()
    cache.set(cache_key(REQUEST), {"cached": True}, TTL)
    assert make_fetcher(ProviderError, cache).get(REQUEST, identity) == {"cached": True}
    assert not route.called


def test_cache_key_ignores_secrets() -> None:
    other_key = JsonRequest(URL, {"q": "x"}, TTL, {"apiKey": "other"})
    assert cache_key(REQUEST) == cache_key(other_key)
    assert cache_key(REQUEST) != cache_key(JsonRequest(URL, {"q": "y"}, TTL))


@respx.mock
@pytest.mark.parametrize("response", [httpx.Response(500), httpx.Response(200, text="not json")])
def test_failures_raise_provider_error_without_secret(response: httpx.Response) -> None:
    respx.get(URL).mock(return_value=response)
    cache = FakeCache()
    with pytest.raises(ProviderError) as error:
        make_fetcher(ProviderError, cache).get(REQUEST, identity)
    assert "secret" not in str(error.value)
    assert cache.entries == {}


@respx.mock
def test_network_error_raises_provider_error() -> None:
    respx.get(URL).mock(side_effect=httpx.ConnectError("down"))
    with pytest.raises(ProviderError):
        make_fetcher(ProviderError).get(REQUEST, identity)


@respx.mock
def test_payload_that_fails_parsing_is_not_cached() -> None:
    respx.get(URL).respond(json={"bad": True})
    cache = FakeCache()
    with pytest.raises(ProviderError):
        make_fetcher(ProviderError, cache).get(REQUEST, reject)
    assert cache.entries == {}


@respx.mock
def test_returns_parsed_result() -> None:
    respx.get(URL).respond(json={"a": 1})
    assert make_fetcher(ProviderError).get(REQUEST, lambda payload: payload["a"]) == 1
