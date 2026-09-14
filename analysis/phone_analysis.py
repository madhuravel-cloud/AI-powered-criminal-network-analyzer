import pandas as pd
from pathlib import Path


def find_repeated_phones():

    data_path = Path(__file__).resolve().parent.parent / "data" / "fir_data.csv"

    df = pd.read_csv(data_path)

    phone_firs = {}

    for _, row in df.iterrows():

        phone = str(row["Phone"])
        fir_id = row["FIR_ID"]
        person = row["Person"]

        if phone not in phone_firs:
            phone_firs[phone] = {
                "firs": set(),
                "people": set()
            }

        phone_firs[phone]["firs"].add(fir_id)
        phone_firs[phone]["people"].add(person)

    results = []

    for phone, data in phone_firs.items():

        results.append({
            "phone": phone,
            "fir_count": len(data["firs"]),
            "firs": sorted(data["firs"]),
            "people": sorted(data["people"])
        })

    return sorted(
        results,
        key=lambda x: x["fir_count"],
        reverse=True
    )