import math
from datetime import UTC, datetime
from typing import Any

from django.utils import timezone
from rest_framework import serializers

from trips.domain.geometry import LatLon
from trips.domain.trip_limits import (
    DEFAULT_INTERVAL_MI,
    MAX_GROSS_WEIGHT_LB,
    SAMPLING_INTERVALS_MI,
    departure_window,
)
from trips.services.trip_planner import TripRequest

MAX_LABEL_LENGTH = 300
MAX_QUERY_LENGTH = 200
MAX_LATITUDE = 90
MAX_LONGITUDE = 180


class FiniteFloatField(serializers.FloatField):
    def to_internal_value(self, data: Any) -> float:
        value = super().to_internal_value(data)
        if not math.isfinite(value):
            raise serializers.ValidationError("A finite number is required.")
        return value


class OffsetDateTimeField(serializers.DateTimeField):
    """Requires an explicit UTC offset and normalises to UTC."""

    def enforce_timezone(self, value: datetime) -> datetime:
        if timezone.is_naive(value):
            raise serializers.ValidationError("Include a UTC offset.")
        return value.astimezone(UTC)


class PlaceSerializer(serializers.Serializer):
    label = serializers.CharField(max_length=MAX_LABEL_LENGTH)
    lat = FiniteFloatField(min_value=-MAX_LATITUDE, max_value=MAX_LATITUDE)
    lon = FiniteFloatField(min_value=-MAX_LONGITUDE, max_value=MAX_LONGITUDE)


class TripInputSerializer(serializers.Serializer):
    origin = PlaceSerializer()
    destination = PlaceSerializer()
    departure = OffsetDateTimeField()
    gross_weight_lb = FiniteFloatField(max_value=MAX_GROSS_WEIGHT_LB)
    interval_mi = serializers.ChoiceField(SAMPLING_INTERVALS_MI, default=DEFAULT_INTERVAL_MI)

    def validate_departure(self, value: datetime) -> datetime:
        earliest, latest = departure_window(timezone.now())
        if not earliest <= value <= latest:
            raise serializers.ValidationError("Departure must be from 1 hour ago to 7 days ahead.")
        return value

    def validate_gross_weight_lb(self, value: float) -> float:
        if value <= 0:
            raise serializers.ValidationError("Gross weight must be greater than 0.")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if _position(attrs["origin"]) == _position(attrs["destination"]):
            raise serializers.ValidationError("Origin and destination must differ.")
        return attrs


class AutosuggestQuerySerializer(serializers.Serializer):
    q = serializers.CharField(max_length=MAX_QUERY_LENGTH)


def _position(place: dict[str, Any]) -> LatLon:
    return LatLon(place["lat"], place["lon"])


def to_trip_request(attrs: dict[str, Any]) -> TripRequest:
    origin, destination = _position(attrs["origin"]), _position(attrs["destination"])
    weight, interval = attrs["gross_weight_lb"], attrs["interval_mi"]
    return TripRequest(origin, destination, attrs["departure"], weight, interval)
