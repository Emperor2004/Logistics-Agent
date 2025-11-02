from pydantic import BaseModel
from typing import List
from src.models.location import Location


class Route(BaseModel):
    stops: List[Location]
    total_duration_s: float | None = None
    total_distance_m: float | None = None