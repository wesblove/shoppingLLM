#!/usr/bin/env python3
"""
pathfinder.py
Executes exactly what the LLM provides — no reasoning, no optimization, no validation.

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

    waypoints = [plan["start"]] + plan["waypoints"] + [plan["end"]]

    path = []
    for a, b in zip(waypoints, waypoints[1:]):
        sub = find_shortest_path(G, a, b)
        append_to_path(path, sub)

    draw_path(G, path)


# --------------------------------------------------
if __name__ == "__main__":
    # example for quick testing
    sample_plan = {
        "start": "ENTRY1",
        "waypoints": ["G13", "G07", "E01"],
        "end": "REG",
        "avoid": ["E05", "E06"],
    }
    execute_plan(sample_plan)
