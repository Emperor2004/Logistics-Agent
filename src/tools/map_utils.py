from typing import List, Tuple, Dict
from src.models.location import Location
from src.models.driver import Driver
from src.models.package import Package

class MapVisualizer:
    """ASCII map visualizer for Mumbai region"""
    
    # Mumbai region bounds (approx)
    MIN_LAT = 19.0
    MAX_LAT = 19.2
    MIN_LON = 72.8
    MAX_LON = 73.0
    
    def __init__(self, width: int = 50, height: int = 20):
        self.width = width
        self.height = height
        self.grid = [[" " for _ in range(width)] for _ in range(height)]
    
    def _coord_to_grid(self, lat: float, lon: float) -> Tuple[int, int]:
        """Convert geo coordinates to grid positions"""
        x = int((lon - self.MIN_LON) / (self.MAX_LON - self.MIN_LON) * (self.width - 1))
        y = int((self.MAX_LAT - lat) / (self.MAX_LAT - self.MIN_LAT) * (self.height - 1))
        return max(0, min(x, self.width-1)), max(0, min(y, self.height-1))
    
    def generate_map(self, drivers: List[Driver], packages: List[Package]) -> str:
        """Generate ASCII map with drivers and packages"""
        # Reset grid
        self.grid = [[" " for _ in range(self.width)] for _ in range(self.height)]
        
        # Add border
        for x in range(self.width):
            self.grid[0][x] = "─"
            self.grid[self.height-1][x] = "─"
        for y in range(self.height):
            self.grid[y][0] = "│"
            self.grid[y][self.width-1] = "│"
        
        # Add corners
        self.grid[0][0] = "┌"
        self.grid[0][self.width-1] = "┐"
        self.grid[self.height-1][0] = "└"
        self.grid[self.height-1][self.width-1] = "┘"
        
        # Add major roads/landmarks
        self.add_landmarks()
        
        # Plot drivers
        for driver in drivers:
            x, y = self._coord_to_grid(driver.location.lat, driver.location.lon)
            self.grid[y][x] = "🚗" if driver.status == "en_route" else "P"
        
        # Plot packages
        for pkg in packages:
            # Plot pickup points
            x, y = self._coord_to_grid(pkg.pickup.lat, pkg.pickup.lon)
            self.grid[y][x] = "📍"
            # Plot delivery points
            x, y = self._coord_to_grid(pkg.dropoff.lat, pkg.dropoff.lon)
            self.grid[y][x] = "📦"
        
        # Convert grid to string
        map_str = "\n".join("".join(row) for row in self.grid)
        
        # Add legend
        legend = (
            "\nLegend:\n"
            "🚗 Active Driver   P Parked Driver\n"
            "📍 Pickup Point   📦 Delivery Point\n"
        )
        
        return map_str + legend
    
    def add_landmarks(self):
        """Add major Mumbai landmarks/roads to map"""
        landmarks = {
            "CST": (18.9398, 72.8354),
            "BKC": (19.0607, 72.8681),
            "Andheri": (19.1136, 72.8697),
            "Bandra": (19.0596, 72.8295)
        }
        
        for name, (lat, lon) in landmarks.items():
            x, y = self._coord_to_grid(lat, lon)
            if 0 <= y < self.height and 0 <= x < self.width:
                self.grid[y][x] = "+"