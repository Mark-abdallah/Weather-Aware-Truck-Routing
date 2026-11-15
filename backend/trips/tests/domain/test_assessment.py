import pytest

from trips.domain.assessment import Condition, apply_load_rules, assess_checkpoint
from trips.domain.risk import RiskLevel, classify_wind
from trips.domain.weather import WeatherSample


def _level(mph: float, load: float) -> RiskLevel:
    return apply_load_rules(classify_wind(mph), mph, load)


def _sample(wind=0.0, rain=0.0, snow=0.0) -> WeatherSample:
    return WeatherSample(wind_mph=wind, gust_mph=wind, rain_in_hr=rain, snow_in_hr=snow)


def test_no_travel_at_55_any_load():
    assert _level(55, 0) == RiskLevel.NO_TRAVEL


def test_heavy_load_boundary_at_50_mph():
    assert _level(50, 30_000) == RiskLevel.SEVERE
    assert _level(50, 30_001) == RiskLevel.NO_TRAVEL


def test_heavy_load_boundary_at_40_mph():
    assert _level(40, 40_000) == RiskLevel.HIGH
    assert _level(40, 40_001) == RiskLevel.SEVERE


def test_below_35_mph_heavy_load_unchanged():
    assert _level(34.9, 80_000) == RiskLevel.MODERATE


def test_load_rules_never_lower_level():
    assert apply_load_rules(RiskLevel.NO_TRAVEL, 10, 0) == RiskLevel.NO_TRAVEL
    assert apply_load_rules(RiskLevel.SEVERE, 36, 41_000) == RiskLevel.SEVERE


def test_single_worst_cause():
    result = assess_checkpoint(_sample(wind=10, rain=0.3), 0)
    assert result.level == RiskLevel.HIGH
    assert result.causes == (Condition.RAIN,)


def test_tied_causes_listed_in_order():
    result = assess_checkpoint(_sample(wind=36, rain=0.3, snow=0.1), 0)
    assert result.causes == (Condition.WIND, Condition.RAIN)


def test_load_rule_flag_and_cause():
    result = assess_checkpoint(_sample(wind=40), 50_000)
    assert result.level == RiskLevel.SEVERE
    assert result.causes == (Condition.WIND,)
    assert result.load_rule_applied is True


def test_load_rule_flag_false_without_raise():
    result = assess_checkpoint(_sample(wind=40), 10_000)
    assert result.load_rule_applied is False
    assert result.wind == RiskLevel.HIGH


@pytest.mark.parametrize("field", ["wind_mph", "gust_mph", "rain_in_hr", "snow_in_hr"])
@pytest.mark.parametrize("bad", [float("nan"), -1.0])
def test_invalid_weather_raises(field, bad):
    values = {"wind_mph": 0.0, "gust_mph": 0.0, "rain_in_hr": 0.0, "snow_in_hr": 0.0}
    values[field] = bad
    with pytest.raises(ValueError):
        assess_checkpoint(WeatherSample(**values), 0)


@pytest.mark.parametrize("bad", [float("nan"), -1.0])
def test_invalid_load_raises(bad):
    with pytest.raises(ValueError):
        assess_checkpoint(_sample(), bad)


def test_exact_boundaries_at_45_mph():
    assert _level(45.0, 30_000) == RiskLevel.SEVERE
    assert _level(45.0, 30_001) == RiskLevel.NO_TRAVEL


def test_exact_boundaries_at_35_mph():
    assert _level(35.0, 40_001) == RiskLevel.SEVERE
    assert _level(34.99, 40_001) == RiskLevel.MODERATE


def test_just_below_45_mph_is_never_no_travel():
    assert _level(44.9, 30_001) == RiskLevel.HIGH
    assert _level(44.9, 40_001) == RiskLevel.SEVERE


def test_55_mph_no_travel_even_at_max_load():
    assert _level(55, 80_000) == RiskLevel.NO_TRAVEL


def test_three_way_tie_lists_all_causes():
    result = assess_checkpoint(_sample(wind=40, rain=0.3, snow=1.0), 0)
    assert result.level == RiskLevel.HIGH
    assert result.causes == (Condition.WIND, Condition.RAIN, Condition.SNOW)
