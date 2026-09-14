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
        phone = str(row["Phone"])
        location = row["Location"]
        fir_id = row["FIR_ID"]

        G.add_node(person, type="person")
        G.add_node(related_person, type="person")
        G.add_node(phone, type="phone")
        G.add_node(location, type="location")
        G.add_node(fir_id, type="fir")

        G.add_edge(
            person,
            related_person,
            type="relationship",
            fir_id=fir_id,
            relationship=row["Relationship"]
        )

        G.add_edge(
            person,
            phone,
            type="uses"
        )

        G.add_edge(
            person,
            location,
            type="located_at"
        )

        G.add_edge(
            person,
            fir_id,
            type="appears_in"
        )

        G.add_edge(
            related_person,
            fir_id,
            type="appears_in"
        )

    return G