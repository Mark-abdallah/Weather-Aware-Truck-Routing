import pytest

from trips.clients.flexible_polyline import decode
from trips.domain.geometry import LatLon

EXPECTED = [
    LatLon(50.10228, 8.69821),
    LatLon(50.10201, 8.69567),
    LatLon(50.10063, 8.69150),
    LatLon(50.09878, 8.68752),
]


def test_decodes_2d_reference_polyline() -> None:
    assert decode("BFoz5xJ67i1B1B7PzIhaxL7Y") == EXPECTED


def test_decodes_3d_polyline_ignoring_third_dimension() -> None:
    assert decode("BlBoz5xJ67i1BU1B7PUzIhaUxL7YU") == EXPECTED


@pytest.mark.parametrize("encoded", ["", "C", "BF!", "BFo", "BFoz5xJ"])
def test_rejects_malformed_input(encoded: str) -> None:
    with pytest.raises(ValueError):
        decode(encoded)
