import tempfile

import easyocr
import networkx as nx
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

from PIL import Image
from pyvis.network import Network

from ml.nlp import analyze_fir_text
from ml.predict import analyze_fir


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Criminal Network Analyzer",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# GLOBAL STYLE
# =========================================================

st.markdown("""
<style>

/* =====================================================
   REMOVE WHITE LOOK FROM STREAMLIT COMPONENTS
   ===================================================== */

[data-testid="stMetric"],
[data-testid="stExpander"],
[data-testid="stStatus"],
[data-testid="stFileUploader"] {
    color: #ffffff !important;
}


/* =====================================================
   METRIC CARDS
   ===================================================== */

[data-testid="stMetric"] {
    position: relative;
    overflow: hidden;

    background:
        linear-gradient(
            135deg,
            rgba(15, 118, 170, 0.90),
            rgba(30, 41, 120, 0.92)
        ) !important;

    border: 1px solid rgba(96, 165, 250, 0.45) !important;

    border-radius: 18px !important;

    padding: 1rem !important;

    box-shadow:
        0 10px 30px rgba(0, 0, 0, 0.25),
        inset 0 0 25px rgba(59, 130, 246, 0.12);

    transition:
        transform .3s ease,
        box-shadow .3s ease,
        border-color .3s ease;

    animation:
        cardFloat 5s ease-in-out infinite;
}


/* moving glow inside cards */

[data-testid="stMetric"]::before {
    content: "";

    position: absolute;

    width: 180px;
    height: 180px;

    top: -100px;
    right: -70px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(0, 229, 255, 0.28),
            transparent 70%
        );

    animation:
        metricGlow 5s ease-in-out infinite;
}


/* second glow */

[data-testid="stMetric"]::after {
    content: "";

    position: absolute;

    width: 120px;
    height: 120px;

    bottom: -70px;
    left: -40px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(236, 72, 153, 0.22),
            transparent 70%
        );

    animation:
        metricGlow2 6s ease-in-out infinite;
}


/* metric text */

[data-testid="stMetric"] label {
    color: #c7d2fe !important;
    font-weight: 700 !important;
}

[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 850 !important;
    text-shadow:
        0 0 12px rgba(255,255,255,.18);
}


/* =====================================================
   DIFFERENT CARD ACCENTS
   ===================================================== */

[data-testid="stMetric"]:nth-child(1) {
    background:
        linear-gradient(
            135deg,
            #075985,
            #1d4ed8
        ) !important;
}

[data-testid="stMetric"]:nth-child(2) {
    background:
        linear-gradient(
            135deg,
            #0f766e,
            #0891b2
        ) !important;
}

[data-testid="stMetric"]:nth-child(3) {
    background:
        linear-gradient(
            135deg,
            #6d28d9,
            #9333ea
        ) !important;
}

[data-testid="stMetric"]:nth-child(4) {
    background:
        linear-gradient(
            135deg,
            #b45309,
            #ea580c
        ) !important;
}

[data-testid="stMetric"]:nth-child(5) {
    background:
        linear-gradient(
            135deg,
            #be185d,
            #db2777
        ) !important;
}


/* hover */

[data-testid="stMetric"]:hover {
    transform:
        translateY(-7px)
        scale(1.015);

    box-shadow:
        0 18px 45px rgba(0,0,0,.35),
        0 0 25px rgba(99,102,241,.22);

    border-color:
        rgba(255,255,255,.55) !important;
}


/* =====================================================
   EXPANDERS
   ===================================================== */

[data-testid="stExpander"] {
    position: relative;
    overflow: hidden;

    background:
        linear-gradient(
            135deg,
            rgba(30,41,90,.96),
            rgba(49,30,95,.95)
        ) !important;

    border:
        1px solid rgba(129,140,248,.42) !important;

    border-radius:
        17px !important;

    box-shadow:
        0 12px 32px rgba(0,0,0,.24),
        inset 0 0 25px rgba(124,58,237,.08);

    animation:
        panelPulse 7s ease-in-out infinite;
}

[data-testid="stExpander"]::before {
    content: "";

    position: absolute;

    width: 220px;
    height: 220px;

    right: -100px;
    top: -130px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(0,229,255,.16),
            transparent 70%
        );

    animation:
        panelOrb 8s ease-in-out infinite;
}

[data-testid="stExpander"] summary {
    color: #ffffff !important;
    font-weight: 800 !important;
}

[data-testid="stExpander"] summary p {
    color: #ffffff !important;
}

[data-testid="stExpander"] p,
[data-testid="stExpander"] span,
[data-testid="stExpander"] li {
    color: #dbeafe !important;
}


/* =====================================================
   STATUS BOX
   ===================================================== */

[data-testid="stStatus"] {
    position: relative;
    overflow: hidden;

    background:
        linear-gradient(
            135deg,
            #172554,
            #312e81,
            #4c1d95
        ) !important;

    border:
        1px solid rgba(129,140,248,.5) !important;

    border-radius:
        18px !important;

    box-shadow:
        0 12px 35px rgba(0,0,0,.3);

    animation:
        statusPulse 4s ease-in-out infinite;
}

[data-testid="stStatus"]::before {
    content: "";

    position: absolute;

    width: 260px;
    height: 260px;

    right: -100px;
    top: -130px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(0,229,255,.18),
            transparent 68%
        );

    animation:
        statusGlow 5s ease-in-out infinite;
}

[data-testid="stStatus"] * {
    color: #e0e7ff !important;
}

[data-testid="stStatus"] summary {
    background:
        rgba(2,6,23,.35) !important;
}

[data-testid="stStatus"] summary * {
    color: #ffffff !important;
}


/* =====================================================
   FILE UPLOADER
   ===================================================== */

[data-testid="stFileUploader"] {
    position: relative;
    overflow: hidden;

    background:
        linear-gradient(
            135deg,
            rgba(8,47,73,.96),
            rgba(30,27,75,.96)
        ) !important;

    border:
        2px dashed #22d3ee !important;

    border-radius:
        18px !important;

    box-shadow:
        0 0 25px rgba(34,211,238,.12);

    animation:
        uploaderGlow 4s ease-in-out infinite;
}

[data-testid="stFileUploader"] * {
    color: #dbeafe !important;
}

[data-testid="stFileUploader"]::after {
    content: "";

    position: absolute;

    width: 160%;
    height: 2px;

    left: -30%;
    top: 50%;

    background:
        linear-gradient(
            90deg,
            transparent,
            #00e5ff,
            #7c3aed,
            #ff0099,
            transparent
        );

    opacity: .35;

    animation:
        uploaderScan 4s linear infinite;
}


/* =====================================================
   INFO / ALERTS
   ===================================================== */

[data-testid="stAlert"] {
    background:
        linear-gradient(
            135deg,
            rgba(30,58,138,.90),
            rgba(67,56,202,.90)
        ) !important;

    border:
        1px solid rgba(129,140,248,.45) !important;

    border-radius:
        15px !important;

    color:
        #eef2ff !important;

    box-shadow:
        0 10px 28px rgba(0,0,0,.22);
}

[data-testid="stAlert"] * {
    color:
        #eef2ff !important;
}


/* =====================================================
   LEAD CARDS
   ===================================================== */

.lead-card {
    position: relative;
    overflow: hidden;

    background:
        linear-gradient(
            135deg,
            rgba(15,23,42,.97),
            rgba(30,41,90,.96)
        );

    border:
        1px solid rgba(99,102,241,.45);

    border-radius:
        18px;

    padding:
        18px;

    margin-bottom:
        10px;

    box-shadow:
        0 12px 32px rgba(0,0,0,.28);

    transition:
        transform .3s ease,
        box-shadow .3s ease;
}

.lead-card::before {
    content: "";

    position: absolute;

    left: 0;
    top: 0;

    width: 5px;
    height: 100%;

    background:
        linear-gradient(
            180deg,
            #00e5ff,
            #7c3aed,
            #ff0099
        );
}

.lead-card::after {
    content: "";

    position: absolute;

    width: 180px;
    height: 180px;

    right: -100px;
    bottom: -100px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(236,72,153,.20),
            transparent 70%
        );

    animation:
        leadGlow 6s ease-in-out infinite;
}

.lead-card:hover {
    transform:
        translateY(-5px);

    box-shadow:
        0 20px 45px rgba(124,58,237,.24);
}

.candidate-name {
    color: #ffffff;
    font-size: 1.15rem;
    font-weight: 850;
}

.candidate-label {
    color: #a5b4fc;
    font-size: .82rem;
}

.score-high {
    color: #fb7185;
    font-weight: 850;
}

.score-medium {
    color: #fbbf24;
    font-weight: 850;
}

.score-low {
    color: #4ade80;
    font-weight: 850;
}


/* =====================================================
   INPUT / TEXT AREA
   ===================================================== */

textarea {
    background:
        rgba(15,23,42,.92) !important;

    color:
        #f8fafc !important;

    border:
        1px solid rgba(129,140,248,.45) !important;

    border-radius:
        14px !important;
}


/* =====================================================
   ANIMATIONS
   ===================================================== */

@keyframes cardFloat {
    0%,100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-2px);
    }
}

@keyframes metricGlow {
    0%,100% {
        transform: translate(0,0) scale(.9);
        opacity: .45;
    }

    50% {
        transform: translate(-35px,25px) scale(1.15);
        opacity: .95;
    }
}

@keyframes metricGlow2 {
    0%,100% {
        transform: scale(.8);
        opacity: .25;
    }

    50% {
        transform: scale(1.25);
        opacity: .7;
    }
}

@keyframes panelPulse {
    0%,100% {
        box-shadow:
            0 12px 32px rgba(0,0,0,.24);
    }

    50% {
        box-shadow:
            0 16px 40px rgba(124,58,237,.18);
    }
}

@keyframes panelOrb {
    0%,100% {
        transform: translate(0,0);
    }

    50% {
        transform: translate(-45px,35px);
    }
}

@keyframes statusPulse {
    0%,100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-2px);
    }
}

@keyframes statusGlow {
    0%,100% {
        transform: scale(.9);
        opacity: .4;
    }

    50% {
        transform: scale(1.2);
        opacity: .9;
    }
}

@keyframes uploaderGlow {
    0%,100% {
        box-shadow:
            0 0 20px rgba(34,211,238,.08);
    }

    50% {
        box-shadow:
            0 0 32px rgba(124,58,237,.18);
    }
}

@keyframes uploaderScan {
    from {
        transform: translateX(-20%);
    }

    to {
        transform: translateX(80%);
    }
}

@keyframes leadGlow {
    0%,100% {
        transform: scale(.8);
        opacity: .35;
    }

    50% {
        transform: scale(1.25);
        opacity: .8;
    }
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# OCR MODEL
# =========================================================

@st.cache_resource
def load_ocr():

    return easyocr.Reader(
        ["en"],
        gpu=False
    )


def extract_text_from_image(image):

    reader = load_ocr()

    image_array = np.array(image)

    text = reader.readtext(
        image_array,
        detail=0,
        paragraph=True
    )

    return "\n".join(text)


# =========================================================
# NETWORKX GRAPH
# =========================================================

def build_network_graph(relationships):

    graph = nx.Graph()

    for relationship in relationships:

        person = relationship["person"]
        related_person = relationship["related_person"]
        relation = relationship["relationship"]

        graph.add_node(
            person,
            label=person,
            title=f"Person: {person}",
            group="person"
        )

        graph.add_node(
            related_person,
            label=related_person,
            title=f"Person: {related_person}",
            group="person"
        )

        if graph.has_edge(
            person,
            related_person
        ):

            old_label = graph[
                person
            ][
                related_person
            ].get(
                "label",
                ""
            )

            if old_label:

                old_label += ", "

            graph[
                person
            ][
                related_person
            ]["label"] = (
                old_label + relation
            )

        else:

            graph.add_edge(
                person,
                related_person,
                label=relation,
                title=relation
            )

    return graph


def display_network_graph(graph):

    network = Network(
        height="650px",
        width="100%",
        bgcolor="#07111f",
        font_color="#e2e8f0",
        directed=False
    )

    network.from_nx(graph)

    # --------------------------------------------------
    # NODE STYLING
    # --------------------------------------------------

    for node in network.nodes:

        node["shape"] = "dot"
        node["size"] = 22

        node["color"] = {
            "background": "#6366f1",
            "border": "#a5b4fc",
            "highlight": {
                "background": "#8b5cf6",
                "border": "#c4b5fd"
            },
            "hover": {
                "background": "#7c3aed",
                "border": "#e9d5ff"
            }
        }

        node["borderWidth"] = 2

        node["shadow"] = {
            "enabled": True,
            "color": "rgba(124,58,237,0.55)",
            "size": 14,
            "x": 0,
            "y": 0
        }

        node["font"] = {
            "size": 16,
            "face": "Arial",
            "color": "#f8fafc",
            "strokeWidth": 3,
            "strokeColor": "#07111f"
        }


    # --------------------------------------------------
    # EDGE STYLING
    # --------------------------------------------------

    for edge in network.edges:

        edge["width"] = 2
        edge["color"] = {
            "color": "#64748b",
            "highlight": "#22d3ee",
            "hover": "#a78bfa"
        }

        edge["selectionWidth"] = 4

        edge["smooth"] = {
            "enabled": True,
            "type": "dynamic"
        }

        edge["dashes"] = [8, 6]

        edge["font"] = {
            "size": 13,
            "color": "#cbd5e1",
            "strokeWidth": 3,
            "strokeColor": "#07111f",
            "align": "middle"
        }


    # --------------------------------------------------
    # GRAPH OPTIONS
    # --------------------------------------------------

    network.set_options("""
    {
        "nodes": {
            "chosen": {
                "node": true,
                "label": true
            }
        },

        "edges": {
            "hoverWidth": 3,
            "arrowStrikethrough": false
        },

        "physics": {
            "enabled": true,

            "barnesHut": {
                "gravitationalConstant": -4200,
                "centralGravity": 0.18,
                "springLength": 170,
                "springConstant": 0.035,
                "damping": 0.08,
                "avoidOverlap": 1
            },

            "minVelocity": 0.5,

            "stabilization": {
                "enabled": true,
                "iterations": 250,
                "fit": true
            }
        },

        "interaction": {
            "hover": true,
            "tooltipDelay": 80,
            "navigationButtons": true,
            "keyboard": true,
            "zoomView": true,
            "dragView": true,
            "multiselect": false,
            "selectConnectedEdges": true
        }
    }
    """)


    # --------------------------------------------------
    # RENDER
    # --------------------------------------------------

    with tempfile.NamedTemporaryFile(
        suffix=".html",
        delete=False
    ) as temp_file:

        network.save_graph(temp_file.name)

        with open(
            temp_file.name,
            "r",
            encoding="utf-8"
        ) as file:

            html = file.read()


    components.html(
        html,
        height=680,
        scrolling=False
    )

# =========================================================
# ANIMATED HERO
# =========================================================

components.html("""
<html>

<head>

<style>

body {

    margin:
        0;

    background:
        transparent;

    overflow:
        hidden;
}


.hero {

    position:
        relative;

    height:
        185px;

    border-radius:
        24px;

    overflow:
        hidden;

    background:
        linear-gradient(
            120deg,
            #020617,
            #0f172a,
            #1e1b4b,
            #312e81
        );

    background-size:
        300% 300%;

    animation:
        heroMove 11s ease infinite;

    box-shadow:
        0 20px 50px rgba(15,23,42,.23);
}


/* grid */

.grid {

    position:
        absolute;

    inset:
        0;

    background-image:

        linear-gradient(
            rgba(255,255,255,.035) 1px,
            transparent 1px
        ),

        linear-gradient(
            90deg,
            rgba(255,255,255,.035) 1px,
            transparent 1px
        );

    background-size:
        28px 28px;

    animation:
        gridMove 15s linear infinite;
}


/* scan */

.scan {

    position:
        absolute;

    width:
        24%;

    height:
        220%;

    top:
        -60%;

    left:
        -35%;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(59,130,246,.14),
            rgba(167,139,250,.38),
            rgba(236,72,153,.14),
            transparent
        );

    transform:
        skewX(-18deg);

    animation:
        scanMove 4s linear infinite;
}


/* orbs */

.orb {

    position:
        absolute;

    border-radius:
        50%;

    filter:
        blur(3px);

    pointer-events:
        none;
}

.orb-a {

    width:
        190px;

    height:
        190px;

    left:
        6%;

    top:
        -80px;

    background:
        radial-gradient(
            circle,
            rgba(59,130,246,.22),
            transparent 70%
        );

    animation:
        orbA 7s ease-in-out infinite;
}

.orb-b {

    width:
        220px;

    height:
        220px;

    right:
        7%;

    bottom:
        -120px;

    background:
        radial-gradient(
            circle,
            rgba(168,85,247,.20),
            transparent 70%
        );

    animation:
        orbB 8s ease-in-out infinite;
}

.orb-c {

    width:
        130px;

    height:
        130px;

    right:
        35%;

    top:
        25%;

    background:
        radial-gradient(
            circle,
            rgba(236,72,153,.11),
            transparent 70%
        );

    animation:
        orbC 5s ease-in-out infinite;
}


/* particles */

.particle {

    position:
        absolute;

    width:
        4px;

    height:
        4px;

    border-radius:
        50%;

    background:
        #bfdbfe;

    box-shadow:
        0 0 12px rgba(147,197,253,.8);

    animation:
        floatParticle 5s ease-in-out infinite;
}

.p1 {
    left: 16%;
    top: 27%;
}

.p2 {
    left: 30%;
    top: 70%;
    animation-delay: 1s;
}

.p3 {
    left: 52%;
    top: 22%;
    animation-delay: 2s;
}

.p4 {
    left: 70%;
    top: 66%;
    animation-delay: 3s;
}

.p5 {
    left: 87%;
    top: 37%;
    animation-delay: 1.5s;
}

.p6 {
    left: 62%;
    top: 82%;
    animation-delay: 2.5s;
}


/* content */

.content {

    position:
        absolute;

    left:
        30px;

    top:
        28px;

    z-index:
        10;

    color:
        white;

    font-family:
        Arial,
        sans-serif;
}

.title {

    font-size:
        31px;

    font-weight:
        850;

    letter-spacing:
        -.8px;

    animation:
        titleIn 1s ease-out;
}

.subtitle {

    margin-top:
        7px;

    color:
        #cbd5e1;

    font-size:
        13px;

    animation:
        subtitleIn 1.4s ease-out;
}

.status {

    margin-top:
        18px;

    display:
        flex;

    align-items:
        center;

    color:
        #bbf7d0;

    font-size:
        12px;

    animation:
        statusIn 1.8s ease-out;
}

.dot {

    width:
        8px;

    height:
        8px;

    margin-right:
        8px;

    border-radius:
        50%;

    background:
        #22c55e;

    box-shadow:
        0 0 14px #22c55e;

    animation:
        dotPulse 1.5s infinite;
}


/* animations */

@keyframes heroMove {

    0% {
        background-position:
            0% 50%;
    }

    50% {
        background-position:
            100% 50%;
    }

    100% {
        background-position:
            0% 50%;
    }
}

@keyframes gridMove {

    from {
        transform:
            translate(0,0);
    }

    to {
        transform:
            translate(28px,28px);
    }
}

@keyframes scanMove {

    from {
        left:
            -35%;
    }

    to {
        left:
            135%;
    }
}

@keyframes orbA {

    0%,100% {
        transform:
            translate(0,0)
            scale(1);
    }

    50% {
        transform:
            translate(50px,20px)
            scale(1.18);
    }
}

@keyframes orbB {

    0%,100% {
        transform:
            translate(0,0)
            scale(1);
    }

    50% {
        transform:
            translate(-50px,-25px)
            scale(1.16);
    }
}

@keyframes orbC {

    0%,100% {
        transform:
            scale(.8);
    }

    50% {
        transform:
            scale(1.25);
    }
}

@keyframes floatParticle {

    0%,100% {
        transform:
            translateY(0)
            scale(.7);

        opacity:
            .25;
    }

    50% {
        transform:
            translateY(-22px)
            scale(1.35);

        opacity:
            1;
    }
}

@keyframes titleIn {

    from {
        opacity:
            0;

        transform:
            translateY(12px);
    }

    to {
        opacity:
            1;

        transform:
            translateY(0);
    }
}

@keyframes subtitleIn {

    from {
        opacity:
            0;
    }

    to {
        opacity:
            1;
    }
}

@keyframes statusIn {

    from {
        opacity:
            0;

        transform:
            translateX(-12px);
    }

    to {
        opacity:
            1;

        transform:
            translateX(0);
    }
}

@keyframes dotPulse {

    0%,100% {
        opacity:
            .4;

        transform:
            scale(.8);
    }

    50% {
        opacity:
            1;

        transform:
            scale(1.2);
    }
}

</style>

</head>


<body>

<div class="hero">

    <div class="grid"></div>

    <div class="scan"></div>

    <div class="orb orb-a"></div>
    <div class="orb orb-b"></div>
    <div class="orb orb-c"></div>

    <div class="particle p1"></div>
    <div class="particle p2"></div>
    <div class="particle p3"></div>
    <div class="particle p4"></div>
    <div class="particle p5"></div>
    <div class="particle p6"></div>

    <div class="content">

        <div class="title">
            Criminal Network Analyzer
        </div>

        <div class="subtitle">
            AI-powered cross-FIR investigation intelligence platform
        </div>

        <div class="status">

            <span class="dot"></span>

            Investigation engine ready

        </div>

    </div>

</div>

</body>

</html>
""", height=195)


# =========================================================
# FIR DOCUMENT
# =========================================================

st.markdown(
    '<div class="section-title">FIR Document</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-accent"></div>',
    unsafe_allow_html=True
)


uploaded_file = st.file_uploader(
    "Upload FIR image",
    type=[
        "png",
        "jpg",
        "jpeg",
        "webp"
    ]
)


if uploaded_file is None:

    st.info(
        "Upload an FIR image to begin analysis."
    )

    st.stop()


# =========================================================
# IMAGE
# =========================================================

image = Image.open(
    uploaded_file
)


preview_col, details_col = st.columns(
    [1.15, 0.85]
)


with preview_col:

    st.image(
        image,
        caption="Uploaded FIR",
        use_container_width=True
    )


with details_col:

    st.markdown("### Document Ready")

    st.write(
        f"**File:** {uploaded_file.name}"
    )

    st.write(
        f"**Resolution:** "
        f"{image.size[0]} × {image.size[1]}"
    )

    st.write(
        "**Pipeline:** OCR → NLP → Network Analysis"
    )

    st.write("")

    analyze_button = st.button(
        "Analyze FIR",
        use_container_width=True
    )


# =========================================================
# ANALYSIS
# =========================================================

if analyze_button:

    with st.status(
        "Running investigation pipeline...",
        expanded=True
    ) as status:

        st.write(
            "Initializing document analysis..."
        )

        st.write(
            "Running OCR..."
        )

        fir_text = extract_text_from_image(
            image
        )

        st.write(
            "Extracting entities and relationships..."
        )

        nlp_results = analyze_fir_text(
            fir_text
        )

        st.write(
            "Preparing network intelligence..."
        )

        relationships = nlp_results["relationships"]

        input_fir = []

for relationship in relationships:

    input_fir.append([
        relationship["person"],
        locations[0] if locations else "",
        phones[0] if phones else "",
        relationship["related_person"],
        relationship["relationship"]
    ])


    # =====================================================
    # ENTITIES
    # =====================================================

    persons = nlp_results["persons"]
    locations = nlp_results["locations"]
    phones = nlp_results["phones"]
    vehicles = nlp_results["vehicles"]
    organizations = nlp_results["organizations"]


    # =====================================================
    # OCR
    # =====================================================

    st.divider()

    with st.expander(
        "View OCR Text"
    ):

        st.text_area(
            "Recognized text",
            fir_text,
            height=190,
            label_visibility="collapsed"
        )


    # =====================================================
    # EXTRACTED INTELLIGENCE
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        'Extracted Intelligence'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-accent"></div>',
        unsafe_allow_html=True
    )


    m1, m2, m3, m4, m5 = st.columns(5)


    m1.metric(
        "Persons",
        len(persons)
    )

    m2.metric(
        "Locations",
        len(locations)
    )

    m3.metric(
        "Phones",
        len(phones)
    )

    m4.metric(
        "Vehicles",
        len(vehicles)
    )

    m5.metric(
        "Organizations",
        len(organizations)
    )


    # =====================================================
    # ENTITY DETAILS
    # =====================================================

    with st.expander(
        "View Extracted Entities"
    ):

        left, right = st.columns(2)

        with left:

            st.markdown("**Persons**")

            st.write(
                persons
                if persons
                else "None"
            )

            st.markdown("**Locations**")

            st.write(
                locations
                if locations
                else "None"
            )

            st.markdown("**Phone Numbers**")

            st.write(
                phones
                if phones
                else "None"
            )

        with right:

            st.markdown("**Vehicles**")

            st.write(
                vehicles
                if vehicles
                else "None"
            )

            st.markdown("**Organizations**")

            st.write(
                organizations
                if organizations
                else "None"
            )


    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    st.divider()

    st.markdown(
        '<div class="section-title">'
        'Extracted Relationships'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-accent"></div>',
        unsafe_allow_html=True
    )


    if relationships:

        for relationship in relationships:

            st.info(
                f"{relationship['person']} "
                f"→ {relationship['relationship']} → "
                f"{relationship['related_person']}"
            )

    else:

        st.info(
            "No relationships were extracted."
        )


    # =====================================================
    # NETWORKX GRAPH
    # =====================================================

    st.divider()

    st.markdown(
        '<div class="section-title">'
        'Network Intelligence'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-accent"></div>',
        unsafe_allow_html=True
    )


    if relationships:

        graph = build_network_graph(
            relationships
        )

        graph_left, graph_right = st.columns(2)

        graph_left.metric(
            "Network Nodes",
            graph.number_of_nodes()
        )

        graph_right.metric(
            "Network Relationships",
            graph.number_of_edges()
        )

        display_network_graph(
            graph
        )

    else:

        st.info(
            "Network visualization requires "
            "extracted relationships."
        )


    # =====================================================
    # ML INPUT
    # =====================================================

    input_fir = []


    for relationship in relationships:

        input_fir.append([
            relationship["person"],
            locations[0] if locations else "",
            phones[0] if phones else "",
            relationship["related_person"],
            relationship["relationship"]
        ])


    # =====================================================
# ML ANALYSIS
# =====================================================

st.divider()

st.subheader("AI-Assisted Leads")

if input_fir:

    with st.spinner("Analyzing historical network..."):

        results = analyze_fir(input_fir)

    if results:

        for result in results:

            candidate = result["Candidate"]
            score = float(result["Score"])

            col1, col2 = st.columns([4, 1])

            with col1:

                st.markdown(
                    f"### {candidate}"
                )

                st.caption(
                    "Person relevance score"
                )

                st.progress(
                    min(
                        max(
                            score / 100,
                            0.0
                        ),
                        1.0
                    )
                )

            with col2:

                st.metric(
                    "Score",
                    f"{score:.2f}/100"
                )

            with st.expander("Analysis details"):

                detail_col1, detail_col2 = st.columns(2)

                with detail_col1:

                    st.write(
                        "Shared locations"
                    )

                    st.write(
                        "Matching phone numbers"
                    )

                    st.write(
                        "FIR appearances"
                    )

                with detail_col2:

                    st.write(
                        "Relationship connections"
                    )

                    st.write(
                        "Network centrality"
                    )

                    st.write(
                        "Graph distance"
                    )

    else:

        st.info(
            "No relevant people were found."
        )

else:

    st.info(
        "Network analysis requires extracted relationships."
    )
# =========================================================
# FOOTER
# =========================================================

st.markdown(
    '<div class="footer-line"></div>',
    unsafe_allow_html=True
)

st.caption(
    "AI-generated network relevance signals support "
    "investigation and do not establish criminality or guilt."
)