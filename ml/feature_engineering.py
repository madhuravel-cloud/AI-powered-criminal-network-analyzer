import pandas as pd
import networkx as nx
from pathlib import Path

from graph.graph_builder import build_graph
from analysis.centrality import calculate_centrality
from analysis.repeated_person import find_repeated_people
from analysis.phone_analysis import find_repeated_phones
from analysis.location_analysis import find_repeated_locations
from analysis.communities import find_communities


def build_features(input_fir):

    data_path = Path(__file__).resolve().parent.parent / "data" / "fir_data.csv"

    df = pd.read_csv(data_path)

    input_columns = [
        "Person",
        "Location",
        "Phone",
        "Related_Person",
        "Relationship"
    ]

    input_data = pd.DataFrame(
        input_fir,
        columns=input_columns
    )

    if input_data.empty:
        return pd.DataFrame()

    G = build_graph()

    centrality_results = calculate_centrality(G)
    repeated_people = find_repeated_people()
    repeated_phones = find_repeated_phones()
    repeated_locations = find_repeated_locations()
    communities = find_communities(G)

    input_people = (
        set(input_data["Person"]) |
        set(input_data["Related_Person"])
    )

    input_locations = set(
        input_data["Location"]
    )

    input_phones = set(
        input_data["Phone"].astype(str)
    )

    candidates = set()

    # Shared phone
    for _, row in df.iterrows():

        person = row["Person"]
        related_person = row["Related_Person"]
        phone = str(row["Phone"])
        location = row["Location"]

        if phone in input_phones:
            candidates.add(person)
            candidates.add(related_person)

        # Shared location
        if location in input_locations:
            candidates.add(person)
            candidates.add(related_person)

    # Graph connections
    for person in input_people:

        if person not in G:
            continue

        for neighbour in G.neighbors(person):

            if G.nodes[neighbour].get("type") == "person":
                candidates.add(neighbour)

        for predecessor in G.predecessors(person):

            if G.nodes[predecessor].get("type") == "person":
                candidates.add(predecessor)

    candidates -= input_people

    centrality_map = {
        item["person"]: item
        for item in centrality_results
    }

    repeated_people_map = {
        item["person"]: item
        for item in repeated_people
    }

    repeated_location_map = {
        item["location"]: item
        for item in repeated_locations
    }

    repeated_phone_map = {
        item["phone"]: item
        for item in repeated_phones
    }

    community_map = {}

    for community in communities:

        for person in community["people"]:
            community_map[person] = community["community"]

    undirected_graph = nx.Graph(G)

    results = []

    for candidate in candidates:

        candidate_rows = df[
            (df["Person"] == candidate) |
            (df["Related_Person"] == candidate)
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
            input_phones &
            candidate_phones
        )

        relationship_count = len(
            candidate_rows
        )

        path_lengths = []

        for person in input_people:

            if person not in undirected_graph:
                continue

            if candidate not in undirected_graph:
                continue

            try:

                path = nx.shortest_path(
                    undirected_graph,
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
                    ==
                    community_map[candidate]
                ):

                    community_overlap = 1
                    break

        centrality = centrality_map.get(
            candidate,
            {}
        )

        repeated_location_count = sum(
            1
            for location in candidate_locations
            if location in repeated_location_map
        )

        repeated_phone_count = sum(
            1
            for phone in candidate_phones
            if phone in repeated_phone_map
        )

        repeated_fir_count = repeated_people_map.get(
            candidate,
            {}
        ).get(
            "fir_count",
            0
        )

        results.append({

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
                relationship_count,

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

    return pd.DataFrame(results)