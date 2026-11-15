import hashlib
import json
import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

import httpx

from trips.clients.cache import ResponseCache

logger = logging.getLogger(__name__)
MAX_REASON_CHARS = 300


@dataclass(frozen=True)
class JsonRequest:
    url: str
    params: Mapping[str, str]
    ttl: timedelta
    secrets: Mapping[str, str] = field(default_factory=dict)


def cache_key(request: JsonRequest) -> str:
    encoded = json.dumps([request.url, sorted(request.params.items())])
    return hashlib.sha256(encoded.encode()).hexdigest()


class JsonFetcher:
    def __init__(self, http: httpx.Client, cache: ResponseCache, error: type[Exception]) -> None:
        self._http = http
        self._cache = cache
        self._error = error

    def get[Result](self, request: JsonRequest, parse: Callable[[Any], Result]) -> Result:
        key = cache_key(request)
        cached = self._cache.get(key)
        if cached is not None:
            return parse(cached)
        payload = self._download(request)
        result = parse(payload)
        self._cache.set(key, payload, request.ttl)
        return result

    def _download(self, request: JsonRequest) -> Any:
        try:
            response = self._http.get(request.url, params={**request.params, **request.secrets})
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as error:
            logger.warning("Request to %s failed: %s", request.url, _describe(error))
            raise self._error(f"Request to {request.url} failed") from None


def _describe(error: Exception) -> str:
    if isinstance(error, httpx.HTTPStatusError):
        body = error.response.text[:MAX_REASON_CHARS]
        return f"HTTP {error.response.status_code}: {body}"
    return type(error).__name__
