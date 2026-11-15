from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta

from trips.domain.geometry import LatLon
from trips.domain.grid import GridConfig, corridor_grid
from trips.services.assessment_at import assess_at
from trips.services.ports import HourlyForecast, WeatherClient, WeatherQuery
from trips.services.weather_validation import fetch_forecasts

HEATMAP_HOURS = 49


@dataclass(frozen=True)
class Heatmap:
    points: list[LatLon]
    hours: list[datetime]
    levels: list[list[int]]


class HeatmapService:
    def __init__(self, weather: WeatherClient) -> None:
        self._weather = weather

    def build(
        self, routes: Sequence[Sequence[LatLon]], departure_utc: datetime, gross_weight_lb: float
    ) -> Heatmap:
        points = corridor_grid(routes, GridConfig())
        hours = [departure_utc + timedelta(hours=h) for h in range(HEATMAP_HOURS)]
        forecasts = self._forecasts(points, hours)
        levels = [_levels_at(hour, forecasts, gross_weight_lb) for hour in hours]
        return Heatmap(points=points, hours=hours, levels=levels)

    def _forecasts(self, points: list[LatLon], hours: list[datetime]) -> list[HourlyForecast]:
        if not points:
            return []
        return fetch_forecasts(self._weather, WeatherQuery(tuple(points), hours[0], hours[-1]))


def _levels_at(hour: datetime, forecasts: list[HourlyForecast], load_lb: float) -> list[int]:
    return [int(assess_at(forecast, hour, load_lb).assessment.level) for forecast in forecasts]
