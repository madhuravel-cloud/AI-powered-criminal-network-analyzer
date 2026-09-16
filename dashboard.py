import streamlit as st

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


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown("""
<div class="header">
    <h1>🔎 Criminal Network Analyzer</h1>
    <p>AI-Powered Cross-FIR Investigation Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# FIR INPUT
# --------------------------------------------------

st.markdown(
    '<div class="section">📄 FIR Input</div>',
    unsafe_allow_html=True
)


fir_text = st.text_area(
    "Enter FIR details",
    height=220,
    placeholder=(
        "Example:\n"
        "Ravi met Arun at Kochi railway station. "
        "Arun contacted Kumar using 9876543211. "
        "Kumar was travelling in a white Toyota car."
    ),
    label_visibility="collapsed"
)


analyze_button = st.button(
    "🔍 Analyze FIR",
    use_container_width=True
)


if analyze_button:

    if not fir_text.strip():

        st.warning("Please enter FIR text.")

    else:

        # --------------------------------------------------
        # NLP
        # --------------------------------------------------

        nlp_results = analyze_fir_text(fir_text)


        # --------------------------------------------------
        # EXTRACTED INTELLIGENCE
        # --------------------------------------------------

        st.markdown(
            '<div class="section">🧠 Extracted Intelligence</div>',
            unsafe_allow_html=True
        )


        persons = nlp_results["persons"]
        locations = nlp_results["locations"]
        phones = nlp_results["phones"]
        vehicles = nlp_results["vehicles"]
        organizations = nlp_results["organizations"]


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


        # --------------------------------------------------
        # ENTITY DETAILS
        # --------------------------------------------------

        with st.expander("View Extracted Entities"):

            col1, col2 = st.columns(2)


            with col1:

                st.write("**Persons**")

                if persons:
                    for person in persons:
                        st.write(f"• {person}")
                else:
                    st.write("None")


                st.write("**Locations**")

                if locations:
                    for location in locations:
                        st.write(f"• {location}")
                else:
                    st.write("None")


                st.write("**Phone Numbers**")

                if phones:
                    for phone in phones:
                        st.write(f"• {phone}")
                else:
                    st.write("None")


            with col2:

                st.write("**Vehicles**")

                if vehicles:
                    for vehicle in vehicles:
                        st.write(f"• {vehicle}")
                else:
                    st.write("None")


                st.write("**Organizations**")

                if organizations:
                    for organization in organizations:
                        st.write(f"• {organization}")
                else:
                    st.write("None")


        # --------------------------------------------------
        # RELATIONSHIPS
        # --------------------------------------------------

        st.markdown(
            '<div class="section">🔗 Extracted Relationships</div>',
            unsafe_allow_html=True
        )


        relationships = nlp_results["relationships"]


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


        # --------------------------------------------------
        # BUILD INPUT FIR
        # --------------------------------------------------

        input_fir = []


        for relationship in relationships:

            person = relationship["person"]

            related_person = relationship["related_person"]

            relation = relationship["relationship"]


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


        # --------------------------------------------------
        # NETWORK ANALYSIS
        # --------------------------------------------------

        st.markdown(
            '<div class="section">🕸️ Network Intelligence</div>',
            unsafe_allow_html=True
        )


        if input_fir:

            results = analyze_fir(input_fir)


            if results:

                st.markdown(
                    '<div class="section">🎯 AI-Assisted Leads</div>',
                    unsafe_allow_html=True
                )


                for result in results:

                    candidate = result["Candidate"]

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
                        min(max(score / 100, 0.0), 1.0)
                    )


                    with st.expander(
                        f"Why is {candidate} relevant?"
                    ):

                        st.write(
                            "The score is derived from network "
                            "and cross-FIR features such as:"
                        )

                        st.write("• Shared locations")
                        st.write("• Matching phone numbers")
                        st.write("• Number of FIR appearances")
                        st.write("• Relationship connections")
                        st.write("• Network centrality")
                        st.write("• Graph distance from input FIR")


            else:

                st.info(
                    "No relevant people found in the historical network."
                )


        else:

            st.info(
                "Network analysis requires extracted relationships."
            )


        # --------------------------------------------------
        # DISCLAIMER
        # --------------------------------------------------

        st.caption(
            "AI scores indicate network relevance for investigation "
            "and do not establish criminality or guilt."
        )