# src/models.py
from pydantic import BaseModel, Field
from typing import List, Optional

class Location(BaseModel):
    """Represents a geographic location."""
    latitude: float
    longitude: float
    address: Optional[str] = None

class Package(BaseModel):
    """Represents a package to be delivered."""
    id: str
    destination: Location
    status: str = "pending" # pending, in_transit, delivered, failed

class Driver(BaseModel):
    """Represents a delivery driver."""
    id: str
    current_location: Location
    status: str = "idle" # idle, on_delivery, returning
    route: List[Package] = Field(default_factory=list)