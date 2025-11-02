from pydantic import BaseModel
from math import radians, sin, cos, sqrt, atan2


class Location(BaseModel):
    lat: float
    lon: float
    address: str | None = None

    def haversine_distance_m(self, other: "Location") -> float:
        # returns distance in meters
        R = 6371000.0
        lat1, lon1, lat2, lon2 = map(radians, (self.lat, self.lon, other.lat, other.lon))
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c