from src.tools.routing_engine import RoutingEngine
from src.models.location import Location


def test_routing_engine_matrix_fallback():
    r = RoutingEngine(base_url="http://invalid-host")
    pts = [Location(lat=19.0, lon=72.0), Location(lat=19.01, lon=72.01)]
    mat = r.get_duration_matrix(pts)
    assert len(mat) == 2
    assert mat[0][1] > 0