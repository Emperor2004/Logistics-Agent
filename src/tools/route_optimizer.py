from typing import List, Tuple
from src.models.location import Location
import logging

logger = logging.getLogger("optimizer")


class RouteOptimizer:
    """
    Lightweight optimizer. Tries to use OR-Tools if installed; otherwise uses a greedy nearest-neighbor.
    Input: duration matrix (seconds) and number of vehicles.
    Output: list of routes (each route is a list of indexes into input points).
    """

    def __init__(self):
        # lazy import for OR-Tools
        try:
            from ortools.constraint_solver import pywrapcp, routing_enums_pb2  # type: ignore
            self.ortools_available = True
            self.pywrapcp = pywrapcp
            self.routing_enums_pb2 = routing_enums_pb2
        except Exception:
            self.ortools_available = False

    def solve(self, duration_matrix: List[List[float]], vehicle_count: int = 1, depot: int = 0) -> List[List[int]]:
        n = len(duration_matrix)
        if n == 0:
            return [[] for _ in range(vehicle_count)]

        if self.ortools_available and n <= 200:
            return self._solve_ortools(duration_matrix, vehicle_count, depot)
        else:
            return self._solve_greedy(duration_matrix, vehicle_count, depot)

    def _solve_greedy(self, mat: List[List[float]], vehicle_count: int, depot: int) -> List[List[int]]:
        n = len(mat)
        unvisited = set(range(n))
        unvisited.discard(depot)
        routes = [[] for _ in range(vehicle_count)]
        for v in range(vehicle_count):
            cur = depot
            routes[v].append(depot)
            while unvisited:
                # pick nearest
                next_node = min(unvisited, key=lambda x: mat[cur][x])
                routes[v].append(next_node)
                unvisited.discard(next_node)
                cur = next_node
                # simple balancing: break sometimes
                if len(routes[v]) > max(2, n // vehicle_count + 1):
                    break
        return routes

    def _solve_ortools(self, mat: List[List[float]], vehicle_count: int, depot: int) -> List[List[int]]:
        # Basic VRP with time/duration cost only
        pywrapcp = self.pywrapcp
        routing_enums_pb2 = self.routing_enums_pb2
        n = len(mat)
        manager = pywrapcp.RoutingIndexManager(n, vehicle_count, depot)
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            i = manager.IndexToNode(from_index)
            j = manager.IndexToNode(to_index)
            return int(mat[i][j] * 1000)  # scaled

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # set search parameters
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        search_parameters.time_limit.seconds = 5

        solution = routing.SolveWithParameters(search_parameters)
        routes = [[] for _ in range(vehicle_count)]
        if solution:
            for v in range(vehicle_count):
                index = routing.Start(v)
                while not routing.IsEnd(index):
                    node = manager.IndexToNode(index)
                    routes[v].append(int(node))
                    index = solution.Value(routing.NextVar(index))
                # add depot end if needed
                end_node = manager.IndexToNode(index)
                routes[v].append(int(end_node))
        else:
            logger.warning("OR-Tools solver returned no solution, falling back to greedy.")
            return self._solve_greedy(mat, vehicle_count, depot)
        return routes