# --------------------------------------------------
# LLMAssistant.py
# Reasoning + Planning Layer for Shopping LLM
# --------------------------------------------------
# Responsibilities:
#   1. Parse user text (items + constraints)
#   2. Map items → store nodes
#   3. Use LLM reasoning to build a route plan
#   4. Execute via pathFinder
#   5. Summarize results
# --------------------------------------------------

import json
from openai import OpenAI
from pathlib import Path
from dataExtract import extract_known_items, extract_graph_structure
from storeGraph import build_store_graph, find_section_by_item
from pathFinder import execute_plan


class LLMAssistant:
    def __init__(self, model="gpt-4o-mini", debug=False):
        """Initialize model and load store graph."""
        self.model = model
        self.debug = debug
        self.client = OpenAI()
        self.G = build_store_graph()

    # --------------------------------------------------
    def parse_user_input(self, user_text):
        """
        Step 1: Extract items and constraints from natural language.
        """
        store_items = extract_known_items(json_path)
        messages = [
            {"role": "system", "content": "You are an assistant that extracts structured data from shopping requests. Only include items that exist in the provided store list."},
            {
                "role": "user",
                "content": f"""
        The store's valid item list is:
        {json.dumps(store_items, indent=2)}

        If a requested item is not in this list, replace it with the closest logical match from the list.
        Now parse this user request into JSON with keys 'items' and 'constraints':

        {user_text}
        """
            }
        ]


        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0
        )

        content = response.choices[0].message.content
        print("DEBUG: Model raw response:", repr(content))
        if content.startswith("```"):
            content = content.strip("`")       # remove backticks
            content = content.replace("json", "", 1).strip()  # remove optional 'json' language tag

        if self.debug:
            print("DEBUG: Cleaned model output:", repr(content))

        parsed = json.loads(content)

        if self.debug:
            print("Parsed input:", parsed)

        return parsed

    # --------------------------------------------------
    def map_items_to_nodes(self, items):
        """
        Step 2: Map item names to node IDs in the store graph.
        """
        mapped_nodes = []
        for item in items:
            matches = find_section_by_item(self.G, item)
            if matches:
                mapped_nodes.append(matches[0][0])  # use first matching node
        if self.debug:
            print("Mapped nodes:", mapped_nodes)
        return mapped_nodes

    # --------------------------------------------------
    def generate_plan(self, mapped_nodes, constraints):
        """
        Step 3: Use the LLM to create an ordered route plan.
        """
        context = {
            "mapped_nodes": mapped_nodes,
            "constraints": constraints
        }

        graph_struct = extract_graph_structure(json_path)

        system_prompt = """
        You are a navigation planner for a grocery store.
        Given a set of store node IDs to visit and constraints,
        create an optimal JSON plan in this format:
        {
            "start": "ENTRY1",
            "waypoints": ["D03", "E02", "B04"],
            "end": "REG",
            "avoid": ["E05"]
        }
        Only return JSON — no explanations.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"This graph provides the store node IDs, along with x and y coordinates, and edges with weights. This is how you will determine the ideal route.: {graph_struct}"},
            {"role": "user", "content": json.dumps(context)}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0
        )

        plan = json.loads(response.choices[0].message.content)

        if self.debug:
            print("Generated plan:", json.dumps(plan, indent=2))

        return plan

    # --------------------------------------------------
    def execute_plan(self, plan):
        """
        Step 4: Pass the plan to pathFinder for execution.
        """
        path, total_distance = execute_plan(plan)
        if self.debug:
            print("Path executed:", path)
            print("Total distance:", total_distance)
        return path, total_distance

    # --------------------------------------------------
    def summarize_results(self, path, total_distance):
        """
        Step 5: Summarize the route for user output.
        """
        summary = f"Your route visits {len(path)} nodes with a total distance of {total_distance:.1f} units."
        if self.debug:
            print(summary)
        return summary

    # --------------------------------------------------
    def run_session(self, user_text):
        """
        Complete pipeline: parse → map → plan → execute → summarize.
        """
        parsed = self.parse_user_input(user_text)
        items = parsed["items"]
        constraints = parsed.get("constraints", {})

        mapped_nodes = self.map_items_to_nodes(items)
        plan = self.generate_plan(mapped_nodes, constraints)
        path, total_distance = self.execute_plan(plan)
        summary = self.summarize_results(path, total_distance)

        return summary


# --------------------------------------------------
# Example Usage
# --------------------------------------------------

if __name__ == "__main__":
    json_path = Path(__file__).resolve().parent.parent / "data" /"storeMap.json"
    assistant = LLMAssistant(debug=True)
    user_text = input("Enter grocery instructions: ")
    result = assistant.run_session(user_text)
    print("\nFinal Summary:\n", result)