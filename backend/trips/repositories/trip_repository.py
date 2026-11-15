from typing import Any
from uuid import UUID

from trips.models import Trip
from trips.services.ports import StoredTrip


class TripRepository:
    def save(self, inputs: dict[str, Any], result: dict[str, Any]) -> StoredTrip:
        return _stored(Trip.objects.create(inputs=inputs, result=result))

    def get(self, trip_id: UUID) -> StoredTrip | None:
        trip = Trip.objects.filter(id=trip_id).first()
        return None if trip is None else _stored(trip)


def _stored(trip: Trip) -> StoredTrip:
    return StoredTrip(trip.id, trip.computed_at, trip.inputs, trip.result)
