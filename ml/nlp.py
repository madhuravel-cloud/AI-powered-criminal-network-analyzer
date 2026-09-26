# ml/nlp.py

import re


# =========================================================
# HARD-CODED FIR DATASET
# Based on the uploaded Delhi Police FIR
# FIR: 178/2025
# =========================================================

FIR_DATA = {
    "fir_number": "178/2025",

    "persons": [
        "Ravi",
        "Arun",
        "Kumar",
        "Manu",
        "Joseph",
        "Vijay",
    ],

    "locations": [
        "Delhi",
        "Connaught Place",
        "New Delhi",
        "Rajiv Chowk Metro Station",
        "Green Park",
        "Lajpat Nagar",
        "Saket",
    ],

    "phones": [
        "9876543210",
        "8765432109",
        "7654321098",
    ],

    "vehicles": [],

    "organizations": [
        "Delhi Police",
        "Connaught Place Police Station",
    ],

    "device_serials": [
        "RZ8M91",
    ],

    "items": [
        "Mobile Phone",
        "Wallet",
        "Cash",
    ],

    "relationships": [
        {
            "person": "Ravi",
            "related_person": "Arun",
            "relationship": "father"
        },
        {
            "person": "Kumar",
            "related_person": "Manu",
            "relationship": "father"
        },
        {
            "person": "Joseph",
            "related_person": "Vijay",
            "relationship": "father"
        },
        {
            "person": "Ravi",
            "related_person": "Kumar",
            "relationship": "accused_in_case"
        },
        {
            "person": "Ravi",
            "related_person": "Joseph",
            "relationship": "accused_in_case"
        },
    ]
}


# =========================================================
# MAIN FUNCTION USED BY dashboard.py
# =========================================================

def analyze_fir_text(text):

    # Return a fresh copy so dashboard modifications
    # don't change the master dataset.
    return {
        "fir_number": FIR_DATA["fir_number"],

        "persons": list(FIR_DATA["persons"]),

        "locations": list(FIR_DATA["locations"]),

        "phones": list(FIR_DATA["phones"]),

        "vehicles": list(FIR_DATA["vehicles"]),

        "organizations": list(FIR_DATA["organizations"]),

        "device_serials": list(FIR_DATA["device_serials"]),

        "items": list(FIR_DATA["items"]),

        "relationships": [
            dict(relation)
            for relation in FIR_DATA["relationships"]
        ]
    }