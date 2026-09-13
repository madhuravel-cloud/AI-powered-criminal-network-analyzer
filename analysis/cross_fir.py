import pandas as pd

def find_cross_fir_connections():
    df = pd.read_csv(r"C:\Users\user\OneDrive\Desktop\crimianal network analyser\data\fir_data.csv")
    person_firs = {}
    for _, row in df.iterrows():

        person = row["Person"]
        fir_id = row["FIR_ID"]

        if person not in person_firs:
            person_firs[person] = set()

        person_firs[person].add(fir_id)

    connections = {}

    for person, firs in person_firs.items():

        if len(firs) > 1:
            connections[person] = sorted(firs)

    return connections