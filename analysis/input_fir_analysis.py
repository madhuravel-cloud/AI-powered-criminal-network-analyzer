import pandas as pd
from pathlib import Path


def compare_input_fir(input_fir_id):

    data_path = Path(__file__).resolve().parent.parent / "data" / "fir_data.csv"

    df = pd.read_csv(data_path)

    input_data = df[df["FIR_ID"] == input_fir_id]

    if input_data.empty:
        return {}

    input_people = set(input_data["Person"]) | set(input_data["Related_Person"])
    input_phones = set(input_data["Phone"].astype(str))
    input_locations = set(input_data["Location"])

    results = {}

    for fir_id in df["FIR_ID"].unique():

        if fir_id == input_fir_id:
            continue

        fir_data = df[df["FIR_ID"] == fir_id]

        fir_people = set(fir_data["Person"]) | set(fir_data["Related_Person"])
        fir_phones = set(fir_data["Phone"].astype(str))
        fir_locations = set(fir_data["Location"])

        common_people = input_people & fir_people
        common_phones = input_phones & fir_phones
        common_locations = input_locations & fir_locations

        if common_people or common_phones or common_locations:

            results[fir_id] = {
                "common_people": sorted(common_people),
                "common_phones": sorted(common_phones),
                "common_locations": sorted(common_locations)
            }

    return results