from dataclasses import dataclass
from enum import IntEnum


class RiskLevel(IntEnum):
    LOW = 0
    MODERATE = 1
    HIGH = 2
    SEVERE = 3
    NO_TRAVEL = 4


@dataclass(frozen=True)
class Thresholds:
    """Lower bounds (inclusive) of Moderate, High and Severe, plus the No Travel limit."""

    moderate: float
    high: float
    severe: float
    no_travel: float
    no_travel_inclusive: bool


WIND_THRESHOLDS_MPH = Thresholds(25, 35, 45, 55, no_travel_inclusive=True)
RAIN_THRESHOLDS_IN_PER_HR = Thresholds(0.10, 0.25, 0.50, 1.00, no_travel_inclusive=False)
SNOW_THRESHOLDS_IN_PER_HR = Thresholds(0.5, 1.0, 2.0, 3.0, no_travel_inclusive=False)


def _is_no_travel(value: float, thresholds: Thresholds) -> bool:
    if thresholds.no_travel_inclusive:
        return value >= thresholds.no_travel
    return value > thresholds.no_travel


def _classify(value: float, thresholds: Thresholds) -> RiskLevel:
    if _is_no_travel(value, thresholds):
        return RiskLevel.NO_TRAVEL
    if value >= thresholds.severe:
        return RiskLevel.SEVERE
    if value >= thresholds.high:
        return RiskLevel.HIGH
    if value >= thresholds.moderate:
        return RiskLevel.MODERATE
    return RiskLevel.LOW


def classify_wind(mph: float) -> RiskLevel:
    return _classify(mph, WIND_THRESHOLDS_MPH)


def classify_rain(in_per_hr: float) -> RiskLevel:
    return _classify(in_per_hr, RAIN_THRESHOLDS_IN_PER_HR)


def classify_snow(in_per_hr: float) -> RiskLevel:
    return _classify(in_per_hr, SNOW_THRESHOLDS_IN_PER_HR)
