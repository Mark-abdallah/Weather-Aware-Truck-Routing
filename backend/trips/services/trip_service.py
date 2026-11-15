from typing import Any
from uuid import UUID

from trips.services.heatmap import HeatmapService
from trips.services.ports import StoredTrip, TripStore
from trips.services.serialization import serialize_heatmap, serialize_trip_plan
from trips.services.trip_planner import TripPlanner, TripRequest


class TripService:
    """Plans a trip, builds its heatmap and stores the snapshot."""

    def __init__(self, planner: TripPlanner, heatmap: HeatmapService, store: TripStore) -> None:
        self._planner = planner
        self._heatmap = heatmap
        self._store = store

    def create(self, request: TripRequest, inputs: dict[str, Any]) -> StoredTrip:
        plan = self._planner.plan(request)
        polylines = [route.polyline for route in plan.routes]
        heatmap = self._heatmap.build(polylines, request.departure_utc, request.gross_weight_lb)
        result = {"plan": serialize_trip_plan(plan), "heatmap": serialize_heatmap(heatmap)}
        return self._store.save(inputs, result)

    def get(self, trip_id: UUID) -> StoredTrip | None:
        return self._store.get(trip_id)
