import networkx as nx


def find_paths(G, source, target):

    if source not in G or target not in G:
        return []

    paths = nx.all_simple_paths(
        G,
        source=source,
        target=target
    )

    return list(paths)