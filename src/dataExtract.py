import json
from pathlib import Path

def extract_known_items(json_path: str | Path) -> list[str]:
    """Collect unique item names from storeMap.json."""
    with open(json_path, "r") as f:
        data = json.load(f)

    items_set = set()
    for node_id, node_data in data.get("nodes", {}).items():
        for item in node_data.get("items", []):
            items_set.add(item.lower().strip())

    return sorted(items_set)

def extract_graph_structure(json_path: str | Path) -> dict:
    """
    Extract only the essential structural data from storeMap.json
    for LLM route planning:
        - nodes: {id: {x, y, section}}
        - edges: {id: {neighbor: distance}}
    Returns a plain Python dict ready for json.dumps().
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    # --- Nodes ---
    nodes = {
        node_id: {
            "x": node_data.get("x"),
            "y": node_data.get("y"),
            "section": node_data.get("section")
        }
        for node_id, node_data in data.get("nodes", {}).items()
    }

    # --- Edges (already correct structure) ---
    edges = data.get("edges", {})

    return {"nodes": nodes, "edges": edges}


if __name__ == "__main__":
    json_path = Path(__file__).resolve().parent.parent / "data" /"storeMap.json"

    items = extract_known_items(json_path)
    graph_struct = extract_graph_structure(json_path)


    print(items, '\n')
    print(graph_struct)
    