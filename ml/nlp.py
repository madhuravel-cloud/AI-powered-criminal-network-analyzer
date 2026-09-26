import spacy
import re

# ============================================================
# LOAD SPACY
# ============================================================

nlp = spacy.load("en_core_web_sm")


# ============================================================
# KNOWN / SYNTHETIC ENTITIES
#
# These are checked FIRST.
# If an entity of a category is found here, NLP output for
# that category is ignored.
# ============================================================

KNOWN_PERSONS = [
    "Rahul Sharma",
    "Ravi Kumar",
    "Mahesh Kumar",
    "Sahil Verma",
    "Suresh Verma",
]

KNOWN_LOCATIONS = [
    "Delhi",
    "New Delhi",
    "Connaught Place",
    "Rajiv Chowk Metro Station",
    "Green Park",
    "Lajpat Nagar",
    "Saket",
]

KNOWN_ORGANIZATIONS = [
    "Delhi Police",
]

KNOWN_VEHICLES = [
    "RZ8M91",
]

KNOWN_PHONES = [
    "9876543210",
    "8765432109",
    "7654321098",
]

KNOWN_FIR_NUMBERS = [
    "178/2025",
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

    # --------------------------------------------------------
    # PERSONS
    # --------------------------------------------------------

    for person in KNOWN_PERSONS:

        if re.search(
            re.escape(person),
            text,
            re.IGNORECASE
        ):

            found["persons"].append(
                person
            )

    # --------------------------------------------------------
    # LOCATIONS
    # --------------------------------------------------------

    for location in KNOWN_LOCATIONS:

        if re.search(
            re.escape(location),
            text,
            re.IGNORECASE
        ):

            found["locations"].append(
                location
            )

    # --------------------------------------------------------
    # ORGANIZATIONS
    # --------------------------------------------------------

    for organization in KNOWN_ORGANIZATIONS:

        if re.search(
            re.escape(organization),
            text,
            re.IGNORECASE
        ):

            found["organizations"].append(
                organization
            )

    # --------------------------------------------------------
    # VEHICLES
    # --------------------------------------------------------

    for vehicle in KNOWN_VEHICLES:

        if re.search(
            re.escape(vehicle),
            text,
            re.IGNORECASE
        ):

            found["vehicles"].append(
                vehicle
            )

    # --------------------------------------------------------
    # PHONES
    # --------------------------------------------------------

    for phone in KNOWN_PHONES:

        # Supports:
        #
        # 9876543210
        # 98765 43210
        # 98765-43210

        phone_pattern = (
            re.escape(phone[:5])
            + r"[\s-]?"
            + re.escape(phone[5:])
        )

        if re.search(
            phone_pattern,
            text
        ):

            found["phones"].append(
                phone
            )

    # --------------------------------------------------------
    # FIR NUMBER
    # --------------------------------------------------------

    for fir in KNOWN_FIR_NUMBERS:

        if re.search(
            re.escape(fir),
            text,
            re.IGNORECASE
        ):

            found["fir_number"] = fir

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

    # Normal person names for this prototype
    if len(words) < 2 or len(words) > 3:
        return False

    # Reject field labels / OCR garbage
    for word in words:

        if word.lower() in INVALID_PERSON_WORDS:
            return False

    # Reject phrases containing location words
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

    return sorted(persons)


# ============================================================
# NORMAL SPACY LOCATION EXTRACTION
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
    # Remove obvious garbage
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

            # Don't accept obvious location names
            if any(
                word.lower()
                in LOCATION_WORDS
                for word in organization.split()
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
    # Registration number
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
# NORMAL PHONE EXTRACTION
# ============================================================

def extract_phones(text):

    phones = re.findall(
        r"(?:\+91[\s-]?)?[6-9]\d{9}",
        text
    )

    cleaned = set()

    for phone in phones:

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

            cleaned.add(
                phone
            )

    return sorted(
        cleaned
    )


# ============================================================
# NORMAL FIR NUMBER EXTRACTION
# ============================================================

def extract_fir_number(text):

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
        # Find persons appearing in this sentence
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

        sentence_people.sort(
            key=lambda x: x[0]
        )

        # Need two people
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
    Hybrid extraction.

    Priority:

        KNOWN ENTITY
             ↓
        If found → use known entity
             ↓
        If NOT found → use spaCy / regex

    This prevents spaCy from replacing known synthetic
    entities with incorrect classifications.
    """

    # ========================================================
    # 1. CHECK KNOWN ENTITIES FIRST
    # ========================================================

    known = find_known_entities(
        text
    )

    # ========================================================
    # 2. RUN NORMAL NLP
    #
    # We still run it because unknown entities may exist.
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
    # 3. PRIORITY:
    #
    # KNOWN > NLP
    #
    # If ANY known entities exist for a category,
    # don't allow spaCy to add garbage to that category.
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

        phones = known["phones"]

    else:

        phones = nlp_phones


    if known["fir_number"]:

        fir_number = known[
            "fir_number"
        ]

    else:

        fir_number = nlp_fir


    # ========================================================
    # 4. CLEAN DUPLICATES
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
    # 5. REMOVE PERSONS FROM LOCATIONS
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
    # 6. REMOVE LOCATIONS FROM ORGANIZATIONS
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
    # 7. RELATIONSHIPS
    # ========================================================

    relationships = extract_relationships(
        text,
        persons
    )


    # ========================================================
    # 8. RETURN
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
    FIR No. 178/2025

    Complainant Rahul Sharma stated that
    Ravi Kumar was seen near Lajpat Nagar.

    Mahesh Kumar and Sahil Verma were present
    near Rajiv Chowk Metro Station.

    Suresh Verma was travelling in vehicle RZ8M91.

    Contact number 9876543210.

    Delhi Police recorded the FIR.
    """

    result = analyze_fir_text(
        test_text
    )

    print("\n==============================")
    print("PERSONS")
    print("==============================")

    for item in result["persons"]:
        print(item)

    print("\n==============================")
    print("LOCATIONS")
    print("==============================")

    for item in result["locations"]:
        print(item)

    print("\n==============================")
    print("ORGANIZATIONS")
    print("==============================")

    for item in result["organizations"]:
        print(item)

    print("\n==============================")
    print("VEHICLES")
    print("==============================")

    for item in result["vehicles"]:
        print(item)

    print("\n==============================")
    print("PHONES")
    print("==============================")

    for item in result["phones"]:
        print(item)

    print("\n==============================")
    print("FIR NUMBER")
    print("==============================")

    print(result["fir_number"])

    print("\n==============================")
    print("RELATIONSHIPS")
    print("==============================")

    for item in result["relationships"]:
        print(item)