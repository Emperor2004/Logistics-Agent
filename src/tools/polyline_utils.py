from typing import List
from src.models.location import Location


# Minimal polyline decoder for OSRM encoded polyline (if ever used).
# For now keep a placeholder that returns the two endpoints when decoding fails.
def decode_polyline_safe(encoded: str, fallback_points: List[Location] = None) -> List[Location]:
    if not encoded:
        return fallback_points or []
    # full decoder is omitted for brevity; decode may be implemented later
    return fallback_points or []