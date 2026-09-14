import pandas as pd
import networkx as nx
from pathlib import Path


def build_features(G, input_fir_id):

    data_path = Path(__file__).resolve().parent.parent / "data" / "fir_data.csv"

    df = pd.read_csv(data_path)

    input_data = df[df["FIR_ID"] == input_fir_id]

    if input_data.empty:
        return pd.DataFrame()

    input_people = set(input_data["Person"]) | set(input_data["Related_Person"])
    input_phones = set(input_data["Phone"].astype(str))
    input_locations = set(input_data["Location"])

    degree = nx.degree_centrality(G)
    betweenness = nx.betweenness_centrality(G)
    closeness = nx.closeness_centrality(G)

    person_firs = {}
    person_relationships = {}

    for _, row in df.iterrows():

        person = row["Person"]
        related_person = row["Related_Person"]
        fir_id = row["FIR_ID"]

        for candidate in [person, related_person]:

            if candidate not in person_firs:
                person_firs[candidate] = set()

            person_firs[candidate].add(fir_id)

        person_relationships[person] = person_relationships.get(person, 0) + 1
        person_relationships[related_person] = person_relationships.get(
            related_person, 0
        ) + 1

    communities = list(
        nx.community.greedy_modularity_communities(
            nx.Graph(G)
        )
    )

    community_map = {}

    for community_id, community in enumerate(communities):

        for person in community:
            community_map[person] = community_id

    candidates = set()

    for person in input_people:

        if person in G:
            candidates.update(G.neighbors(person))
            candidates.update(G.predecessors(person))

    candidates -= input_people

    results = []

    for candidate in candidates:

        candidate_firs = person_firs.get(candidate, set())

        common_people = set()
        common_phones = set()
        common_locations = set()

        for fir_id in candidate_firs:

            fir_data = df[df["FIR_ID"] == fir_id]

            fir_people = set(fir_data["Person"]) | set(
                fir_data["Related_Person"]
            )

            fir_phones = set(fir_data["Phone"].astype(str))
            fir_locations = set(fir_data["Location"])

            common_people.update(input_people & fir_people)
            common_phones.update(input_phones & fir_phones)
            common_locations.update(input_locations & fir_locations)

        path_lengths = []

        for person in input_people:

            try:
                path_length = nx.shortest_path_length(
                    G,
                    source=person,
                    target=candidate
                )

                path_lengths.append(path_length)

            except nx.NetworkXNoPath:
                pass

        if path_lengths:
            shortest_path = min(path_lengths)
        else:
            shortest_path = -1

        community_overlap = 0

        if candidate in community_map:

            candidate_community = community_map[candidate]

            for person in input_people:

                if community_map.get(person) == candidate_community:
                    community_overlap = 1
                    break

        results.append({
            "FIR_ID": input_fir_id,
            "Candidate": candidate,
            "fir_count": len(candidate_firs),
            "common_people_count": len(common_people),
            "common_phone_count": len(common_phones),
            "common_location_count": len(common_locations),
            "degree_centrality": degree.get(candidate, 0),
            "betweenness": betweenness.get(candidate, 0),
            "closeness": closeness.get(candidate, 0),
            "relationship_count": person_relationships.get(candidate, 0),
            "connected_fir_count": len(candidate_firs),
            "path_length": shortest_path,
            "community_overlap": community_overlap
        })

    return pd.DataFrame(results)