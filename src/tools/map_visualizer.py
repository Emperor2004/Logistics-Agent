from typing import List, Tuple
import folium
import requests
import os
import webbrowser
from time import time
from src.config import settings
from src.models.driver import Driver
from src.models.package import Package
from src.models.location import Location
import polyline
import logging

logger = logging.getLogger("map-visualizer")


class MapVisualizer:
    def __init__(self, center_lat=19.075983, center_lon=72.877655, zoom_start=12):
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.zoom_start = zoom_start
        self.last_update = 0
        self.update_interval = 2.0
        self.map_path = os.path.join(os.path.expanduser("~"), "logistics_map.html")
        self.browser_opened = False
        self.osrm_url = settings.OSRM_SERVER_URL.rstrip("/")

    def _coords_from_geojson(self, coords: List[List[float]]) -> List[Tuple[float, float]]:
        # OSRM geojson coords are [lon, lat] -> convert to (lat, lon)
        return [(c[1], c[0]) for c in coords]

    def get_route_geometry(self, start: Location, end: Location) -> List[Tuple[float, float]]:
        """Get route geometry from OSRM, try geojson then polyline (precision 6 then 5)."""
        if not self.osrm_url:
            logger.debug("OSRM URL not configured, skipping road geometry.")
            return [(start.lat, start.lon), (end.lat, end.lon)]

        base = f"{self.osrm_url}/route/v1/driving/{start.lon},{start.lat};{end.lon},{end.lat}"
        params = {"overview": "full", "steps": "false"}
        headers = {"User-Agent": "Logistics-Agent/1.0 (+https://example)"}

        def _call(geometries):
            try:
                resp = requests.get(base, params={**params, "geometries": geometries}, timeout=8, headers=headers)
                logger.debug("OSRM request URL=%s status=%s", resp.url, resp.status_code)
                resp.raise_for_status()
                data = resp.json()
                logger.debug("OSRM response routes=%d", len(data.get("routes", [])))
                return data
            except Exception as e:
                # log limited info to avoid huge output
                logger.debug("OSRM request failed (geometries=%s): %s", geometries, str(e))
                try:
                    logger.debug("Response text (truncated): %s", resp.text[:200])
                except Exception:
                    pass
                return None

        # 1) Try geojson
        data = _call("geojson")
        if data:
            geom = data.get("routes", [{}])[0].get("geometry")
            if geom and isinstance(geom.get("coordinates"), list) and len(geom["coordinates"]) > 1:
                logger.debug("Using geojson geometry, pts=%d", len(geom["coordinates"]))
                return [(c[1], c[0]) for c in geom["coordinates"]]

        # 2) polyline6
        data = _call("polyline6")
        if data:
            encoded = data.get("routes", [{}])[0].get("geometry")
            if encoded:
                try:
                    pts = polyline.decode(encoded, precision=6)
                    if len(pts) > 1:
                        logger.debug("Decoded polyline6 pts=%d", len(pts))
                        return pts
                except Exception as e:
                    logger.debug("polyline6 decode failed: %s", e)

        # 3) polyline (prec5)
        data = _call("polyline")
        if data:
            encoded = data.get("routes", [{}])[0].get("geometry")
            if encoded:
                try:
                    pts = polyline.decode(encoded, precision=5)
                    if len(pts) > 1:
                        logger.debug("Decoded polyline (prec5) pts=%d", len(pts))
                        return pts
                except Exception as e:
                    logger.debug("polyline decode failed: %s", e)

        logger.debug("Falling back to straight line for route.")
        return [(start.lat, start.lon), (end.lat, end.lon)]

    def generate_map(self, drivers: List[Driver], packages: List[Package]) -> bool:
        now = time()
        if now - self.last_update < self.update_interval:
            return False
        self.last_update = now

        m = folium.Map(
            location=[self.center_lat, self.center_lon],
            zoom_start=self.zoom_start,
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri",
            name="Satellite",
        )

        # Add OpenStreetMap layer and layer control
        folium.TileLayer("OpenStreetMap").add_to(m)
        folium.LayerControl().add_to(m)

        # Draw drivers and their routes
        for driver in drivers:
            color = "green" if str(driver.status).lower().endswith("en_route") else "gray"
            folium.CircleMarker(
                location=[driver.location.lat, driver.location.lon],
                radius=6,
                popup=f"Driver: {driver.id}<br>Status: {driver.status}",
                color=color,
                fill=True,
                fill_color=color,
            ).add_to(m)

            # driver.route may be list of Location objects; draw OSRM path between successive stops
            if getattr(driver, "route", None):
                try:
                    route_points = []
                    for i in range(len(driver.route) - 1):
                        a = driver.route[i]
                        b = driver.route[i + 1]
                        seg = self.get_route_geometry(a, b)
                        route_points.extend(seg if i == 0 else seg[1:])  # avoid duplicate points
                    if route_points:
                        folium.PolyLine(locations=route_points, color="green", weight=4, opacity=0.8).add_to(m)
                except Exception:
                    logger.debug("Failed to draw driver route, skipping.")

        # Draw packages and their road routes
        for package in packages:
            folium.Marker(
                location=[package.pickup.lat, package.pickup.lon],
                popup=f"Pickup: {package.id}<br>Status: {package.status}",
                icon=folium.Icon(color="blue", icon="arrow-up"),
            ).add_to(m)

            folium.Marker(
                location=[package.dropoff.lat, package.dropoff.lon],
                popup=f"Dropoff: {package.id}<br>Status: {package.status}",
                icon=folium.Icon(color="red", icon="flag"),
            ).add_to(m)

            try:
                coords = self.get_route_geometry(package.pickup, package.dropoff)
                if coords:
                    folium.PolyLine(locations=coords, color="blue", weight=3, opacity=0.7, dash_array="8").add_to(m)
            except Exception:
                logger.debug("Failed to draw package route, falling back to straight line.")
                folium.PolyLine(locations=[[package.pickup.lat, package.pickup.lon], [package.dropoff.lat, package.dropoff.lon]], color="blue", weight=2).add_to(m)

        # Save and keep single file updated
        m.save(self.map_path)
        return True

    def show_map(self) -> bool:
        if not self.browser_opened and os.path.exists(self.map_path):
            webbrowser.open(f"file://{os.path.realpath(self.map_path)}")
            self.browser_opened = True
        return True