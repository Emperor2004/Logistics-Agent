import asyncio
import logging
from typing import Optional
from src.tools.routing_engine import RoutingEngine
from src.tools.route_optimizer import RouteOptimizer
from src.environment.simulator import EnvironmentSimulator

logger = logging.getLogger("dispatcher")


class DispatcherAgent:
    """
    Simple dispatcher loop:
    - polls the simulator snapshot
    - if unassigned packages exist, builds a distance/duration matrix and requests routes
    - assigns route waypoints to available drivers
    """

    def __init__(self, routing_engine: RoutingEngine, optimizer: RouteOptimizer, simulator: EnvironmentSimulator):
        self.routing = routing_engine
        self.optimizer = optimizer
        self.simulator = simulator
        self._running = False

    async def run_loop(self, poll_interval: float = 1.0):
        self._running = True
        logger.info("Dispatcher loop started.")
        while self._running:
            try:
                await self._tick()
            except Exception as e:
                logger.exception("Dispatcher tick failed: %s", e)
            await asyncio.sleep(poll_interval)

    async def _tick(self):
        snap = self.simulator.snapshot()
        drivers = [d for d in snap["drivers"] if d.status == d.status.IDLE]
        packages = [p for p in snap["packages"] if p.status == p.status.PENDING]

        if not drivers or not packages:
            return

        # Build points list as [depot (driver pos), pickups..., dropoffs...]
        # For simplicity, we plan per driver: assign nearest package to each idle driver
        for d_agent in self.simulator.drivers:
            if d_agent.driver.status != d_agent.driver.status.IDLE:
                continue
            if not packages:
                break
            # pick nearest package (pickup leg only) using haversine
            driver_loc = d_agent.driver.location
            packages.sort(key=lambda p: driver_loc.haversine_distance_m(p.pickup))
            pkg = packages.pop(0)
            # request route for driver->pickup->dropoff (use routing engine)
            r1 = self.routing.get_route(driver_loc, pkg.pickup)
            r2 = self.routing.get_route(pkg.pickup, pkg.dropoff)
            # assemble simple route: driver loc -> pickup -> dropoff
            route_points = [driver_loc, pkg.pickup, pkg.dropoff]
            d_agent.assign_route(route_points, packages=[pkg])
            pkg.mark_assigned(d_agent.driver.id)
            logger.info("Assigned package %s to driver %s", pkg.id, d_agent.driver.id)