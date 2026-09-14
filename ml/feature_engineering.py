import pandas as pd
import networkx as nx
from pathlib import Path

from graph.graph_builder import build_graph
from analysis.centrality import calculate_centrality
from analysis.repeated_person import find_repeated_people
from analysis.phone_analysis import find_repeated_phones
from analysis.location_analysis import find_repeated_locations
from analysis.relationship_analysis import find_relationships
from analysis.communities import find_communities


def build_features(input_fir_id):

    data_path = Path(__file__).resolve().parent.parent / "data" / "fir_data.csv"

    df = pd.read_csv(data_path)

    input_data = df[df["FIR_ID"] == input_fir_id]

    if input_data.empty:
        return pd.DataFrame()

    G = build_graph()

    centrality_results = calculate_centrality(G)
    repeated_people = find_repeated_people()
    repeated_phones = find_repeated_phones()
    repeated_locations = find_repeated_locations()
    relationships = find_relationships()
    communities = find_communities(G)

    input_people = set(input_data["Person"]) | set(
        input_data["Related_Person"]
    )

    input_locations = set(input_data["Location"])

    input_phones = set(input_data["Phone"].astype(str))

    other_fir_data = df[df["FIR_ID"] != input_fir_id]

    other_fir_phones = set(
        other_fir_data["Phone"].astype(str)
    )

    matching_phones = input_phones & other_fir_phones

    candidates = set()

    for _, row in other_fir_data.iterrows():

        person = row["Person"]
        related_person = row["Related_Person"]
        phone = str(row["Phone"])

        if phone in matching_phones:
            candidates.add(person)
            candidates.add(related_person)

        if row["Location"] in input_locations:
            candidates.add(person)
            candidates.add(related_person)

    for person in input_people:

        if person in G:

            candidates.update(
                neighbour
                for neighbour in G.neighbors(person)
                if G.nodes[neighbour].get("type") == "person"
            )

            candidates.update(
                predecessor
                for predecessor in G.predecessors(person)
                if G.nodes[predecessor].get("type") == "person"
            )

    candidates -= input_people

    centrality_map = {
        item["person"]: item
        for item in centrality_results
    }

    repeated_people_map = {
        item["person"]: item
        for item in repeated_people
    }

    repeated_locations_map = {
        item["location"]: item
        for item in repeated_locations
    }

    community_map = {}

    for community in communities:

        for person in community["people"]:
            community_map[person] = community["community"]

    results = []

    for candidate in candidates:

        candidate_rows = df[
            (df["Person"] == candidate)
            | (df["Related_Person"] == candidate)
        ]

        candidate_firs = set(
            candidate_rows["FIR_ID"]
        )

        candidate_locations = set(
            candidate_rows["Location"]
        )

        candidate_phones = set(
            candidate_rows["Phone"].astype(str)
        )

        common_locations = (
            input_locations &
            candidate_locations
        )

        common_phones = (
            matching_phones &
            candidate_phones
        )

        candidate_relationship_count = len(
            candidate_rows
        )

        path_lengths = []

        for person in input_people:

            if person not in G or candidate not in G:
                continue

            try:

                path = nx.shortest_path(
                    nx.Graph(G),
                    source=person,
                    target=candidate
                )

                path_lengths.append(
                    len(path) - 1
                )

            except nx.NetworkXNoPath:
                continue

        shortest_path = (
            min(path_lengths)
            if path_lengths
            else -1
        )

        community_overlap = 0

        if candidate in community_map:

            for person in input_people:

                if (
                    community_map.get(person)
                    == community_map[candidate]
                ):
                    community_overlap = 1
                    break

        centrality = centrality_map.get(
            candidate,
            {}
        )

        repeated_location_count = 0

        for location in candidate_locations:

            if location in repeated_locations_map:

                repeated_location_count += 1

        repeated_phone_count = 0

        for phone in candidate_phones:

            phone_data = [
                item
                for item in find_repeated_phones()
                if item["phone"] == phone
            ]

            if phone_data:
                repeated_phone_count += 1

        results.append({

            "FIR_ID": input_fir_id,

            "Candidate": candidate,

            "fir_count": len(
                candidate_firs
            ),

            "common_location_count": len(
                common_locations
            ),

            "matching_phone_count": len(
                common_phones
            ),

            "relationship_count":
                candidate_relationship_count,

            "repeated_location_count":
                repeated_location_count,

            "repeated_phone_count":
                repeated_phone_count,

            "degree_centrality":
                centrality.get(
                    "degree",
                    0
                ),

            "betweenness":
                centrality.get(
                    "betweenness",
                    0
                ),

            "closeness":
                centrality.get(
                    "closeness",
                    0
                ),

            "shortest_path":
                shortest_path,

            "community_overlap":
                community_overlap
        })

    features = pd.DataFrame(results)

    features = features.sort_values(
        by="fir_count",
        ascending=False
    )

    output_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / f"features_{input_fir_id}.csv"
    )

    features.to_csv(
        output_path,
        index=False
    )

    return features


if __name__ == "__main__":

    input_fir_id = input(
        "Enter FIR ID: "
    ).strip()

    features = build_features(
        input_fir_id
    )

    if features.empty:

        print("FIR not found.")

    else:

        print("\nFeature Table:\n")

        print(features.to_string(
            index=False
        ))