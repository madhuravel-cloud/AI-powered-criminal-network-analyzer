import streamlit as st
from ml.predict import analyze_fir


st.set_page_config(
    page_title="Criminal Network Analyzer",
    layout="wide"
)


st.title("Criminal Network Analyzer")
st.write("AI-powered criminal network analysis")


st.subheader("FIR Information")

col1, col2 = st.columns(2)

with col1:
    person = st.text_input("Person")
    location = st.text_input("Location")
    phone = st.text_input("Phone")

with col2:
    related_person = st.text_input("Related Person")
    relationship = st.selectbox(
        "Relationship",
        [
            "associate",
            "friend",
            "relative",
            "colleague"
        ]
    )


if st.button("Analyze FIR"):

    if not person or not location or not phone or not related_person:
        st.warning("Please fill all fields.")

    else:

        input_fir = [
            [
                person,
                location,
                phone,
                related_person,
                relationship
            ]
        ]

        results = analyze_fir(input_fir)

        if not results:

            st.info("No relevant people found.")

        else:

            st.subheader("Person Relevance Scores")

            for result in results:

                st.metric(
                    result["Candidate"],
                    f'{result["Score"]}/100'
                )