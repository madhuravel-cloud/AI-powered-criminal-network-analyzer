from graph.graph_builder import build_graph
from analysis.centrality import calculate_centrality
from analysis.input_fir_analysis import compare_input_fir
from analysis.repeated_person import find_repeated_people
from analysis.phone_analysis import find_repeated_phones
from analysis.location_analysis import find_repeated_locations
from analysis.relationship_analysis import find_relationships
from analysis.paths import find_paths
from analysis.communities import find_communities


G = build_graph()


print("\nMost Connected People:\n")

centrality = calculate_centrality(G)

for result in centrality:
    print(
        f"{result['person']}: "
        f"degree={result['degree']:.3f}, "
        f"betweenness={result['betweenness']:.3f}, "
        f"closeness={result['closeness']:.3f}"
    )


input_fir_id = input("\nEnter FIR ID for cross-FIR analysis: ").strip()

print("\nCross-FIR Connections:\n")

connections = compare_input_fir(input_fir_id)

if connections:
    for fir_id, data in connections.items():
        print(f"{fir_id}:")
        print(f"  Common People: {', '.join(data['common_people']) or 'None'}")
        print(f"  Common Phones: {', '.join(data['common_phones']) or 'None'}")
        print(f"  Common Locations: {', '.join(data['common_locations']) or 'None'}")
else:
    print("No connections found.")


print("\nRepeated People:\n")

repeated_people = find_repeated_people()

for result in repeated_people:
    if result["fir_count"] > 1:
        print(
            f"{result['person']}: "
            f"{result['fir_count']} FIRs - "
            f"{', '.join(result['firs'])}"
        )


print("\nRepeated Phones:\n")

repeated_phones = find_repeated_phones()

for result in repeated_phones:
    if result["fir_count"] > 1:
        print(
            f"{result['phone']}: "
            f"{result['fir_count']} FIRs - "
            f"{', '.join(result['firs'])}"
        )


print("\nRepeated Locations:\n")

repeated_locations = find_repeated_locations()

for result in repeated_locations:
    if result["fir_count"] > 1:
        print(
            f"{result['location']}: "
            f"{result['fir_count']} FIRs - "
            f"{', '.join(result['firs'])}"
        )


print("\nRelationships:\n")

relationships = find_relationships()

for relationship, data in relationships.items():
    print(f"{relationship}:")

    for item in data:
        print(
            f"  {item['person']} -> "
            f"{item['related_person']} "
            f"({item['fir_id']})"
        )


print("\nCommunities:\n")

communities = find_communities(G)

for community in communities:
    print(
        f"Community {community['community']}: "
        f"{', '.join(community['people'])}"
    )


source = input("\nEnter source person for path analysis: ").strip()
target = input("Enter target person for path analysis: ").strip()

paths = find_paths(G, source, target)

print("\nPaths:\n")

if paths:
    for path in paths:
        print(" -> ".join(path))
else:
    print("No path found.")