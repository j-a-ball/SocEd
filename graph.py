__author__ = "Jon Ball"
__version__ = "Winter 2023"

# Python 3.9.1

import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import json
import os

# Main function
def main():
    # Load the data
    data = load_data("data/author_citations.json")
    # Draw the graph
    draw_graph(data)

# NetworkX graph of citations
def draw_graph(
    data: dict[str : list[str]],
    output_dir: str = "data/graphs/"
    ) -> None:
    """Given a dictionary of citations and a list of all authors, draw a graph of the citations."""
    # Create the graph
    G = nx.DiGraph()
    print("Graph initialized.")
    G.add_edges_from(get_author_edges(data))
    # Draw the graph
    print("Drawing graph...")
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, node_size=10)
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color="black", width=0.05)
    nx.draw_networkx_labels(G, pos, font_size=0, font_color="red")
    # Save the graph
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    plt.savefig(output_dir + "soced_graph.png", bbox_inches="tight", dpi=1000)
    # Save for gephi
    nx.write_gexf(G, output_dir + "soced_graph.gexf")
    print("Graph saved.")

# Get the edges between authors
def get_author_edges(
    data: dict[str : list[str]]
    ) -> list[tuple[str, str]]:
    """Given a dictionary of citations and a list of all authors, return a list of edges between authors."""
    # Convert the data dict to a list of edges / tuples between authors and the authors they cite
    edges = []
    for author, authors_they_cite in data.items():
        for author_they_cite in authors_they_cite:
            edges.append((author, author_they_cite))
    print(f"{len(edges)} edges created.")
    return edges

# Load the json data dict[str : list[str]]
def load_data(filepath):
    with open(filepath), "r") as infile:
        data = json.load(infile)
    print(f"Data loaded of type {type(data)}.")
    return data