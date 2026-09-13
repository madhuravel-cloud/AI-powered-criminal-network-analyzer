from graph.graph_builder import build_graph
from analysis.centrality import calculate_centrality
from analysis.cross_fir import find_cross_fir_connections
G = build_graph()
print("\nMost Connected People:\n")

centrality = calculate_centrality(G)

for person, score in centrality:
    print(f"{person}: {score:.3f}")


print("\nCross-FIR Connections:\n")

connections = find_cross_fir_connections()

for person, firs in connections.items():
    print(f"{person}: {', '.join(firs)}")