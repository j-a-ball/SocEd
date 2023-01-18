__author__ = "Jon Ball"
__version__ = "Winter 2023"

# Python 3.9.1

import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import json
import time
import os
import re

# Main function
def main():
    print("***\n")
    print("Graphing citations...")
    # Load the data
    citations = load_data("data/author_citations.json")
    # Draw the graph
    draw_graph(filename="soced_graph", data=citations, labels=False, output_dir="data/graphs")
    # Draw the labeled graph
    draw_graph(filename="soced_graph_labeled", data=citations,  labels=True, output_dir="data/graphs")
    # Draw the graph with only the top n=50 authors
    draw_subgraph(filename="soced_graph_top50", data=citations, n=50, labels=False, output_dir="data/graphs")
    # Draw the labeled graph with only the top n=50 authors
    draw_subgraph(filename="soced_graph_top50_labeled", data=citations, n=50, labels=True, output_dir="data/graphs")
    print("***")

# NetworkX graph of citations
def draw_graph(
    filename: str,
    data: dict[str : list[str]],
    labels: bool,
    output_dir: str,
    ) -> None:
    # Start the timer
    tock = time.time()
    # Create the graph
    G = nx.DiGraph()
    print(f"Graph {filename} initialized.")
    G.add_edges_from(get_author_edges(data))
    # Draw the graph
    print("   Drawing graph...")
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, node_size=10, edgecolors="black", linewidths=0.1, node_color="#1f77b4")
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color="black", width=0.01, arrowsize=5)
    if labels:
        nx.draw_networkx_labels(G, pos, font_size=0.5, font_color="#ffd700") # gold to pair with blues
    # End the timer
    print(f"   Graph drawn in {round(time.time() - tock, 2)} seconds.")
    # Save the node centrality scores
    print("   Saving node centrality scores...")
    centrality = nx.degree_centrality(G)
    with open(os.path.join(output_dir, filename + "_centrality.json"), "w") as outfile:
        json.dump(centrality, outfile)
    # Save the graph
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    plt.savefig(os.path.join(output_dir, filename + ".png"), bbox_inches="tight", dpi=800)
    # Save for gephi
    nx.write_gexf(G, os.path.join(output_dir, filename + ".gexf"))
    print(f"Graph saved in {output_dir}.\n")

def draw_subgraph(
    filename: str,
    data: dict[str : list[str]],
    n: int,
    labels: bool,
    output_dir: str
    ) -> list[tuple[str, str]]:
    # Get edges for citations among the top n authors
    nodes = []
    nauthors = [author for author, _ in Counter([cite for cites in data.values() for cite in cites]).most_common(n)]
    for author, cites in data.items():
        for cite in cites:
            if author and cite in nauthors:
                nodes.append((author, cite))
    # Start the timer
    tock = time.time()
    # Create the graph
    G = nx.DiGraph()
    print(f"Subgraph initialized.")
    G.add_edges_from(list(set(nodes)))
    # Draw the graph
    print("   Drawing subgraph...")
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, node_size=10, edgecolors="black", linewidths=0.1, node_color="#1f77b4")
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color="black", width=0.01, arrowsize=5)
    if labels:
        nx.draw_networkx_labels(G, pos, font_size=0.5, font_color="#ffd700")
    # End the timer
    print(f"   Subgraph drawn in {round(time.time() - tock, 2)} seconds.")
    # Save the node centrality scores
    print("   Saving node centrality scores...")
    centrality = nx.betweenness_centrality(G)
    with open(os.path.join(output_dir, filename + "_centrality.json"), "w") as outfile:
        json.dump(centrality, outfile)
    # Save the graph
    plt.savefig(os.path.join(output_dir, filename + ".png"), bbox_inches="tight", dpi=800)
    # Save for gephi
    nx.write_gexf(G, os.path.join(output_dir, filename + ".gexf"))
    print(f"Subgraph saved in {output_dir}.\n")

# Get the edges between authors
def get_author_edges(
    data: dict[str : list[str]]
    ) -> list[tuple[str, str]]:
    # Convert the data dict to a list of edges / tuples between authors and the authors they cite
    edges = []
    for author, authors_they_cite in data.items():
        for author_they_cite in authors_they_cite:
            # manual fix for roslyn arlin mickelson
            if re.search("roslyn arlin|r mickelson", author):
                edges.append(("roslyn a mickelson", author))
            elif re.search("roslyn arlin|r mickelson", author_they_cite):
                edges.append((author, "roslyn a mickelson"))
            else:
                edges.append((author, author_they_cite))
    print(f"   {len(edges)} edges created.")
    return edges

# Load the json data dict[str : list[str]]
def load_data(filepath):
    with open(filepath, "r") as infile:
        data = json.load(infile)
    print(f"Data loaded of type {type(data)}.")
    return data

if __name__ == "__main__":
    main()