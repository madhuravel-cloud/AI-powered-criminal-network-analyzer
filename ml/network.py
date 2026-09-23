import tempfile

import networkx as nx
import streamlit.components.v1 as components
from pyvis.network import Network


def build_network_graph(relationships):

    G = nx.Graph()

    for relationship in relationships:

        person = relationship["person"]
        related_person = relationship["related_person"]
        relation = relationship["relationship"]

        G.add_node(
            person,
            label=person,
            title=f"Person: {person}",
            group="person"
        )

        G.add_node(
            related_person,
            label=related_person,
            title=f"Person: {related_person}",
            group="person"
        )

        if G.has_edge(person, related_person):

            old_label = G[person][related_person].get(
                "label",
                ""
            )

            G[person][related_person]["label"] = (
                old_label + ", " + relation
            )

        else:

            G.add_edge(
                person,
                related_person,
                label=relation,
                title=relation
            )

    return G


def display_network_graph(G):

    net = Network(
        height="600px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#0f172a",
        directed=False
    )

    net.from_nx(G)

    net.set_options("""
    {
        "nodes": {
            "shape": "dot",
            "size": 18,
            "borderWidth": 2,
            "font": {
                "size": 15,
                "face": "Arial",
                "color": "#0f172a"
            }
        },

        "edges": {
            "width": 2,
            "color": {
                "color": "#64748b",
                "highlight": "#6366f1"
            },
            "smooth": {
                "enabled": true,
                "type": "dynamic"
            },
            "font": {
                "size": 12,
                "color": "#334155",
                "strokeWidth": 0
            }
        },

        "physics": {
            "enabled": true,
            "barnesHut": {
                "gravitationalConstant": -3000,
                "centralGravity": 0.2,
                "springLength": 150,
                "springConstant": 0.04,
                "damping": 0.09
            },
            "stabilization": {
                "enabled": true,
                "iterations": 150
            }
        },

        "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": true,
            "zoomView": true,
            "dragView": true
        }
    }
    """)

    with tempfile.NamedTemporaryFile(
        suffix=".html",
        delete=False
    ) as temp:

        net.save_graph(temp.name)

        with open(
            temp.name,
            "r",
            encoding="utf-8"
        ) as f:

            html = f.read()

    components.html(
        html,
        height=620,
        scrolling=False
    )