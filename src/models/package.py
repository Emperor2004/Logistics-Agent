from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional
from src.models.location import Location


class PackageStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"


class Package(BaseModel):
    id: str
    pickup: Location
    dropoff: Location
    created_at: datetime = datetime.utcnow()
    assigned_to: Optional[str] = None
    status: PackageStatus = PackageStatus.PENDING
    priority: int = 1

    def mark_assigned(self, driver_id: str):
        self.assigned_to = driver_id
        self.status = PackageStatus.ASSIGNED

    def mark_in_transit(self):
        self.status = PackageStatus.IN_TRANSIT

    def mark_delivered(self):
        self.status = PackageStatus.DELIVERED