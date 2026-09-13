import pandas as pd
from pathlib import Path


def find_repeated_people():

    data_path = Path(__file__).resolve().parent.parent / "data" / "fir_data.csv"

    df = pd.read_csv(data_path)

    person_firs = {}

    for _, row in df.iterrows():

        fir_id = row["FIR_ID"]

        people = {
            row["Person"],
            row["Related_Person"]
        }

        for person in people:

            if person not in person_firs:
                person_firs[person] = set()

            person_firs[person].add(fir_id)

    results = []

    for person, firs in person_firs.items():

        results.append({
            "person": person,
            "fir_count": len(firs),
            "firs": sorted(firs)
        })

    return sorted(
        results,
        key=lambda x: x["fir_count"],
        reverse=True
    )