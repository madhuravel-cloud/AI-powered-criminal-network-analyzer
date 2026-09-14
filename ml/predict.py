from pathlib import Path
import joblib

from ml.feature_engineering import build_features


model_path = Path(__file__).resolve().parent / "criminal_network_model.pkl"

model = joblib.load(model_path)


def analyze_fir(input_fir):

    features = build_features(input_fir)

    if features.empty:
        return []

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

    features["Score"] = (
        probabilities * 100
    ).round(2)

    results = features[
        ["Candidate", "Score"]
    ].sort_values(
        "Score",
        ascending=False
    )

    return results.to_dict(
        orient="records"
    )


if __name__ == "__main__":

    input_fir = [

        [
            "Ravi",
            "Kochi",
            "9876543210",
            "Arun",
            "associate"
        ],

        [
            "Arun",
            "Kochi",
            "9876543211",
            "Kumar",
            "associate"
        ],

        [
            "Kumar",
            "Kochi",
            "9876543212",
            "Manu",
            "friend"
        ]

    ]

    results = analyze_fir(input_fir)

    if not results:

        print("No relevant people found.")

    else:

        print("\nPerson Relevance Scores:\n")

        for result in results:

            print(
                f"{result['Candidate']:<12}"
                f"{result['Score']}"
            )
