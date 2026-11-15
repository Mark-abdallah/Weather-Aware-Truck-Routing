from collections.abc import Iterable
from dataclasses import dataclass

from trips.domain.metrics import RouteMetrics

MILES_PRECISION = 2
RISK_PRECISION = 3


@dataclass(frozen=True)
class RouteOption:
    route_id: str
    metrics: RouteMetrics
    duration_s: float


@dataclass(frozen=True)
class RankedRoute:
    option: RouteOption
    rank: int
    recommended: bool
    has_no_travel: bool


def ranking_key(option: RouteOption) -> tuple[float, float, float, float, float]:
    metrics = option.metrics
    return (
        round(metrics.no_travel_miles, MILES_PRECISION),
        round(metrics.severe_miles, MILES_PRECISION),
        round(metrics.high_miles, MILES_PRECISION),
        round(metrics.average_risk, RISK_PRECISION),
        option.duration_s,
    )


def _to_ranked(rank: int, option: RouteOption) -> RankedRoute:
    return RankedRoute(
        option=option,
        rank=rank,
        recommended=rank == 1,
        has_no_travel=option.metrics.no_travel_miles > 0,
    )


def rank_routes(options: Iterable[RouteOption]) -> list[RankedRoute]:
    ordered = sorted(options, key=ranking_key)
    return [_to_ranked(rank, option) for rank, option in enumerate(ordered, start=1)]
