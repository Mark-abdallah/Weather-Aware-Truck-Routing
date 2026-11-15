from uuid import uuid4

import pytest

from trips.repositories.trip_repository import TripRepository


@pytest.mark.django_db
def test_saved_trip_can_be_read_back() -> None:
    repository = TripRepository()
    saved = repository.save({"interval_mi": 25}, {"plan": {"routes": []}})
    loaded = repository.get(saved.trip_id)
    assert loaded == saved
    assert loaded.inputs == {"interval_mi": 25}
    assert loaded.computed_at is not None


@pytest.mark.django_db
def test_unknown_trip_returns_none() -> None:
    assert TripRepository().get(uuid4()) is None
