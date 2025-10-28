# storeGraph.py
# Builds a NetworkX graph from the storeMap.json structure.
# Each node = store section or aisle
# Each edge = walkable path with distance weight

import json
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

def build_store_graph(json_path: str):
    """Load storeMap.json and build a weighted NetworkX graph."""
    with open(json_path, "r") as f:
        data = json.load(f)

    nodes = data["nodes"]
    edges = data["edges"]

    G = nx.Graph()

    # --- Add Nodes ---
    for node_id, props in nodes.items():
        G.add_node(
            node_id,
            x=props["x"],
            y=props["y"],
            section=props.get("section", ""),
            items=props.get("items", [])
        )

    # --- Add Edges ---
    for src, neighbors in edges.items():
        for dest, dist in neighbors.items():
            # Avoid duplicate edges (NetworkX handles fine, but this ensures clarity)
            if not G.has_edge(src, dest):
                G.add_edge(src, dest, weight=float(dist))

    return G


def plot_store_graph(G):
    """Visualize the store layout using node coordinates."""
    pos = {n: (G.nodes[n]["x"], G.nodes[n]["y"]) for n in G.nodes}
    plt.figure(figsize=(14, 10))
    nx.draw(
        G, pos,
        with_labels=True,
        node_size=80,
        node_color="lightblue",
        edge_color="gray",
        font_size=6
    )
    plt.title("Store Graph Layout")
    plt.show()


def find_section_by_item(G, item_name: str):
    """Find the node(s) that contain a specific item."""
    item_name = item_name.lower()
    matches = []
    for node, attrs in G.nodes(data=True):
        for item in attrs.get("items", []):
            if item_name in item.lower():
                matches.append((node, attrs["section"]))
    return matches


def find_shortest_path(G, start_node: str, end_node: str):
    """Return the shortest path and total distance between two nodes."""
    if start_node not in G or end_node not in G:
        raise ValueError("Invalid node(s) provided.")
    path = nx.shortest_path(G, source=start_node, target=end_node, weight="weight")
    distance = nx.shortest_path_length(G, source=start_node, target=end_node, weight="weight")
    return path, distance


# --- Example usage ---
if __name__ == "__main__":
    json_path = Path(__file__).parent / "storeMap.json"
    G = build_store_graph(json_path)

    print(f"Graph built with {len(G.nodes)} nodes and {len(G.edges)} edges.")

    # Example queries
    print("\nSearching for 'milk'...")
    milk_nodes = find_section_by_item(G, "milk")
    for n, sec in milk_nodes:
        print(f"  Found in {sec} ({n})")

    # Example route: Entrance to Electronics
    path, dist = find_shortest_path(G, "ENTRY1", "E06")
    print(f"\nShortest path ENTRY1 → E06: {path} (Total distance: {dist})")

    # Optional visualization
    # plot_store_graph(G)
