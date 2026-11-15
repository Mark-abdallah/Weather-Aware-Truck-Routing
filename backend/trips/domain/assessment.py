import math
from dataclasses import astuple, dataclass
from enum import Enum

from trips.domain.risk import RiskLevel, classify_rain, classify_snow, classify_wind
from trips.domain.weather import WeatherSample

NO_TRAVEL_WIND_MPH = 55
HEAVY_LOAD_NO_TRAVEL_WIND_MPH = 45
HEAVY_LOAD_NO_TRAVEL_LOAD_LB = 30_000
HEAVY_LOAD_SEVERE_WIND_MPH = 35
HEAVY_LOAD_SEVERE_LOAD_LB = 40_000


class Condition(Enum):
    WIND = "wind"
    RAIN = "rain"
    SNOW = "snow"


@dataclass(frozen=True)
class Assessment:
    level: RiskLevel
    causes: tuple[Condition, ...]
    wind: RiskLevel
    rain: RiskLevel
    snow: RiskLevel
    load_rule_applied: bool


def _load_rule_level(wind_mph: float, load_lb: float) -> RiskLevel:
    if wind_mph >= NO_TRAVEL_WIND_MPH:
        return RiskLevel.NO_TRAVEL
    if wind_mph >= HEAVY_LOAD_NO_TRAVEL_WIND_MPH and load_lb > HEAVY_LOAD_NO_TRAVEL_LOAD_LB:
        return RiskLevel.NO_TRAVEL
    if wind_mph >= HEAVY_LOAD_SEVERE_WIND_MPH and load_lb > HEAVY_LOAD_SEVERE_LOAD_LB:
        return RiskLevel.SEVERE
    return RiskLevel.LOW


def apply_load_rules(wind_level: RiskLevel, wind_mph: float, load_lb: float) -> RiskLevel:
    return max(wind_level, _load_rule_level(wind_mph, load_lb))


def _validate(sample: WeatherSample) -> None:
    for value in astuple(sample):
        if math.isnan(value) or value < 0:
            raise ValueError("Weather values must be non-negative numbers")


def _validate_load(load_lb: float) -> None:
    if math.isnan(load_lb) or load_lb < 0:
        raise ValueError("Load must be a non-negative number")


def _tied_causes(levels: dict[Condition, RiskLevel], worst: RiskLevel) -> tuple[Condition, ...]:
    return tuple(condition for condition, level in levels.items() if level == worst)


def assess_checkpoint(sample: WeatherSample, load_lb: float) -> Assessment:
    _validate(sample)
    _validate_load(load_lb)
    base_wind = classify_wind(sample.wind_mph)
    wind = apply_load_rules(base_wind, sample.wind_mph, load_lb)
    rain = classify_rain(sample.rain_in_hr)
    snow = classify_snow(sample.snow_in_hr)
    levels = {Condition.WIND: wind, Condition.RAIN: rain, Condition.SNOW: snow}
    worst = max(levels.values())
    return Assessment(worst, _tied_causes(levels, worst), wind, rain, snow, wind > base_wind)
