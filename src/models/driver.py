from pydantic import BaseModel
from enum import Enum
from typing import List, Optional
from src.models.location import Location
from src.models.package import Package


class DriverStatus(str, Enum):
    IDLE = "idle"
    EN_ROUTE = "en_route"
    DELIVERING = "delivering"


class Driver(BaseModel):
    id: str
    location: Location
    status: DriverStatus = DriverStatus.IDLE
    assigned_packages: List[Package] = []
    route: List[Location] | None = None
    speed_mps: float | None = None  # simulated speed

    def assign_route(self, route: List[Location], packages: List[Package] = None):
        self.route = route
        if packages:
            self.assigned_packages = packages
        self.status = DriverStatus.EN_ROUTE

    def clear_route(self):
        self.route = None
        self.assigned_packages = []
        self.status = DriverStatus.IDLE