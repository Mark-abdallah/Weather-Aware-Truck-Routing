from collections.abc import Callable

from trips.services.ports import WeatherUnavailableError


def retry_once[Result](operation: Callable[[], Result]) -> Result:
    try:
        return operation()
    except WeatherUnavailableError:
        return operation()
