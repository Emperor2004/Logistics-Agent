# src/environment.py
from datetime import datetime, timedelta
from typing import List
from .models import Driver, Package, Location

class Environment:
    """Manages the state of the simulation."""
    def __init__(self):
        self.drivers: List[Driver] = []
        self.packages: List[Package] = []
        self.current_time = datetime.now()
        print("🌍 Environment initialized.")
        self.generate_initial_state()

    def generate_initial_state(self):
        """Creates a starting scenario with drivers and packages."""
        # A central depot location in Kothrud, Pune
        depot_location = Location(latitude=18.5074, longitude=73.8077, address="Kothrud Depot, Pune")

        # Create 2 initial drivers starting at the depot
        self.drivers.append(Driver(id="Driver_01", current_location=depot_location))
        self.drivers.append(Driver(id="Driver_02", current_location=depot_location))

        # Create 5 initial packages for delivery in and around Kothrud
        self.packages.append(Package(id="PKG_001", destination=Location(latitude=18.5196, longitude=73.8567, address="Shaniwar Wada")))
        self.packages.append(Package(id="PKG_002", destination=Location(latitude=18.4988, longitude=73.8213, address="Vanaz Corner")))
        self.packages.append(Package(id="PKG_003", destination=Location(latitude=18.5085, longitude=73.7845, address="Bhusari Colony")))
        self.packages.append(Package(id="PKG_004", destination=Location(latitude=18.5323, longitude=73.8055, address="Chaturshringi Temple")))
        self.packages.append(Package(id="PKG_005", destination=Location(latitude=18.4877, longitude=73.8252, address="Sinhagad Road")))

        print(f"✅ Initial state generated with {len(self.drivers)} drivers and {len(self.packages)} packages.")

    def tick(self):
        """Advances the simulation by one time step."""
        self.current_time += timedelta(minutes=1)
        # In future phases, this method will handle driver movement, event generation, etc.
        print(f"---------------------\n🕒 Tick! Current Time: {self.current_time.strftime('%H:%M:%S')}")

    def get_status_report(self):
        """Prints the current state of the environment."""
        print("\n--- Fleet Status ---")
        for driver in self.drivers:
            print(f"  - {driver.id}: at ({driver.current_location.latitude:.4f}, {driver.current_location.longitude:.4f}) | Status: {driver.status}")

        print("\n--- Package Status ---")
        pending_packages = [p for p in self.packages if p.status == 'pending']
        if pending_packages:
            print(f"  - {len(pending_packages)} packages pending delivery.")
        else:
            print("  - All packages are on their way or delivered!")