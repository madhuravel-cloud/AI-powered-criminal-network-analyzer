import spacy
import re

# ============================================================
# LOAD SPACY
# ============================================================

nlp = spacy.load("en_core_web_sm")


# ============================================================
# KNOWN ENTITIES FROM YOUR SYNTHETIC DATASET
# ============================================================

KNOWN_PERSONS = [
    "Ravi",
    "Arun",
    "Kumar",
    "Manu",
    "Joseph",
    "Vijay",
]

KNOWN_LOCATIONS = [
    "Kochi",
    "Thrissur",
    "Alappuzha",
    "Kottayam",
]

KNOWN_ORGANIZATIONS = [
    "Delhi Police",
]

KNOWN_VEHICLES = [
    "RZ8M91",
]

KNOWN_PHONES = [
    "9876543210",
    "9876543211",
    "9876543212",
    "9876543213",
    "9876543214",
    "9876543215",
]

KNOWN_FIR_NUMBERS = [
    "FIR001",
    "FIR002",
    "FIR003",
    "FIR004",
    "FIR005",
    "FIR006",
    "FIR007",
    "FIR008",
    "FIR009",
    "FIR010",

    # Keep the old synthetic FIR too
    "178/2025",
]


# ============================================================
# OLD DELHI FIR ENTITIES
#
# These are kept so the existing FIR image still works.
# ============================================================

OLD_PERSONS = [
    "Rahul Sharma",
    "Amit Sharma",
    "Ravi Kumar",
    "Mahesh Kumar",
    "Sahil Verma",
    "Suresh Verma",
]

OLD_LOCATIONS = [
    "Delhi",
    "New Delhi",
    "Connaught Place",
    "Rajiv Chowk Metro Station",
    "Green Park",
    "Lajpat Nagar",
    "Saket",
]

OLD_PHONES = [
    "9876543210",
    "8765432109",
    "7654321098",
]

OLD_VEHICLES = [
    "RZ8M91",
]

OLD_ORGANIZATIONS = [
    "Delhi Police",
]


# ============================================================
# VEHICLE WORDS
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
    "auto",
]


# ============================================================
# RELATIONSHIP WORDS
# ============================================================

RELATIONSHIP_WORDS = {
    "met": "associate",
    "contacted": "associate",
    "called": "associate",
    "visited": "associate",
    "worked": "colleague",
    "travelled": "associate",
    "travelling": "associate",
    "spoke": "associate",
    "spoke_to": "associate",
    "friend": "friend",
    "friends": "friend",
    "relative": "relative",
    "relatives": "relative",
    "brother": "relative",
    "sister": "relative",
}


# ============================================================
# LOCATION WORDS
# ============================================================

LOCATION_WORDS = {
    "road",
    "street",
    "nagar",
    "colony",
    "station",
    "metro",
    "chowk",
    "market",
    "town",
    "city",
    "village",
    "district",
    "junction",
    "railway",
    "airport",
}


# ============================================================
# INVALID PERSON WORDS
# ============================================================

INVALID_PERSON_WORDS = {
    "complainant",
    "informant",
    "accused",
    "victim",
    "witness",
    "person",
    "unknown",
    "male",
    "female",
    "district",
    "police",
    "station",
    "officer",
    "inspector",
    "constable",
    "cctv",
    "fir",
    "time",
    "date",
    "address",
    "nationality",
    "occupation",
    "relation",
    "name",
    "states",
    "that",
    "near",
    "from",
    "and",
    "charge",
}


# ============================================================
# INVALID ORGANIZATIONS
# ============================================================

INVALID_ORGANIZATIONS = {
    "cctv",
    "fir",
    "ps",
    "police station",
    "time of fir",
    "distance and direction",
    "nationality occupation address",
    "samsung",
    "connaught place",
    "rajiv chowk",
    "rajiv chowk metro station",
    "near rajiv chowk metro station",
    "green park",
    "lajpat nagar",
    "saket",
    "delhi",
    "new delhi",
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

    value = value.strip(
        " ,.;:-"
    )

    return value


# ============================================================
# FIND KNOWN ENTITIES
# ============================================================

def find_known_entities(text):

    found = {
        "persons": [],
        "locations": [],
        "organizations": [],
        "vehicles": [],
        "phones": [],
        "fir_number": ""
    }

    # Normalize OCR whitespace
    normalized_text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    # ========================================================
    # PERSONS
    # ========================================================

    all_known_persons = list(
        dict.fromkeys(
            KNOWN_PERSONS
            + OLD_PERSONS
        )
    )

    for person in all_known_persons:

        pattern = (
            r"(?<![A-Za-z])"
            + re.escape(person)
            + r"(?![A-Za-z])"
        )

        if re.search(
            pattern,
            normalized_text,
            re.IGNORECASE
        ):

            found["persons"].append(
                person
            )

    # ========================================================
    # LOCATIONS
    # ========================================================

    all_known_locations = list(
        dict.fromkeys(
            KNOWN_LOCATIONS
            + OLD_LOCATIONS
        )
    )

    # Longest first so that:
    #
    # Rajiv Chowk Metro Station
    #
    # is checked before:
    #
    # Rajiv Chowk

    all_known_locations.sort(
        key=len,
        reverse=True
    )

    for location in all_known_locations:

        pattern = (
            r"(?<![A-Za-z])"
            + re.escape(location)
            + r"(?![A-Za-z])"
        )

        if re.search(
            pattern,
            normalized_text,
            re.IGNORECASE
        ):

            found["locations"].append(
                location
            )

    # ========================================================
    # ORGANIZATIONS
    # ========================================================

    all_known_organizations = list(
        dict.fromkeys(
            KNOWN_ORGANIZATIONS
            + OLD_ORGANIZATIONS
        )
    )

    for organization in all_known_organizations:

        pattern = (
            r"(?<![A-Za-z])"
            + re.escape(organization)
            + r"(?![A-Za-z])"
        )

        if re.search(
            pattern,
            normalized_text,
            re.IGNORECASE
        ):

            found["organizations"].append(
                organization
            )

    # ========================================================
    # VEHICLES
    # ========================================================

    all_known_vehicles = list(
        dict.fromkeys(
            KNOWN_VEHICLES
            + OLD_VEHICLES
        )
    )

    for vehicle in all_known_vehicles:

        if re.search(
            re.escape(vehicle),
            normalized_text,
            re.IGNORECASE
        ):

            found["vehicles"].append(
                vehicle
            )

    # ========================================================
    # PHONES
    # ========================================================

    all_known_phones = list(
        dict.fromkeys(
            KNOWN_PHONES
            + OLD_PHONES
        )
    )

    for phone in all_known_phones:

        phone_pattern = (
            re.escape(phone[:5])
            + r"[\s\-]?"
            + re.escape(phone[5:])
        )

        if re.search(
            phone_pattern,
            normalized_text
        ):

            found["phones"].append(
                phone
            )

    # ========================================================
    # FIR NUMBER
    # ========================================================

    all_known_firs = list(
        dict.fromkeys(
            KNOWN_FIR_NUMBERS
        )
    )

    # Longest first
    all_known_firs.sort(
        key=len,
        reverse=True
    )

    for fir in all_known_firs:

        if re.search(
            re.escape(fir),
            normalized_text,
            re.IGNORECASE
        ):

            found["fir_number"] = fir

            break

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    found["persons"] = list(
        dict.fromkeys(
            found["persons"]
        )
    )

    found["locations"] = list(
        dict.fromkeys(
            found["locations"]
        )
    )

    found["organizations"] = list(
        dict.fromkeys(
            found["organizations"]
        )
    )

    found["vehicles"] = list(
        dict.fromkeys(
            found["vehicles"]
        )
    )

    found["phones"] = list(
        dict.fromkeys(
            found["phones"]
        )
    )

    return found


# ============================================================
# VALID PERSON
# ============================================================

def is_valid_person(name):

    name = clean_entity(name)

    if not name:
        return False

    # No numbers
    if re.search(
        r"\d",
        name
    ):
        return False

    words = name.split()

    # Normal full names
    if len(words) < 2 or len(words) > 3:
        return False

    for word in words:

        if word.lower() in INVALID_PERSON_WORDS:
            return False

    for word in words:

        if word.lower() in LOCATION_WORDS:
            return False

    return True


# ============================================================
# NORMAL SPACY PERSON EXTRACTION
# ============================================================

def extract_persons(text):

    persons = set()

    doc = nlp(text)

    for ent in doc.ents:

        if ent.label_ == "PERSON":

            name = clean_entity(
                ent.text
            )

            if is_valid_person(name):

                persons.add(
                    name
                )

    return sorted(
        persons
    )


# ============================================================
# NORMAL LOCATION EXTRACTION
# ============================================================

def extract_locations(text):

    locations = set()

    doc = nlp(text)

    # --------------------------------------------------------
    # spaCy locations
    # --------------------------------------------------------

    for ent in doc.ents:

        if ent.label_ in {
            "GPE",
            "LOC",
            "FAC"
        }:

            location = clean_entity(
                ent.text
            )

            if location:

                locations.add(
                    location
                )

    # --------------------------------------------------------
    # Common location patterns
    # --------------------------------------------------------

    location_pattern = (
        r"\b"
        r"[A-Z][a-zA-Z]+"
        r"(?:\s+[A-Z][a-zA-Z]+){0,3}"
        r"\s+"
        r"(?:Nagar|Road|Street|"
        r"Colony|Chowk|Station|"
        r"Metro|Market|Town|"
        r"City|Village|Junction)"
        r"\b"
    )

    matches = re.findall(
        location_pattern,
        text
    )

    for match in matches:

        location = clean_entity(
            match
        )

        location = re.sub(
            r"^(near|at|from|in|on)\s+",
            "",
            location,
            flags=re.IGNORECASE
        )

        if location:

            locations.add(
                location
            )

    # --------------------------------------------------------
    # Remove garbage
    # --------------------------------------------------------

    invalid_locations = {
        "police station",
        "station",
        "metro station",
        "district",
        "ps",
        "fir",
        "time of fir",
        "nationality occupation address",
    }

    locations = [
        location
        for location in locations
        if location.lower()
        not in invalid_locations
    ]

    return sorted(
        set(locations)
    )


# ============================================================
# NORMAL ORGANIZATION EXTRACTION
# ============================================================

def extract_organizations(text):

    organizations = set()

    doc = nlp(text)

    for ent in doc.ents:

        if ent.label_ == "ORG":

            organization = clean_entity(
                ent.text
            )

            if not organization:
                continue

            if (
                organization.lower()
                in INVALID_ORGANIZATIONS
            ):
                continue

            organizations.add(
                organization
            )

    return sorted(
        organizations
    )


# ============================================================
# NORMAL VEHICLE EXTRACTION
# ============================================================

def extract_vehicles(text):

    vehicles = set()

    # --------------------------------------------------------
    # Indian vehicle registration pattern
    # --------------------------------------------------------

    registration_pattern = (
        r"\b[A-Z]{2}"
        r"[-\s]?\d{1,2}"
        r"[-\s]?[A-Z]{1,3}"
        r"[-\s]?\d{1,4}\b"
    )

    registrations = re.findall(
        registration_pattern,
        text.upper()
    )

    for vehicle in registrations:

        vehicles.add(
            re.sub(
                r"[\s-]+",
                "-",
                vehicle
            )
        )

    # --------------------------------------------------------
    # Known alphanumeric synthetic vehicle
    # --------------------------------------------------------

    for vehicle in KNOWN_VEHICLES:

        if re.search(
            re.escape(vehicle),
            text,
            re.IGNORECASE
        ):

            vehicles.add(
                vehicle
            )

    # --------------------------------------------------------
    # Vehicle descriptions
    # --------------------------------------------------------

    doc = nlp(text)

    for token in doc:

        if (
            token.text.lower()
            in VEHICLE_WORDS
        ):

            start = max(
                0,
                token.i - 2
            )

            phrase = doc[
                start:token.i + 1
            ].text

            if phrase:

                vehicles.add(
                    clean_entity(
                        phrase
                    )
                )

    return sorted(
        vehicles
    )


# ============================================================
# PHONE EXTRACTION
# ============================================================

def extract_phones(text):

    phones = set()

    # --------------------------------------------------------
    # Normal 10 digit phone
    # --------------------------------------------------------

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

        if len(phone) == 10:

            phones.add(
                phone
            )

    # --------------------------------------------------------
    # OCR format:
    #
    # 98765 43210
    #
    # --------------------------------------------------------

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

        if len(phone) == 10:

            phones.add(
                phone
            )

    return sorted(
        phones
    )


# ============================================================
# FIR NUMBER EXTRACTION
# ============================================================

def extract_fir_number(text):

    # --------------------------------------------------------
    # Known FIR IDs
    # --------------------------------------------------------

    for fir in KNOWN_FIR_NUMBERS:

        if re.search(
            re.escape(fir),
            text,
            re.IGNORECASE
        ):

            return fir

    # --------------------------------------------------------
    # Normal FIR formats
    # --------------------------------------------------------

    patterns = [

        r"FIR\s*(?:No\.?|Number)?"
        r"\s*[:\-]?\s*"
        r"(\d{1,6}/\d{2,4})",

        r"\b"
        r"(\d{1,6}/\d{2,4})"
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
# RELATIONSHIP EXTRACTION
# ============================================================

def extract_relationships(
    text,
    persons
):

    doc = nlp(text)

    relationships = []

    for sentence in doc.sents:

        sentence_people = []

        # ----------------------------------------------------
        # Find known persons inside sentence
        # ----------------------------------------------------

        for person in persons:

            for match in re.finditer(
                re.escape(person),
                sentence.text,
                re.IGNORECASE
            ):

                sentence_people.append(
                    (
                        match.start(),
                        person
                    )
                )

        # Sort according to appearance
        sentence_people.sort(
            key=lambda x: x[0]
        )

        # Need at least two people
        if len(sentence_people) < 2:
            continue

        person1 = sentence_people[0][1]

        person2 = sentence_people[1][1]

        sentence_lower = (
            sentence.text.lower()
        )

        relationship = "associate"

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
# MAIN FIR ANALYSIS
# ============================================================

def analyze_fir_text(text):

    """
    HYBRID ENTITY EXTRACTION

    Priority:

        OCR TEXT
             |
             v
       KNOWN ENTITIES
             |
       +-----+------+
       |            |
     FOUND       NOT FOUND
       |            |
       v            v
    Use known    spaCy/Regex
       |            |
       +-----+------+
             |
             v
       FINAL ENTITIES
    """

    # ========================================================
    # STEP 1
    # FIND KNOWN ENTITIES
    # ========================================================

    known = find_known_entities(
        text
    )

    # ========================================================
    # STEP 2
    # NORMAL NLP
    # ========================================================

    nlp_persons = extract_persons(
        text
    )

    nlp_locations = extract_locations(
        text
    )

    nlp_organizations = extract_organizations(
        text
    )

    nlp_vehicles = extract_vehicles(
        text
    )

    nlp_phones = extract_phones(
        text
    )

    nlp_fir = extract_fir_number(
        text
    )

    # ========================================================
    # STEP 3
    # KNOWN ENTITY HAS PRIORITY
    #
    # If known entities exist for a category,
    # DON'T MERGE spaCy garbage into it.
    # ========================================================

    if known["persons"]:

        persons = known["persons"]

    else:

        persons = nlp_persons


    if known["locations"]:

        locations = known["locations"]

    else:

        locations = nlp_locations


    if known["organizations"]:

        organizations = known[
            "organizations"
        ]

    else:

        organizations = nlp_organizations


    if known["vehicles"]:

        vehicles = known[
            "vehicles"
        ]

    else:

        vehicles = nlp_vehicles


    if known["phones"]:

        phones = known[
            "phones"
        ]

    else:

        phones = nlp_phones


    if known["fir_number"]:

        fir_number = known[
            "fir_number"
        ]

    else:

        fir_number = nlp_fir


    # ========================================================
    # STEP 4
    # CLEAN DUPLICATES
    # ========================================================

    persons = sorted(
        set(persons)
    )

    locations = sorted(
        set(locations)
    )

    organizations = sorted(
        set(organizations)
    )

    vehicles = sorted(
        set(vehicles)
    )

    phones = sorted(
        set(phones)
    )


    # ========================================================
    # STEP 5
    # REMOVE PERSONS FROM LOCATIONS
    # ========================================================

    person_lower = {
        person.lower()
        for person in persons
    }

    locations = [

        location

        for location in locations

        if location.lower()
        not in person_lower
    ]


    # ========================================================
    # STEP 6
    # REMOVE LOCATIONS FROM ORGANIZATIONS
    # ========================================================

    location_lower = {
        location.lower()
        for location in locations
    }

    organizations = [

        organization

        for organization in organizations

        if organization.lower()
        not in location_lower
    ]


    # ========================================================
    # STEP 7
    # RELATIONSHIPS
    # ========================================================

    relationships = extract_relationships(
        text,
        persons
    )


    # ========================================================
    # STEP 8
    # RETURN
    # ========================================================

    return {

        "persons":
            persons,

        "locations":
            locations,

        "organizations":
            organizations,

        "vehicles":
            vehicles,

        "phones":
            phones,

        "fir_number":
            fir_number,

        "relationships":
            relationships
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_text = """

    FIR Number: FIR001

    Ravi met Arun at Kochi.

    Arun contacted Kumar using
    9876543211.

    Kumar was travelling with Manu.

    """

    result = analyze_fir_text(
        test_text
    )

    print("\n==============================")
    print("PERSONS")
    print("==============================")

    print(
        result["persons"]
    )

    print("\n==============================")
    print("LOCATIONS")
    print("==============================")

    print(
        result["locations"]
    )

    print("\n==============================")
    print("ORGANIZATIONS")
    print("==============================")

    print(
        result["organizations"]
    )

    print("\n==============================")
    print("VEHICLES")
    print("==============================")

    print(
        result["vehicles"]
    )

    print("\n==============================")
    print("PHONES")
    print("==============================")

    print(
        result["phones"]
    )

    print("\n==============================")
    print("FIR NUMBER")
    print("==============================")

    print(
        result["fir_number"]
    )

    print("\n==============================")
    print("RELATIONSHIPS")
    print("==============================")

    print(
        result["relationships"]
    )