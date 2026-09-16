import os

import streamlit as st

from ocr import extract_and_clean_text
from ml.nlp import analyze_fir_text
from ml.predict import analyze_fir


st.set_page_config(
    page_title="Criminal Network Analyzer",
    page_icon="🔎",
    layout="wide"
)


st.markdown("""
<style>

.main {
    background-color: #f5f7fb;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.header {
    padding: 1.5rem 2rem;
    border-radius: 15px;
    background: #111827;
    color: white;
    margin-bottom: 1.5rem;
}

.header h1 {
    margin: 0;
    font-size: 2rem;
}

.header p {
    margin-top: 0.4rem;
    color: #cbd5e1;
}

.section {
    font-size: 1.25rem;
    font-weight: 700;
    margin-top: 1.5rem;
    margin-bottom: 0.8rem;
}

.metric-card {
    padding: 1rem;
    border-radius: 12px;
    background: white;
    border: 1px solid #e5e7eb;
    text-align: center;
}

.metric-number {
    font-size: 1.8rem;
    font-weight: 700;
}

.metric-label {
    color: #64748b;
    font-size: 0.9rem;
}

.score-card {
    padding: 1.2rem;
    border-radius: 12px;
    background: white;
    border: 1px solid #e5e7eb;
    margin-bottom: 0.5rem;
}

.score-name {
    font-size: 1.15rem;
    font-weight: 700;
}

.score-value {
    font-size: 1.8rem;
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="header">
    <h1>🔎 Criminal Network Analyzer</h1>
    <p>AI-Powered Cross-FIR Investigation Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# FIR IMAGE INPUT
# ---------------------------------------------------------

st.markdown(
    '<div class="section">📄 FIR Input</div>',
    unsafe_allow_html=True
)


uploaded_file = st.file_uploader(
    "Upload FIR / Evidence Image",
    type=["png", "jpg", "jpeg"]
)


analyze_button = st.button(
    "🔍 Analyze FIR",
    use_container_width=True
)


# ---------------------------------------------------------
# ANALYSIS
# ---------------------------------------------------------

if analyze_button:

    if uploaded_file is None:

        st.warning("Please upload an FIR image.")

    else:

        temp_path = "temp_fir.png"

        try:

            # -------------------------------------------------
            # SAVE UPLOADED IMAGE
            # -------------------------------------------------

            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())


            # -------------------------------------------------
            # DISPLAY IMAGE
            # -------------------------------------------------

            st.markdown(
                '<div class="section">🖼️ Uploaded FIR</div>',
                unsafe_allow_html=True
            )

            st.image(
                uploaded_file,
                caption="Uploaded FIR Document",
                use_container_width=True
            )


            # -------------------------------------------------
            # OCR
            # -------------------------------------------------

            st.markdown(
                '<div class="section">🔤 OCR Processing</div>',
                unsafe_allow_html=True
            )

            with st.spinner(
                "Extracting text from FIR image..."
            ):

                ocr_results = extract_and_clean_text(
                    temp_path
                )


            if not ocr_results:

                st.error(
                    "No text could be extracted from the uploaded image."
                )

            else:

                fir_text = " ".join(
                    result["text"]
                    for result in ocr_results
                )


                # -------------------------------------------------
                # OCR TEXT
                # -------------------------------------------------

                with st.expander(
                    "📄 View OCR Extracted Text",
                    expanded=True
                ):

                    st.text_area(
                        "Extracted FIR Text",
                        fir_text,
                        height=220
                    )


                # -------------------------------------------------
                # NLP
                # -------------------------------------------------

                st.markdown(
                    '<div class="section">🧠 Extracted Intelligence</div>',
                    unsafe_allow_html=True
                )

                with st.spinner(
                    "Analyzing entities and relationships..."
                ):

                    nlp_results = analyze_fir_text(
                        fir_text
                    )


                persons = nlp_results["persons"]

                locations = nlp_results["locations"]

                phones = nlp_results["phones"]

                vehicles = nlp_results["vehicles"]

                organizations = nlp_results["organizations"]

                relationships = nlp_results["relationships"]


                # -------------------------------------------------
                # INTELLIGENCE METRICS
                # -------------------------------------------------

                cols = st.columns(5)

                metrics = [
                    ("👤", len(persons), "Persons"),
                    ("📍", len(locations), "Locations"),
                    ("📞", len(phones), "Phones"),
                    ("🚗", len(vehicles), "Vehicles"),
                    ("🏢", len(organizations), "Organizations")
                ]


                for col, metric in zip(cols, metrics):

                    icon, number, label = metric

                    with col:

                        st.markdown(
                            f"""
                            <div class="metric-card">

                                <div class="metric-number">
                                    {icon} {number}
                                </div>

                                <div class="metric-label">
                                    {label}
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )


                # -------------------------------------------------
                # EXTRACTED ENTITIES
                # -------------------------------------------------

                with st.expander(
                    "View Extracted Entities"
                ):

                    col1, col2 = st.columns(2)


                    with col1:

                        st.write("**Persons**")

                        if persons:

                            for person in persons:
                                st.write(
                                    f"• {person}"
                                )

                        else:

                            st.write("None")


                        st.write("**Locations**")

                        if locations:

                            for location in locations:
                                st.write(
                                    f"• {location}"
                                )

                        else:

                            st.write("None")


                        st.write("**Phone Numbers**")

                        if phones:

                            for phone in phones:
                                st.write(
                                    f"• {phone}"
                                )

                        else:

                            st.write("None")


                    with col2:

                        st.write("**Vehicles**")

                        if vehicles:

                            for vehicle in vehicles:
                                st.write(
                                    f"• {vehicle}"
                                )

                        else:

                            st.write("None")


                        st.write("**Organizations**")

                        if organizations:

                            for organization in organizations:
                                st.write(
                                    f"• {organization}"
                                )

                        else:

                            st.write("None")


                # -------------------------------------------------
                # RELATIONSHIPS
                # -------------------------------------------------

                st.markdown(
                    '<div class="section">🔗 Extracted Relationships</div>',
                    unsafe_allow_html=True
                )


                if relationships:

                    for relationship in relationships:

                        st.info(
                            f"**{relationship['person']}** "
                            f"→ {relationship['relationship']} → "
                            f"**{relationship['related_person']}**"
                        )

                else:

                    st.info(
                        "No relationships were extracted."
                    )


                # -------------------------------------------------
                # CONVERT NLP OUTPUT TO ML INPUT
                # -------------------------------------------------

                input_fir = []


                for relationship in relationships:

                    person = relationship["person"]

                    related_person = (
                        relationship["related_person"]
                    )

                    relation = (
                        relationship["relationship"]
                    )


                    location = (
                        locations[0]
                        if locations
                        else ""
                    )


                    phone = (
                        phones[0]
                        if phones
                        else ""
                    )


                    input_fir.append([
                        person,
                        location,
                        phone,
                        related_person,
                        relation
                    ])


                # -------------------------------------------------
                # NETWORK ANALYSIS
                # -------------------------------------------------

                st.markdown(
                    '<div class="section">🕸️ Network Intelligence</div>',
                    unsafe_allow_html=True
                )


                if input_fir:

                    with st.spinner(
                        "Analyzing the criminal network..."
                    ):

                        results = analyze_fir(
                            input_fir
                        )


                    # -------------------------------------------------
                    # AI-ASSISTED LEADS
                    # -------------------------------------------------

                    if results:

                        st.markdown(
                            '<div class="section">🎯 AI-Assisted Leads</div>',
                            unsafe_allow_html=True
                        )


                        for result in results:

                            candidate = (
                                result["Candidate"]
                            )

                            score = float(
                                result["Score"]
                            )


                            col1, col2 = st.columns(
                                [3, 1]
                            )


                            with col1:

                                st.markdown(
                                    f"""
                                    <div class="score-card">

                                        <div class="score-name">
                                            👤 {candidate}
                                        </div>

                                        <div class="metric-label">
                                            Person Relevance Score
                                        </div>

                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )


                            with col2:

                                st.metric(
                                    "Relevance Score",
                                    f"{score:.2f}/100"
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


                            with st.expander(
                                f"Why is {candidate} relevant?"
                            ):

                                st.write(
                                    "The score is derived from "
                                    "network and cross-FIR features "
                                    "such as:"
                                )

                                st.write(
                                    "• Shared locations"
                                )

                                st.write(
                                    "• Matching phone numbers"
                                )

                                st.write(
                                    "• Number of FIR appearances"
                                )

                                st.write(
                                    "• Relationship connections"
                                )

                                st.write(
                                    "• Network centrality"
                                )

                                st.write(
                                    "• Graph distance from input FIR"
                                )


                    else:

                        st.info(
                            "No relevant people found "
                            "in the historical network."
                        )


                else:

                    st.info(
                        "Network analysis requires "
                        "extracted relationships."
                    )


                # -------------------------------------------------
                # DISCLAIMER
                # -------------------------------------------------

                st.caption(
                    "AI scores indicate network relevance "
                    "for investigation and do not establish "
                    "criminality or guilt."
                )


        except Exception as e:

            st.error(
                "An error occurred while processing the FIR."
            )

            st.exception(e)


        finally:

            # -------------------------------------------------
            # REMOVE TEMPORARY IMAGE
            # -------------------------------------------------

            if os.path.exists(temp_path):

                os.remove(temp_path)