from bisect import bisect_right
from dataclasses import dataclass

from trips.domain.geometry import LatLon, cumulative_miles, interpolate_point

END_TOLERANCE_MILES = 1e-6


@dataclass(frozen=True)
class TimeAnchor:
    miles: float
    seconds: float


@dataclass(frozen=True)
class Checkpoint:
    index: int
    position: LatLon
    mile: float
    segment_miles: float
    eta_offset_s: float


def _segment_index(marks: list[float], value: float) -> int:
    return min(max(bisect_right(marks, value) - 1, 0), len(marks) - 2)


def _fraction_within(start: float, end: float, value: float) -> float:
    if end <= start:
        return 0.0
    return min(max((value - start) / (end - start), 0.0), 1.0)


def point_at_mile(polyline: list[LatLon], cumulative: list[float], mile: float) -> LatLon:
    i = _segment_index(cumulative, mile)
    fraction = _fraction_within(cumulative[i], cumulative[i + 1], mile)
    return interpolate_point(polyline[i], polyline[i + 1], fraction)


def seconds_at_mile(anchors: list[TimeAnchor], mile: float) -> float:
    if len(anchors) == 1:
        return anchors[0].seconds
    i = _segment_index([anchor.miles for anchor in anchors], mile)
    start, end = anchors[i], anchors[i + 1]
    fraction = _fraction_within(start.miles, end.miles, mile)
    return start.seconds + (end.seconds - start.seconds) * fraction


def _checkpoint_miles(total: float, interval_mi: float) -> list[float]:
    miles = []
    step = 1
    while step * interval_mi < total - END_TOLERANCE_MILES:
        miles.append(step * interval_mi)
        step += 1
    return [*miles, total]


@dataclass(frozen=True)
class _Track:
    polyline: list[LatLon]
    cumulative: list[float]
    anchors: list[TimeAnchor]


def _checkpoint(track: _Track, index: int, miles: list[float]) -> Checkpoint:
    mile = miles[index]
    start = miles[index - 1] if index > 0 else 0.0
    position = point_at_mile(track.polyline, track.cumulative, mile)
    return Checkpoint(index, position, mile, mile - start, seconds_at_mile(track.anchors, mile))


def sample_checkpoints(
    polyline: list[LatLon], interval_mi: float, anchors: list[TimeAnchor]
) -> list[Checkpoint]:
    if len(polyline) < 2 or interval_mi <= 0:
        raise ValueError("Need at least 2 polyline points and a positive interval")
    track = _Track(polyline, cumulative_miles(polyline), anchors)
    miles = _checkpoint_miles(track.cumulative[-1], interval_mi)
    return [_checkpoint(track, index, miles) for index in range(len(miles))]
