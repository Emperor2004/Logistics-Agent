import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import asyncio
import logging
from datetime import datetime
import os

from src.config import settings
from src.environment.simulator import EnvironmentSimulator
from src.tools.routing_engine import RoutingEngine
from src.tools.route_optimizer import RouteOptimizer
from src.agents.dispatcher import DispatcherAgent
from src.agents.driver_agent import DriverAgent
from src.models.location import Location
from src.tools.map_visualizer import MapVisualizer  # Update import

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("logistics-agent")

def format_coordinates(lat: float, lon: float) -> str:
    """Format coordinates with cardinal directions"""
    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"
    return f"{abs(lat):.4f}°{ns}, {abs(lon):.4f}°{ew}"

async def print_status(simulator: EnvironmentSimulator):
    """Periodically print simulation status with enhanced formatting"""
    map_viz = MapVisualizer()
    first_update = True
    
    while True:
        snapshot = simulator.snapshot()
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # Generate map and show only on first update
        if map_viz.generate_map(
            drivers=[d.driver for d in simulator.drivers],
            packages=simulator.packages
        ):
            if first_update:
                map_viz.show_map()
                first_update = False
                logger.info(f"🗺️  Map opened in browser at {current_time}")
            else:
                logger.info(f"🗺️  Map updated at {current_time}")

        print("\033[2J\033[H")  # Clear screen
        logger.info("\n" + "="*70)
        logger.info(f"🕒 Simulation Status at {current_time}")
        logger.info("="*70)
        
        # Driver status section with progress indicators
        logger.info("\n🚚 DRIVERS:")
        active_drivers = 0
        for driver in snapshot["drivers"]:
            status_emoji = "🟢" if driver.status == "en_route" else "⚪"
            coords = format_coordinates(driver.location.lat, driver.location.lon)
            
            # Calculate progress bar for en_route drivers
            progress = ""
            if driver.status == "en_route" and driver.route:
                current_loc = driver.location
                next_stop = driver.route[0]  # Next waypoint
                total_dist = current_loc.haversine_distance_m(next_stop)
                remaining = current_loc.haversine_distance_m(next_stop)
                progress_pct = max(0, min(100, (1 - remaining/total_dist) * 100))
                progress = f"[{'=' * int(progress_pct/10)}{'-' * (10-int(progress_pct/10))}] {progress_pct:.0f}%"
            
            logger.info(
                f"{status_emoji} {driver.id:<8} | "
                f"Status: {driver.status:<10} | "
                f"Position: {coords:<30} "
                f"{progress}"
            )
            
            if driver.status != "idle":
                active_drivers += 1
        
        # Package status section with pickup/delivery locations
        logger.info("\n📦 PACKAGES:")
        delivered = 0
        in_transit = 0
        pending = 0
        
        for package in snapshot["packages"]:
            if package.status == "delivered":
                delivered += 1
            elif package.status == "in_transit":
                in_transit += 1
            elif package.status == "pending":
                pending += 1
            
            status_emoji = {
                "pending": "⌛",
                "assigned": "🔄",
                "in_transit": "🚚",
                "delivered": "✅"
            }.get(package.status, "❓")
            
            pickup_loc = format_coordinates(package.pickup.lat, package.pickup.lon)
            dropoff_loc = format_coordinates(package.dropoff.lat, package.dropoff.lon)
            
            logger.info(
                f"{status_emoji} {package.id:<8} | "
                f"Status: {package.status:<10} | "
                f"Driver: {package.assigned_to or 'unassigned':<10} | "
                f"📍 {pickup_loc} → {dropoff_loc}"
            )
        
        # Enhanced summary section
        logger.info("\n📊 SUMMARY:")
        logger.info(f"Active Drivers: {active_drivers}/{len(snapshot['drivers'])}")
        logger.info(f"Packages - ✅ Delivered: {delivered}, 🚚 In Transit: {in_transit}, ⌛ Pending: {pending}")
        
        logger.info("="*70 + "\n")
        await asyncio.sleep(5)

async def main():
    logger.info("Starting Logistics Agent simulation...")
    
    routing = RoutingEngine()
    optimizer = RouteOptimizer()
    simulator = EnvironmentSimulator()

    # Create drivers
    drivers = []
    home = Location(lat=19.075983, lon=72.877655)  # Mumbai central point
    for i in range(min(settings.MAX_DRIVERS, 4)):
        d = DriverAgent(id=f"driver_{i+1}", start_location=home)
        drivers.append(d)
        simulator.add_driver(d)
        logger.info(f"Created driver {d.driver.id} at location ({home.lat:.4f}, {home.lon:.4f})")

    dispatcher = DispatcherAgent(routing_engine=routing, optimizer=optimizer, simulator=simulator)
    logger.info("Dispatcher agent initialized")

    simulator.create_demo_orders()
    logger.info(f"Created {len(simulator.packages)} demo orders")

    # Run all components concurrently
    logger.info("Starting simulation loops...")
    try:
        await asyncio.gather(
            simulator.run_loop(),
            dispatcher.run_loop(poll_interval=1.0),
            print_status(simulator)
        )
    except Exception as e:
        logger.error(f"Simulation error: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")