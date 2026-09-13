import networkx as nx


def calculate_centrality(G):

    degree = nx.degree_centrality(G)
    betweenness = nx.betweenness_centrality(G)
    closeness = nx.closeness_centrality(G)

    results = []

    for person in G.nodes():

        results.append({
            "person": person,
            "degree": degree[person],
            "betweenness": betweenness[person],
            "closeness": closeness[person]
        })

    return sorted(
        results,
        key=lambda x: x["degree"],
        reverse=True
    )