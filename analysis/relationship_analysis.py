import pandas as pd
from pathlib import Path


def find_relationships():

    data_path = Path(__file__).resolve().parent.parent / "data" / "fir_data.csv"

    df = pd.read_csv(data_path)

    relationship_data = {}

    for _, row in df.iterrows():

        relationship = row["Relationship"]
        person = row["Person"]
        related_person = row["Related_Person"]
        fir_id = row["FIR_ID"]

        if relationship not in relationship_data:
            relationship_data[relationship] = []

        relationship_data[relationship].append({
            "person": person,
            "related_person": related_person,
            "fir_id": fir_id
        })

    return relationship_data