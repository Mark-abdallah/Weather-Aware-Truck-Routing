from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from trips.services.ports import (
    NoRoutesFoundError,
    RoutingUnavailableError,
    SuggestionsUnavailableError,
    WeatherUnavailableError,
)

ERROR_RESPONSES: dict[type[Exception], tuple[int, str]] = {
    NoRoutesFoundError: (
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "No route found between these places.",
    ),
    WeatherUnavailableError: (
        status.HTTP_502_BAD_GATEWAY,
        "Weather service unavailable, try again",
    ),
    RoutingUnavailableError: (
        status.HTTP_502_BAD_GATEWAY,
        "Routing service unavailable, try again",
    ),
    SuggestionsUnavailableError: (
        status.HTTP_502_BAD_GATEWAY,
        "Address suggestions unavailable, try again",
    ),
}


def exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    mapped = ERROR_RESPONSES.get(type(exc))
    if mapped is None:
        return drf_exception_handler(exc, context)
    code, detail = mapped
    return Response({"detail": detail}, status=code)
