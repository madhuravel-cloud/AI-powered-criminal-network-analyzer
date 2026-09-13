import pandas as pd
import networkx as nx
from pathlib import Path


def build_graph():

    data_path = Path(__file__).resolve().parent.parent / "data" / "fir_data.csv"

    df = pd.read_csv(data_path)

    G = nx.MultiDiGraph()

    for _, row in df.iterrows():

        person = row["Person"]
        related_person = row["Related_Person"]

        G.add_node(person, type="person")
        G.add_node(related_person, type="person")

        G.add_edge(
            person,
            related_person,
            fir_id=row["FIR_ID"],
            relationship=row["Relationship"],
            location=row["Location"],
            phone=row["Phone"]
        )

    return G