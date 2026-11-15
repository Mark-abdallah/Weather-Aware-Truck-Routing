import math
from collections.abc import Iterator, Sequence
from dataclasses import dataclass

from trips.domain.geometry import EARTH_RADIUS_MILES, LatLon, haversine_miles

MILES_PER_DEGREE_LATITUDE = math.pi * EARTH_RADIUS_MILES / 180
SPACING_GROWTH_FACTOR = 1.1
MAX_LATITUDE_DEGREES = 89.0
DOWNSAMPLE_FRACTION_OF_SPACING = 0.5


@dataclass(frozen=True)
class GridConfig:
    spacing_mi: float = 15.0
    buffer_mi: float = 30.0
    max_points: int = 600

    def __post_init__(self) -> None:
        if self.spacing_mi <= 0:
            raise ValueError("spacing_mi must be positive")
        if self.buffer_mi < 0:
            raise ValueError("buffer_mi must not be negative")
        if self.max_points <= 0:
            raise ValueError("max_points must be positive")


@dataclass(frozen=True)
class _Lattice:
    origin: LatLon
    spacing_mi: float

    @property
    def lat_step(self) -> float:
        return self.spacing_mi / MILES_PER_DEGREE_LATITUDE

    def lon_step(self, lat: float) -> float:
        return degrees_of_longitude(self.spacing_mi, lat)

    def points_near(self, center: LatLon, radius_mi: float) -> Iterator[LatLon]:
        radius_lat = radius_mi / MILES_PER_DEGREE_LATITUDE
        first = math.ceil((center.lat - radius_lat - self.origin.lat) / self.lat_step)
        last = math.floor((center.lat + radius_lat - self.origin.lat) / self.lat_step)
        for row in range(first, last + 1):
            yield from self._row_points_near(row, center, radius_mi)

    def _row_points_near(self, row: int, center: LatLon, radius_mi: float) -> Iterator[LatLon]:
        lat = self.origin.lat + row * self.lat_step
        step = self.lon_step(lat)
        radius_lon = degrees_of_longitude(radius_mi, lat)
        first = math.ceil((center.lon - radius_lon - self.origin.lon) / step)
        last = math.floor((center.lon + radius_lon - self.origin.lon) / step)
        for column in range(first, last + 1):
            yield LatLon(lat, self.origin.lon + column * step)


def degrees_of_longitude(miles: float, lat: float) -> float:
    clamped = max(-MAX_LATITUDE_DEGREES, min(MAX_LATITUDE_DEGREES, lat))
    return miles / (MILES_PER_DEGREE_LATITUDE * math.cos(math.radians(clamped)))


def downsample(route: Sequence[LatLon], min_gap_mi: float) -> list[LatLon]:
    if not route:
        return []
    kept = [route[0]]
    for point in route[1:]:
        if haversine_miles(kept[-1], point) >= min_gap_mi:
            kept.append(point)
    return kept


def _interpolate(start: LatLon, end: LatLon, fraction: float) -> LatLon:
    return LatLon(
        start.lat + (end.lat - start.lat) * fraction,
        start.lon + (end.lon - start.lon) * fraction,
    )


def _segment_points(start: LatLon, end: LatLon, max_gap_mi: float) -> list[LatLon]:
    parts = math.ceil(haversine_miles(start, end) / max_gap_mi)
    return [_interpolate(start, end, i / parts) for i in range(1, parts)] + [end]


def _densify(route: Sequence[LatLon], max_gap_mi: float) -> list[LatLon]:
    if not route:
        return []
    dense = [route[0]]
    for start, end in zip(route, route[1:], strict=False):
        dense.extend(_segment_points(start, end, max_gap_mi))
    return dense


def _expanded_origin(points: Sequence[LatLon], buffer_mi: float) -> LatLon:
    widest_lat = max(abs(point.lat) for point in points)
    return LatLon(
        lat=min(point.lat for point in points) - buffer_mi / MILES_PER_DEGREE_LATITUDE,
        lon=min(point.lon for point in points) - degrees_of_longitude(buffer_mi, widest_lat),
    )


def _grid_at_spacing(
    anchors: Sequence[LatLon], lattice: _Lattice, buffer_mi: float
) -> list[LatLon]:
    found = {
        candidate
        for anchor in anchors
        for candidate in lattice.points_near(anchor, buffer_mi)
        if haversine_miles(anchor, candidate) <= buffer_mi
    }
    return sorted(found, key=lambda point: (point.lat, point.lon))


def _anchors(routes: Sequence[Sequence[LatLon]], config: GridConfig) -> list[LatLon]:
    min_gap_mi = config.spacing_mi * DOWNSAMPLE_FRACTION_OF_SPACING
    return [
        point for route in routes for point in downsample(_densify(route, min_gap_mi), min_gap_mi)
    ]


def corridor_grid(routes: Sequence[Sequence[LatLon]], config: GridConfig) -> list[LatLon]:
    anchors = _anchors(routes, config)
    if not anchors:
        return []
    origin = _expanded_origin(anchors, config.buffer_mi)
    spacing = config.spacing_mi
    grid = _grid_at_spacing(anchors, _Lattice(origin, spacing), config.buffer_mi)
    while len(grid) > config.max_points:
        spacing *= SPACING_GROWTH_FACTOR
        grid = _grid_at_spacing(anchors, _Lattice(origin, spacing), config.buffer_mi)
    return grid
