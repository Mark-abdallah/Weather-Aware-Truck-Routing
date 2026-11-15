from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from trips.api import dependencies
from trips.api.serializers import AutosuggestQuerySerializer, TripInputSerializer, to_trip_request
from trips.services.ports import PlannedTrip, Suggestion


class HealthView(APIView):
    def get(self, request: Request) -> Response:
        return Response({"status": "ok"})


class TripListView(APIView):
    def post(self, request: Request) -> Response:
        serializer = TripInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        trip_request = to_trip_request(serializer.validated_data)
        trip = dependencies.trip_service().create(trip_request, dict(serializer.data))
        return Response(_trip_body(trip), status=status.HTTP_201_CREATED)


class AutosuggestView(APIView):
    def get(self, request: Request) -> Response:
        serializer = AutosuggestQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        suggestions = dependencies.address_suggester().suggest(serializer.validated_data["q"])
        return Response([_suggestion_body(s) for s in suggestions])


def _trip_body(trip: PlannedTrip) -> dict[str, Any]:
    return {"computed_at": trip.computed_at.isoformat(), "inputs": trip.inputs} | trip.result


def _suggestion_body(suggestion: Suggestion) -> dict[str, Any]:
    position = suggestion.position
    return {"label": suggestion.label, "lat": position.lat, "lon": position.lon}
