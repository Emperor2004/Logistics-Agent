import requests
from typing import List, Tuple
from src.models.location import Location
from src.config import settings
import logging

logger = logging.getLogger("routing")


class RoutingEngine:
    """
    Thin wrapper over OSRM HTTP API (synchronous).
    Methods return seconds for durations and meters for distances where available.
    """

    def __init__(self, base_url: str | None = None, timeout: int = 5):
        self.base_url = base_url or settings.OSRM_SERVER_URL.rstrip("/")
        self.timeout = timeout

    def _coords_str(self, locs: List[Location]) -> str:
        return ";".join(f"{l.lon},{l.lat}" for l in locs)

    def get_route(self, origin: Location, destination: Location) -> dict:
        url = f"{self.base_url}/route/v1/driving/{origin.lon},{origin.lat};{destination.lon},{destination.lat}"
        params = {"overview": "false", "steps": "false", "annotations": "false"}
        try:
            r = requests.get(url, params=params, timeout=self.timeout)
            r.raise_for_status()
            data = r.json()
            route = data.get("routes", [{}])[0]
            return {
                "duration_s": route.get("duration"),
                "distance_m": route.get("distance"),
            }
        except Exception as e:
            logger.debug("OSRM route call failed: %s", e)
            # graceful fallback: use haversine estimate
            distance = origin.haversine_distance_m(destination)
            # assume average speed 40 km/h => 11.11 m/s
            duration = distance / 11.11 if distance > 0 else 0
            return {"duration_s": duration, "distance_m": distance}

    def get_duration_matrix(self, points: List[Location]) -> List[List[float]]:
        """
        Uses OSRM table endpoint to get duration matrix (seconds). Falls back to haversine.
        """
        if len(points) < 2:
            return [[0.0]]
        coords = self._coords_str(points)
        url = f"{self.base_url}/table/v1/driving/{coords}"
        params = {"annotations": "duration"}
        try:
            r = requests.get(url, params=params, timeout=self.timeout)
            r.raise_for_status()
            data = r.json()
            durations = data.get("durations")
            if durations:
                return durations
        except Exception as e:
            logger.debug("OSRM table call failed: %s", e)

        # fallback: compute pairwise haversine / 11.11 m/s
        n = len(points)
        mat = [[0.0 for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j:
                    mat[i][j] = 0.0
                else:
                    d = points[i].haversine_distance_m(points[j])
                    mat[i][j] = d / 11.11
        return mat