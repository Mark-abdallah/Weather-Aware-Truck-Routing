from dataclasses import dataclass
from datetime import datetime

from trips.domain.assessment import Assessment, assess_checkpoint
from trips.domain.forecast import nearest_hour_index
from trips.domain.weather import WeatherSample
from trips.services.ports import HourlyForecast


@dataclass(frozen=True)
class AssessedSample:
    sample: WeatherSample
    assessment: Assessment


def assess_at(forecast: HourlyForecast, when: datetime, load_lb: float) -> AssessedSample:
    sample = forecast.samples[nearest_hour_index(when, forecast.times)]
    return AssessedSample(sample, assess_checkpoint(sample, load_lb))
