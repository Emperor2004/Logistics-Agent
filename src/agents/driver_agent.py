import asyncio
import logging
from typing import List, Optional
from src.models.driver import Driver, DriverStatus
from src.models.location import Location
from src.models.package import Package
from src.config import settings

logger = logging.getLogger("driver-agent")


class DriverAgent:
    """
    Lightweight driver agent that simulates motion along an assigned route.
    Holds an internal Driver model as .driver
    """

    def __init__(self, id: str, start_location: Location):
        self.driver = Driver(id=id, location=start_location, status=DriverStatus.IDLE, speed_mps=settings.DRIVER_SPEED_MPS)
        self._cursor = 0  # index into route stops
        self._route: List[Location] | None = None
        self._packages: List[Package] = []

    async def tick(self, dt_seconds: float):
        # move along route if assigned
        if not self._route or self._cursor >= len(self._route):
            if self.driver.status != DriverStatus.IDLE:
                self.driver.status = DriverStatus.IDLE
            return

        target = self._route[self._cursor]
        # move toward target at speed
        dist = self.driver.location.haversine_distance_m(target)
        step = (self.driver.speed_mps or settings.DRIVER_SPEED_MPS) * dt_seconds
        if step >= dist or dist < 1.0:
            # arrive
            self.driver.location = target
            self._cursor += 1
            logger.debug("%s reached waypoint %d/%d", self.driver.id, self._cursor, len(self._route))
            # handle package delivery/pickup simplistically
            # TODO: tie to actual Package objects for pickup/dropoff events
        else:
            # interpolate roughly along great-circle: fraction f
            f = step / dist
            lat = self.driver.location.lat + (target.lat - self.driver.location.lat) * f
            lon = self.driver.location.lon + (target.lon - self.driver.location.lon) * f
            self.driver.location = Location(lat=lat, lon=lon)

    def assign_route(self, route: List[Location], packages: Optional[List[Package]] = None):
        self._route = route
        self._cursor = 0
        self._packages = packages or []
        self.driver.status = DriverStatus.EN_ROUTE

    def clear_route(self):
        self._route = None
        self._cursor = 0
        self._packages = []
        self.driver.status = DriverStatus.IDLE