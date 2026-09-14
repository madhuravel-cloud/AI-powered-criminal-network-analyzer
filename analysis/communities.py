import networkx as nx


def find_communities(G):

    graph = nx.Graph(G)

    communities = nx.community.greedy_modularity_communities(graph)

    results = []

    for index, community in enumerate(communities, start=1):

        results.append({
            "community": index,
            "people": sorted(community)
        })

    return results