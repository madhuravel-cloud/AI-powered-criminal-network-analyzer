import spacy
import re

nlp = spacy.load("en_core_web_sm")


# ============================================================
# SYNTHETIC / KNOWN ENTITIES
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
# CLEAN
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
# FIND KNOWN ENTITIES IN OCR TEXT
# ============================================================

def find_known_entities(text):

    """
    Search the OCR text for entities from the controlled
    synthetic dataset.

    Only entities actually present in the OCR text are returned.
    """

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

        # Also allow OCR spaces:
        # 98765 43210

        spaced = (
            phone[:5]
            + r"\s?"
            + phone[5:]
        )

        if re.search(
            spaced,
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
# PERSON VALIDATION
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
}


def is_valid_person(name):

    name = clean_entity(name)

    if not name:
        return False

    if re.search(
        r"\d",
        name
    ):
        return False

    words = name.split()

    if len(words) < 2 or len(words) > 3:
        return False

    for word in words:

        if word.lower() in INVALID_PERSON_WORDS:
            return False

    return True


# ============================================================
# NORMAL NLP PERSON EXTRACTION
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
# NORMAL NLP LOCATION EXTRACTION
# ============================================================

def extract_locations(text):

    locations = set()

    doc = nlp(text)

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
    # Common location phrases
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

        if location:

            locations.add(
                location
            )

    return sorted(locations)


# ============================================================
# NORMAL NLP ORGANIZATION EXTRACTION
# ============================================================

def extract_organizations(text):

    organizations = set()

    doc = nlp(text)

    invalid_orgs = {
        "cctv",
        "fir",
        "ps",
        "police station",
        "time of fir",
        "distance and direction",
        "nationality occupation address",
        "samsung",
    }

    for ent in doc.ents:

        if ent.label_ == "ORG":

            organization = clean_entity(
                ent.text
            )

            if not organization:
                continue

            if (
                organization.lower()
                in invalid_orgs
            ):
                continue

            organizations.add(
                organization
            )

    return sorted(organizations)


# ============================================================
# NORMAL NLP VEHICLE EXTRACTION
# ============================================================

def extract_vehicles(text):

    vehicles = set()

    # Registration number
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

    # Vehicle descriptions
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

    return sorted(vehicles)


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

        if phone.startswith("91") and len(phone) == 12:

            phone = phone[2:]

        if len(phone) == 10:

            cleaned.add(
                phone
            )

    return sorted(cleaned)


# ============================================================
# NORMAL FIR EXTRACTION
# ============================================================

def extract_fir_number(text):

    patterns = [

        r"FIR\s*(?:No\.?|Number)?\s*[:\-]?\s*(\d{1,6}/\d{2,4})",

        r"\b(\d{1,6}/\d{2,4})\b"
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

        if len(sentence_people) < 2:
            continue

        person1 = sentence_people[0][1]

        person2 = sentence_people[1][1]

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
# MAIN ANALYZER
# ============================================================

def analyze_fir_text(text):

    """
    HYBRID EXTRACTION

    Priority:

    1. Check known synthetic entities
    2. If found, use the known entity
    3. For anything not found, use normal NLP
    4. Merge both results
    """

    # ========================================================
    # STEP 1
    # KNOWN ENTITY CHECK
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
    # MERGE
    # ========================================================

    persons = list(
        dict.fromkeys(
            known["persons"]
            + nlp_persons
        )
    )

    locations = list(
        dict.fromkeys(
            known["locations"]
            + nlp_locations
        )
    )

    organizations = list(
        dict.fromkeys(
            known["organizations"]
            + nlp_organizations
        )
    )

    vehicles = list(
        dict.fromkeys(
            known["vehicles"]
            + nlp_vehicles
        )
    )

    phones = list(
        dict.fromkeys(
            known["phones"]
            + nlp_phones
        )
    )

    # ========================================================
    # FIR NUMBER
    # ========================================================

    fir_number = (
        known["fir_number"]
        or nlp_fir
    )

    # ========================================================
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
    # RELATIONSHIPS
    # ========================================================

    relationships = extract_relationships(
        text,
        persons
    )

    # ========================================================
    # RETURN
    # ========================================================

    return {

        "persons":
            sorted(persons),

        "locations":
            sorted(locations),

        "organizations":
            sorted(organizations),

        "vehicles":
            sorted(vehicles),

        "phones":
            sorted(phones),

        "fir_number":
            fir_number,

        "relationships":
            relationships
    }