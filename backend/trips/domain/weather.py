from dataclasses import dataclass

CENTIMETERS_PER_INCH = 2.54


@dataclass(frozen=True)
class WeatherSample:
    wind_mph: float
    gust_mph: float
    rain_in_hr: float
    snow_in_hr: float


def cm_to_inches(cm: float) -> float:
    return cm / CENTIMETERS_PER_INCH
