import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from trips.domain.risk import RiskLevel


@dataclass(frozen=True)
class Segment:
    miles: float
    level: RiskLevel


@dataclass(frozen=True)
class RouteMetrics:
    total_miles: float
    miles_by_level: Mapping[RiskLevel, float]
    average_risk: float

    @property
    def no_travel_miles(self) -> float:
        return self.miles_by_level[RiskLevel.NO_TRAVEL]

    @property
    def severe_miles(self) -> float:
        return self.miles_by_level[RiskLevel.SEVERE]

    @property
    def high_miles(self) -> float:
        return self.miles_by_level[RiskLevel.HIGH]


def _miles_by_level(segments: list[Segment]) -> dict[RiskLevel, float]:
    miles = {level: 0.0 for level in RiskLevel}
    for segment in segments:
        miles[segment.level] += segment.miles
    return miles


def _average_risk(miles_by_level: Mapping[RiskLevel, float], total_miles: float) -> float:
    if total_miles == 0:
        return 0.0
    weighted = sum(int(level) * miles for level, miles in miles_by_level.items())
    return weighted / total_miles


def compute_metrics(segments: Iterable[Segment]) -> RouteMetrics:
    segments = list(segments)
    if any(math.isnan(s.miles) or s.miles < 0 for s in segments):
        raise ValueError("Segment miles must be non-negative numbers")
    miles_by_level = MappingProxyType(_miles_by_level(segments))
    total_miles = sum(miles_by_level.values())
    return RouteMetrics(total_miles, miles_by_level, _average_risk(miles_by_level, total_miles))
