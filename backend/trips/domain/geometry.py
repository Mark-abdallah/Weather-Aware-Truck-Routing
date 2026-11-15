import math
from dataclasses import dataclass

EARTH_RADIUS_MILES = 3958.8


@dataclass(frozen=True)
class LatLon:
    lat: float
    lon: float


def haversine_miles(a: LatLon, b: LatLon) -> float:
    d_lat = math.radians(b.lat - a.lat)
    d_lon = math.radians(b.lon - a.lon)
    h = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(a.lat)) * math.cos(math.radians(b.lat)) * math.sin(d_lon / 2) ** 2
    )
    return 2 * EARTH_RADIUS_MILES * math.asin(math.sqrt(h))


def cumulative_miles(polyline: list[LatLon]) -> list[float]:
    totals = [0.0]
    for previous, current in zip(polyline, polyline[1:], strict=False):
        totals.append(totals[-1] + haversine_miles(previous, current))
    return totals


def interpolate_point(a: LatLon, b: LatLon, fraction: float) -> LatLon:
    return LatLon(
        lat=a.lat + (b.lat - a.lat) * fraction,
        lon=a.lon + (b.lon - a.lon) * fraction,
    )
