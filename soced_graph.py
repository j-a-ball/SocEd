__author__ = "Jon Ball"
__version__ = "Winter 2023"

# Python 3.9.1

import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import json
import os

cleanD = {k: v for k, v in citeD.items() if k in all_authors}

print(f"{len(cleanD)} authors published articles citing {sum([len(v) for k,v in cleanD.items()])} other publications.")
print(f"Paring back to authors who were cited ten or more times.")
cites = Counter(cited_authors)

nodes = []
for k, v in cleanD.items():
    if v:
        for author in v:
            if cites[author] >= 10:
                nodes.append((k, author))
nodes = list(set(nodes))
print(f"{len(nodes)} nodes created.")

print("Drawing graph...")
G = nx.DiGraph()
G.add_edges_from(nodes)
pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G, pos, node_size=25)
nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color="black", width=0.1)
nx.draw_networkx_labels(G, pos, font_size=2, font_color="red")

plt.savefig("soced_graph.png", bbox_inches="tight", dpi=1000)