"""Cached JSON GET requests shared by the provider clients."""

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

import httpx

from trips.clients.cache import ResponseCache


@dataclass(frozen=True)
class JsonRequest:
    url: str
    params: Mapping[str, str]
    ttl: timedelta
    secrets: Mapping[str, str] = field(default_factory=dict)


def cache_key(request: JsonRequest) -> str:
    """Hash of url + params; secrets (API keys) are never part of the key."""
    encoded = json.dumps([request.url, sorted(request.params.items())])
    return hashlib.sha256(encoded.encode()).hexdigest()


class JsonFetcher:
    def __init__(self, http: httpx.Client, cache: ResponseCache, error: type[Exception]) -> None:
        self._http = http
        self._cache = cache
        self._error = error

    def get(self, request: JsonRequest) -> Any:
        key = cache_key(request)
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        payload = self._download(request)
        self._cache.set(key, payload, request.ttl)
        return payload

    def _download(self, request: JsonRequest) -> Any:
        try:
            response = self._http.get(request.url, params={**request.params, **request.secrets})
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError):
            # "from None": the original exception text contains the URL with the API key.
            raise self._error(f"Request to {request.url} failed") from None
