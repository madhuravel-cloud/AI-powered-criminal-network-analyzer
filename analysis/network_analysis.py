import pandas as pd
import networkx as nx

df = pd.read_csv(r"C:\Users\user\OneDrive\Desktop\crimianal network analyser\data\fir_data.csv")

G = nx.MultiDiGraph()

for _, row in df.iterrows():
    G.add_node(row["Person"], type="person")
    G.add_node(row["Related_Person"], type="person")

    G.add_edge(
        row["Person"],
        row["Related_Person"],
        fir_id=row["FIR_ID"],
        relationship=row["Relationship"],
        location=row["Location"]
    )

centrality = nx.degree_centrality(G)

print("\nMost Connected People:\n")

for person, score in sorted(
    centrality.items(),
    key=lambda x: x[1],
    reverse=True
):
    print(f"{person}: {score:.3f}")