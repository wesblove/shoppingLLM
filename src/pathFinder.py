#!/usr/bin/env python3
"""
pathfinder.py
Executes exactly what the LLM provides 
Expected plan format:
{
    "start": "ENTRY1",
    "waypoints": ["G13", "G07", "E01"],
    "end": "REG",
    "avoid": ["E05","E06"],
}
"""

import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from storeGraph import build_store_graph, find_shortest_path

#json_path = Path(__file__).resolve().parent.parent / "data" /"storeMap.json"

# --------------------------------------------------
def remove_avoids(G: nx.Graph, avoid_nodes):
    """Remove nodes that the LLM instructed to avoid."""
    if avoid_nodes:
        G.remove_nodes_from(avoid_nodes)


# --------------------------------------------------
def append_to_path(path_list, sub_path):
    """Helper: append sub_path while avoiding duplicate join nodes."""
    if not path_list:
        path_list.extend(sub_path)
    else:
        path_list.extend(sub_path[1:])


# --------------------------------------------------
def draw_path(G: nx.Graph, path):
    """Visualize the final route over the store map."""
    pos = {n: (G.nodes[n]["x"], G.nodes[n]["y"]) for n in G.nodes}

    nx.draw(G, pos, node_size=25, node_color="lightgray", edge_color="gainsboro")

    edges = list(zip(path, path[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=edges, width=2.5, edge_color="dodgerblue")
    nx.draw_networkx_nodes(G, pos, nodelist=[path[0]], node_color="limegreen", label="Start")
    nx.draw_networkx_nodes(G, pos, nodelist=[path[-1]], node_color="red", label="End")
    if len(path) > 2:
        nx.draw_networkx_nodes(G, pos, nodelist=path[1:-1], node_color="deepskyblue", label="Waypoints")

    plt.title("Shopping LLM Route Execution")
    plt.axis("off")
    plt.legend()
    plt.show()


# --------------------------------------------------
def execute_plan(plan: dict):
    """Execute the route plan exactly as provided by the LLM."""
    G = build_store_graph()
    remove_avoids(G, plan.get("avoid", []))
    # Normalize plan keys and defaults
    start = plan.get("start")
    end = plan.get("end")
    waypoints_list = plan.get("waypoints", []) or []

    if start is None or end is None:
        raise ValueError("Plan must include 'start' and 'end' nodes.")

    waypoints = [start] + waypoints_list + [end]

    path = []
    total_distance = 0.0

    for a, b in zip(waypoints, waypoints[1:]):
        # find_shortest_path returns (path, distance)
        try:
            sub_path, distance = find_shortest_path(G, a, b)
        except Exception as e:
            # Provide context if an inner lookup fails
            raise ValueError(f"Error finding shortest path from {a} to {b}: {e}")

        append_to_path(path, sub_path)
        # accumulate the returned weighted distance
        try:
            total_distance += float(distance)
        except Exception:
            # If distance isn't numeric for some reason, ignore but warn
            pass

    draw_path(G, path)
    return path, total_distance


# --------------------------------------------------
if __name__ == "__main__":
    # example for quick testing
    sample_plan = {
        "start": "ENTRY1",
        "waypoints": ["G13", "G07", "E01", "BIKES"],
        "end": "REG",
        "avoid": ["E05", "E06"],
    }
    result = execute_plan(sample_plan)
    if isinstance(result, tuple) and len(result) == 2:
        full_path, total_dist = result
        print(f"Executed plan; total nodes in path: {len(full_path)}; total distance: {total_dist}")
    else:
        print("Executed plan.")
