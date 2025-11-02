import asyncio
from src.environment.simulator import EnvironmentSimulator
from src.tools.routing_engine import RoutingEngine
from src.tools.route_optimizer import RouteOptimizer
from src.agents.dispatcher import DispatcherAgent
from src.agents.driver_agent import DriverAgent
from src.models.location import Location


def test_dispatch_assigns_package():
    sim = EnvironmentSimulator()
    routing = RoutingEngine(base_url="http://invalid-host")
    optimizer = RouteOptimizer()
    home = Location(lat=19.07, lon=72.87)
    d = DriverAgent(id="d1", start_location=home)
    sim.add_driver(d)
    sim.create_demo_orders()
    dispatcher = DispatcherAgent(routing_engine=routing, optimizer=optimizer, simulator=sim)

    # run one tick of dispatcher
    async def run_once():
        await dispatcher._tick()

    asyncio.run(run_once())
    # after tick, one of the packages should be assigned
    packages = sim.packages
    assert any(p.assigned_to is not None for p in packages)