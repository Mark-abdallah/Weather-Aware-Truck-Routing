import pytest

from trips.domain.risk import RiskLevel, classify_rain, classify_snow, classify_wind
from trips.domain.weather import cm_to_inches

L, M, H, S, N = (
    RiskLevel.LOW,
    RiskLevel.MODERATE,
    RiskLevel.HIGH,
    RiskLevel.SEVERE,
    RiskLevel.NO_TRAVEL,
)


def test_levels_are_scored():
    assert [level.value for level in RiskLevel] == [0, 1, 2, 3, 4]


@pytest.mark.parametrize(
    "value,expected",
    [
        (0, L),
        (24.99, L),
        (25, M),
        (34.99, M),
        (35, H),
        (44.99, H),
        (45, S),
        (54.99, S),
        (55, N),
    ],
)
def test_wind(value, expected):
    assert classify_wind(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (0, L),
        (0.0999, L),
        (0.10, M),
        (0.2499, M),
        (0.25, H),
        (0.4999, H),
        (0.50, S),
        (1.00, S),
        (1.0001, N),
    ],
)
def test_rain(value, expected):
    assert classify_rain(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (0, L),
        (0.499, L),
        (0.5, M),
        (0.999, M),
        (1.0, H),
        (1.999, H),
        (2.0, S),
        (3.0, S),
        (3.01, N),
    ],
)
def test_snow(value, expected):
    assert classify_snow(value) == expected


def test_cm_to_inches():
    assert cm_to_inches(2.54) == pytest.approx(1.0)
    assert cm_to_inches(0) == 0
