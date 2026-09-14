import pandas as pd
from pathlib import Path
import joblib
from ml.feature_engineering import build_features


model_path = Path(__file__).resolve().parent / "criminal_network_model.pkl"

model = joblib.load(model_path)

fir_id = input("Enter FIR ID: ").strip()

features = build_features(fir_id)

if features.empty:
    print("FIR not found.")
else:

    feature_columns = [
        "fir_count",
        "common_location_count",
        "matching_phone_count",
        "relationship_count",
        "repeated_location_count",
        "repeated_phone_count",
        "degree_centrality",
        "betweenness",
        "closeness",
        "shortest_path",
        "community_overlap"
    ]

    X = features[feature_columns]

    probabilities = model.predict_proba(X)[:, 1]

    features["Score"] = (probabilities * 100).round(2)

    results = features[
        ["Candidate", "Score"]
    ].sort_values(
        "Score",
        ascending=False
    )

    print("\nPerson Relevance Scores:\n")
    print(results.to_string(index=False))