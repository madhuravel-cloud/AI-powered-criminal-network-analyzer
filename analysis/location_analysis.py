import pandas as pd
from pathlib import Path


def find_repeated_locations():

    data_path = Path(__file__).resolve().parent.parent / "data" / "fir_data.csv"

    df = pd.read_csv(data_path)

    location_firs = {}

    for _, row in df.iterrows():

        location = row["Location"]
        fir_id = row["FIR_ID"]

        if location not in location_firs:
            location_firs[location] = set()

        location_firs[location].add(fir_id)

    results = []

    for location, firs in location_firs.items():

        results.append({
            "location": location,
            "fir_count": len(firs),
            "firs": sorted(firs)
        })

    return sorted(
        results,
        key=lambda x: x["fir_count"],
        reverse=True
    )