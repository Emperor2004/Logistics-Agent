import math
from src.models.location import Location


def test_haversine_distance():
    a = Location(lat=19.0, lon=72.0)
    b = Location(lat=19.0001, lon=72.0001)
    d = a.haversine_distance_m(b)
    assert d > 0
    # small distance approximates ~15m for these deltas
    assert d < 200