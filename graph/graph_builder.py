import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

df = pd.read_csv(r"C:\Users\user\OneDrive\Desktop\crimianal network analyser\data\fir_data.csv")

G = nx.MultiDiGraph()

for _, row in df.iterrows():
    person = row["Person"]
    related_person = row["Related_Person"]

    G.add_node(person, type="person")
    G.add_node(related_person, type="person")

    G.add_edge(
        person,
        related_person,
        relationship=row["Relationship"],
        fir_id=row["FIR_ID"],
        location=row["Location"]
    )

pos = nx.spring_layout(G, seed=42)

nx.draw(
    G,
    pos,
    with_labels=True,
    node_size=2500,
    node_color="lightblue",
    arrows=True
)

edge_labels = {}

for u, v, data in G.edges(data=True):
    edge_labels[(u, v)] = data["relationship"]

nx.draw_networkx_edge_labels(
    G,
    pos,
    edge_labels=edge_labels
)

plt.title("Criminal Network")
plt.show()