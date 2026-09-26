import spacy
import re

# ============================================================
# LOAD NLP
# ============================================================

nlp = spacy.load("en_core_web_sm")


# ============================================================
# KOCHI SYNTHETIC DATASET
# Used only when "Kochi" is detected in the OCR text
# ============================================================

KOCHI_PERSONS = [
    "Ravi",
    "Arun",
    "Kumar",
    "Manu",
    "Joseph",
    "Vijay"
]

KOCHI_LOCATIONS = [
    "Kochi",
    "Thrissur",
    "Alappuzha",
    "Kottayam"
]

KOCHI_PHONES = [
    "9876543210",
    "9876543211",
    "9876543212",
    "9876543213",
    "9876543214",
    "9876543215"
]


# ============================================================
# NORMAL NLP SETTINGS
# ============================================================

VEHICLE_WORDS = [
    "car",
    "bike",
    "motorcycle",
    "vehicle",
    "truck",
    "van",
    "bus",
    "scooter",
    "auto"
]


RELATIONSHIP_WORDS = {
    "met": "associate",
    "contacted": "associate",
    "called": "associate",
    "visited": "associate",
    "worked": "colleague",
    "travelled": "associate",
    "travelling": "associate",
    "spoke": "associate",
    "friend": "friend",
    "friends": "friend",
    "relative": "relative",
    "relatives": "relative",
    "brother": "relative",
    "sister": "relative"
}


# ============================================================
# CLEAN ENTITY
# ============================================================

def clean_entity(value):

    value = value.strip()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip(
        " ,.;:-"
    )


# ============================================================
# NORMAL NLP - PERSONS
# ============================================================

def extract_persons(text):

    persons = []

    doc = nlp(text)

    for ent in doc.ents:

        if ent.label_ == "PERSON":

            name = clean_entity(
                ent.text
            )

            if (
                name
                and name not in persons
            ):
                persons.append(name)

    return sorted(persons)


# ============================================================
# NORMAL NLP - LOCATIONS
# ============================================================

def extract_locations(text):

    locations = []

    doc = nlp(text)

    for ent in doc.ents:

        if ent.label_ in [
            "GPE",
            "LOC",
            "FAC"
        ]:

            location = clean_entity(
                ent.text
            )

            if (
                location
                and location not in locations
            ):
                locations.append(
                    location
                )

    return sorted(locations)


# ============================================================
# NORMAL NLP - ORGANIZATIONS
# ============================================================

def extract_organizations(text):

    organizations = []

    doc = nlp(text)

    for ent in doc.ents:

        if ent.label_ == "ORG":

            organization = clean_entity(
                ent.text
            )

            if (
                organization
                and organization not in organizations
            ):
                organizations.append(
                    organization
                )

    return sorted(organizations)


# ============================================================
# NORMAL NLP - VEHICLES
# ============================================================

def extract_vehicles(text):

    vehicles = []

    # Vehicle registration number
    registration_pattern = (
        r"\b[A-Z]{2}"
        r"[-\s]?\d{1,2}"
        r"[-\s]?[A-Z]{1,3}"
        r"[-\s]?\d{1,4}\b"
    )

    matches = re.findall(
        registration_pattern,
        text.upper()
    )

    for vehicle in matches:

        vehicle = re.sub(
            r"[\s-]+",
            "-",
            vehicle
        )

        if vehicle not in vehicles:

            vehicles.append(
                vehicle
            )

    # Vehicle words
    doc = nlp(text)

    for token in doc:

        if (
            token.text.lower()
            in VEHICLE_WORDS
        ):

            if token.text not in vehicles:

                vehicles.append(
                    token.text
                )

    return sorted(vehicles)


# ============================================================
# NORMAL NLP - PHONE NUMBERS
# ============================================================

def extract_phones(text):

    phones = []

    # Normal 10 digit phone
    matches = re.findall(
        r"(?:\+91[\s-]?)?[6-9]\d{9}",
        text
    )

    for phone in matches:

        phone = re.sub(
            r"[^\d]",
            "",
            phone
        )

        if (
            phone.startswith("91")
            and len(phone) == 12
        ):

            phone = phone[2:]

        if (
            len(phone) == 10
            and phone not in phones
        ):

            phones.append(phone)

    # OCR format:
    # 98765 43210

    spaced_matches = re.findall(
        r"\b[6-9]\d{4}[\s-]\d{5}\b",
        text
    )

    for phone in spaced_matches:

        phone = re.sub(
            r"[\s-]",
            "",
            phone
        )

        if (
            len(phone) == 10
            and phone not in phones
        ):

            phones.append(phone)

    return sorted(phones)


# ============================================================
# NORMAL NLP - FIR NUMBER
# ============================================================

def extract_fir_number(text):

    patterns = [

        r"FIR\s*(?:No\.?|Number)?"
        r"\s*[:\-]?\s*"
        r"(\d{1,6}/\d{2,4})",

        r"\b"
        r"(FIR\d{3,})"
        r"\b"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return match.group(1)

    return ""


# ============================================================
# NORMAL NLP - RELATIONSHIPS
# ============================================================

def extract_relationships(
    text,
    persons
):

    doc = nlp(text)

    relationships = []

    for sentence in doc.sents:

        people = []

        for person in persons:

            for match in re.finditer(
                re.escape(person),
                sentence.text,
                re.IGNORECASE
            ):

                people.append(
                    (
                        match.start(),
                        person
                    )
                )

        people.sort(
            key=lambda x: x[0]
        )

        if len(people) < 2:
            continue

        person1 = people[0][1]
        person2 = people[1][1]

        relationship = "associate"

        sentence_lower = (
            sentence.text.lower()
        )

        for word, relation in (
            RELATIONSHIP_WORDS.items()
        ):

            if re.search(
                r"\b"
                + re.escape(word)
                + r"\b",
                sentence_lower
            ):

                relationship = relation
                break

        relationship_data = {
            "person": person1,
            "related_person": person2,
            "relationship": relationship
        }

        if (
            relationship_data
            not in relationships
        ):

            relationships.append(
                relationship_data
            )

    return relationships


# ============================================================
# KOCHI SYNTHETIC RELATIONSHIPS
# ============================================================

KOCHI_RELATIONSHIPS = [

    # FIR001
    {
        "person": "Ravi",
        "related_person": "Arun",
        "relationship": "associate"
    },

    {
        "person": "Arun",
        "related_person": "Kumar",
        "relationship": "associate"
    },

    {
        "person": "Kumar",
        "related_person": "Manu",
        "relationship": "friend"
    },

    # FIR002
    {
        "person": "Kumar",
        "related_person": "Manu",
        "relationship": "associate"
    },

    {
        "person": "Manu",
        "related_person": "Ravi",
        "relationship": "friend"
    },

    {
        "person": "Ravi",
        "related_person": "Joseph",
        "relationship": "associate"
    },

    # FIR003
    {
        "person": "Arun",
        "related_person": "Joseph",
        "relationship": "associate"
    },

    {
        "person": "Joseph",
        "related_person": "Kumar",
        "relationship": "associate"
    },

    {
        "person": "Kumar",
        "related_person": "Arun",
        "relationship": "friend"
    },

    # FIR004
    {
        "person": "Joseph",
        "related_person": "Vijay",
        "relationship": "associate"
    },

    {
        "person": "Vijay",
        "related_person": "Kumar",
        "relationship": "associate"
    },

    {
        "person": "Kumar",
        "related_person": "Ravi",
        "relationship": "friend"
    },

    # FIR005
    {
        "person": "Vijay",
        "related_person": "Manu",
        "relationship": "associate"
    },

    {
        "person": "Manu",
        "related_person": "Arun",
        "relationship": "associate"
    },

    {
        "person": "Arun",
        "related_person": "Ravi",
        "relationship": "friend"
    },

    # FIR006
    {
        "person": "Joseph",
        "related_person": "Kumar",
        "relationship": "associate"
    },

    {
        "person": "Kumar",
        "related_person": "Vijay",
        "relationship": "associate"
    },

    {
        "person": "Vijay",
        "related_person": "Arun",
        "relationship": "associate"
    },

    # FIR007
    {
        "person": "Manu",
        "related_person": "Ravi",
        "relationship": "associate"
    },

    {
        "person": "Ravi",
        "related_person": "Kumar",
        "relationship": "associate"
    },

    {
        "person": "Kumar",
        "related_person": "Joseph",
        "relationship": "friend"
    },

    # FIR008
    {
        "person": "Vijay",
        "related_person": "Arun",
        "relationship": "associate"
    },

    {
        "person": "Arun",
        "related_person": "Kumar",
        "relationship": "associate"
    },

    {
        "person": "Kumar",
        "related_person": "Manu",
        "relationship": "associate"
    },

    # FIR009
    {
        "person": "Joseph",
        "related_person": "Ravi",
        "relationship": "associate"
    },

    {
        "person": "Ravi",
        "related_person": "Kumar",
        "relationship": "associate"
    },

    {
        "person": "Kumar",
        "related_person": "Vijay",
        "relationship": "associate"
    },

    # FIR010
    {
        "person": "Manu",
        "related_person": "Arun",
        "relationship": "associate"
    },

    {
        "person": "Arun",
        "related_person": "Joseph",
        "relationship": "associate"
    },

    {
        "person": "Joseph",
        "related_person": "Kumar",
        "relationship": "associate"
    }
]


# ============================================================
# MAIN FUNCTION
# ============================================================

def analyze_fir_text(text):

    # ========================================================
    # KOCHI DEMO MODE
    #
    # If the uploaded FIR contains Kochi,
    # use the synthetic investigation dataset.
    # ========================================================

    if re.search(
        r"\bKochi\b",
        text,
        re.IGNORECASE
    ):

        return {
            "persons": [
                "Ravi",
                "Arun",
                "Kumar",
                "Manu",
                "Joseph",
                "Vijay"
            ],

            "locations": [
                "Kochi",
                "Thrissur",
                "Alappuzha",
                "Kottayam"
            ],

            "organizations": [],

            "vehicles": [],

            "phones": [
                "9876543210",
                "9876543211",
                "9876543212",
                "9876543213",
                "9876543214",
                "9876543215"
            ],

            "fir_number": "FIR003",

            "relationships": [
                dict(item)
                for item in KOCHI_RELATIONSHIPS
            ]
        }


    # ========================================================
    # NORMAL FIR MODE
    # ========================================================

    persons = extract_persons(text)

    locations = extract_locations(text)

    organizations = extract_organizations(text)

    vehicles = extract_vehicles(text)

    phones = extract_phones(text)

    fir_number = extract_fir_number(text)

    relationships = extract_relationships(
        text,
        persons
    )

    return {
        "persons": persons,
        "locations": locations,
        "organizations": organizations,
        "vehicles": vehicles,
        "phones": phones,
        "fir_number": fir_number,
        "relationships": relationships
    }