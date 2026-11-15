from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from trips.services.heatmap import HeatmapService
from trips.services.ports import PlannedTrip
from trips.services.serialization import serialize_heatmap, serialize_trip_plan
from trips.services.trip_planner import TripPlanner, TripRequest

Clock = Callable[[], datetime]


def _utc_now() -> datetime:
    return datetime.now(UTC)


class TripService:
    def __init__(
        self, planner: TripPlanner, heatmap: HeatmapService, clock: Clock = _utc_now
    ) -> None:
        self._planner = planner
        self._heatmap = heatmap
        self._clock = clock

    def create(self, request: TripRequest, inputs: dict[str, Any]) -> PlannedTrip:
        plan = self._planner.plan(request)
        polylines = [route.polyline for route in plan.routes]
        heatmap = self._heatmap.build(polylines, request.departure_utc, request.gross_weight_lb)
        result = {"plan": serialize_trip_plan(plan), "heatmap": serialize_heatmap(heatmap)}
        return PlannedTrip(self._clock(), inputs, result)
