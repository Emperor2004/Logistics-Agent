import asyncio
import logging
from typing import List
from datetime import datetime
from src.models.driver import Driver
from src.models.package import Package
from src.models.location import Location
from src.models.driver import Driver as DriverModel
from src.agents.driver_agent import DriverAgent

logger = logging.getLogger("simulator")


class EnvironmentSimulator:
    """
    Light-weight simulation loop. Keeps drivers and packages lists.
    Drivers must be DriverAgent instances (they hold DriverModel internally).
    """

    def __init__(self):
        self.current_time = datetime.utcnow()
        self.drivers: List[DriverAgent] = []
        self.packages: List[Package] = []
        self._tick_seconds = 1.0

    def add_driver(self, driver_agent: DriverAgent):
        self.drivers.append(driver_agent)

    def add_package(self, pkg: Package):
        self.packages.append(pkg)

    def create_demo_orders(self):
        # produce a couple of demo packages (nearby locations)
        p1 = Package(
            id="pkg_1",
            pickup=Location(lat=19.07283, lon=72.88261),
            dropoff=Location(lat=19.08283, lon=72.89261),
        )
        p2 = Package(
            id="pkg_2",
            pickup=Location(lat=19.06283, lon=72.87261),
            dropoff=Location(lat=19.09283, lon=72.90261),
        )
        self.add_package(p1)
        self.add_package(p2)

    async def run_loop(self):
        logger.info("Simulator loop started.")
        while True:
            self.current_time = datetime.utcnow()
            await self._tick()
            await asyncio.sleep(self._tick_seconds)

    async def _tick(self):
        # progress each driver a bit
        for d in list(self.drivers):
            try:
                await d.tick(self._tick_seconds)
            except Exception as e:
                logger.exception("Driver tick failed: %s", e)

    def snapshot(self):
        # shallow copies suitable for Dispatcher perception
        return {
            "time": self.current_time,
            "drivers": [d.driver for d in self.drivers],
            "packages": list(self.packages),
        }