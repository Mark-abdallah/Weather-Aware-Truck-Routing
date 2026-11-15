from trips.domain.geometry import LatLon

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
CHAR_VALUES = {char: value for value, char in enumerate(ALPHABET)}
SUPPORTED_VERSION = 1
CHUNK_BITS = 5
CHUNK_VALUE_MASK = 0x1F
CONTINUATION_BIT = 0x20
PRECISION_MASK = 0xF
THIRD_DIM_SHIFT = 4
THIRD_DIM_MASK = 0x7
HEADER_LENGTH = 2


def decode(encoded: str) -> list[LatLon]:
    values = _unsigned_varints(encoded)
    if len(values) < HEADER_LENGTH or values[0] != SUPPORTED_VERSION:
        raise ValueError("Unsupported or missing flexible polyline header")
    header = values[1]
    dimensions = 3 if (header >> THIRD_DIM_SHIFT) & THIRD_DIM_MASK else 2
    deltas = [_zigzag_decode(value) for value in values[HEADER_LENGTH:]]
    if len(deltas) % dimensions:
        raise ValueError("Flexible polyline has an incomplete coordinate")
    return _accumulate(deltas, dimensions, 10 ** (header & PRECISION_MASK))


def _unsigned_varints(encoded: str) -> list[int]:
    values, value, shift = [], 0, 0
    for chunk in map(_char_value, encoded):
        value |= (chunk & CHUNK_VALUE_MASK) << shift
        shift += CHUNK_BITS
        if not chunk & CONTINUATION_BIT:
            values.append(value)
            value = shift = 0
    if shift:
        raise ValueError("Flexible polyline ends mid-value")
    return values


def _char_value(char: str) -> int:
    if char not in CHAR_VALUES:
        raise ValueError(f"Invalid flexible polyline character {char!r}")
    return CHAR_VALUES[char]


def _zigzag_decode(value: int) -> int:
    return ~(value >> 1) if value & 1 else value >> 1


def _accumulate(deltas: list[int], dimensions: int, scale: int) -> list[LatLon]:
    lat = lon = 0
    points = []
    for start in range(0, len(deltas), dimensions):
        lat += deltas[start]
        lon += deltas[start + 1]
        points.append(LatLon(lat / scale, lon / scale))
    return points
