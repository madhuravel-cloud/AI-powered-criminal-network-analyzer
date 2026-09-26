import spacy
import re

nlp = spacy.load("en_core_web_sm")


# ---------------------------------------------------------
# BASIC REGEX PATTERNS
# ---------------------------------------------------------

PHONE_PATTERN = r"(?:\+91[\s-]?)?[6-9]\d{9}"

FIR_PATTERN = r"\b(?:FIR\s*(?:No\.?|Number)?\s*)?(\d{1,6}/\d{2,4})\b"

VEHICLE_PATTERN = r"\b[A-Z]{2}[-\s]?\d{1,2}[-\s]?[A-Z]{1,3}[-\s]?\d{1,4}\b"


# ---------------------------------------------------------
# WORDS THAT SHOULD NEVER BECOME PERSONS
# ---------------------------------------------------------

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
    "age",
    "father",
    "mother",
    "brother",
    "sister",
    "husband",
    "wife",
}


# ---------------------------------------------------------
# LOCATION WORDS
# ---------------------------------------------------------

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
    "state",
    "junction",
    "railway",
    "airport",
    "temple",
    "hospital",
    "school",
    "college",
}


# ---------------------------------------------------------
# VEHICLE WORDS
# ---------------------------------------------------------

VEHICLE_WORDS = {
    "car",
    "bike",
    "motorcycle",
    "vehicle",
    "truck",
    "van",
    "bus",
    "scooter",
    "auto",
    "sedan",
    "suv",
}


# ---------------------------------------------------------
# RELATIONSHIPS
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# CLEAN TEXT
# ---------------------------------------------------------

def clean_entity(value):
    value = value.strip()
    value = re.sub(r"\s+", " ", value)
    value = value.strip(" ,.;:-")

    return value


# ---------------------------------------------------------
# VALID PERSON CHECK
# ---------------------------------------------------------

def is_valid_person(name):

    name = clean_entity(name)

    if not name:
        return False

    lower = name.lower()

    # Reject obvious field labels
    if lower in INVALID_PERSON_WORDS:
        return False

    # Reject long garbage strings
    if len(name.split()) > 4:
        return False

    # Reject strings containing digits
    if re.search(r"\d", name):
        return False

    # Reject obvious location phrases
    if any(word in lower.split() for word in LOCATION_WORDS):
        return False

    # A person's name should normally contain letters
    if not re.search(r"[A-Za-z]", name):
        return False

    return True


# ---------------------------------------------------------
# PERSON EXTRACTION
# ---------------------------------------------------------

def extract_persons(text):

    persons = set()

    # 1. spaCy PERSON entities
    doc = nlp(text)

    for ent in doc.ents:

        if ent.label_ == "PERSON":

            name = clean_entity(ent.text)

            if is_valid_person(name):
                persons.add(name)

    # 2. Common FIR labels
    label_patterns = [
        r"(?:complainant|informant|accused|victim|witness)"
        r"\s*[:\-]?\s*([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,2})",

        r"(?:name of complainant|name of accused|name)"
        r"\s*[:\-]\s*([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,2})",
    ]

    for pattern in label_patterns:

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        for match in matches:

            name = clean_entity(match)

            if is_valid_person(name):
                persons.add(name)

    return sorted(persons)


# ---------------------------------------------------------
# PHONE EXTRACTION
# ---------------------------------------------------------

def extract_phones(text):

    phones = re.findall(
        PHONE_PATTERN,
        text
    )

    cleaned = set()

    for phone in phones:

        phone = re.sub(r"[^\d+]", "", phone)

        # Remove +91 for consistent storage
        if phone.startswith("+91"):
            phone = phone[3:]

        if len(phone) == 10:
            cleaned.add(phone)

    return sorted(cleaned)


# ---------------------------------------------------------
# LOCATION EXTRACTION
# ---------------------------------------------------------

def extract_locations(text):

    locations = set()

    doc = nlp(text)

    # 1. spaCy locations
    for ent in doc.ents:

        if ent.label_ in {"GPE", "LOC", "FAC"}:

            location = clean_entity(ent.text)

            if location:
                locations.add(location)

    # 2. Detect phrases containing common location words
    location_pattern = (
        r"\b[A-Z][A-Za-z]+"
        r"(?:\s+[A-Z][A-Za-z]+){0,4}"
        r"\s+(?:Road|Street|Nagar|Colony|Station|Metro|"
        r"Chowk|Market|Town|City|Village|District|Junction)\b"
    )

    matches = re.findall(
        location_pattern,
        text,
        flags=re.IGNORECASE
    )

    for match in matches:

        location = clean_entity(match)

        if location:
            locations.add(location)

    # Remove obvious person names
    return sorted(locations)


# ---------------------------------------------------------
# ORGANIZATION EXTRACTION
# ---------------------------------------------------------

def extract_organizations(text):

    organizations = set()

    doc = nlp(text)

    for ent in doc.ents:

        if ent.label_ == "ORG":

            org = clean_entity(ent.text)

            if org:
                organizations.add(org)

    return sorted(organizations)


# ---------------------------------------------------------
# VEHICLE EXTRACTION
# ---------------------------------------------------------

def extract_vehicles(text):

    vehicles = set()

    # Registration numbers
    registrations = re.findall(
        VEHICLE_PATTERN,
        text.upper()
    )

    for vehicle in registrations:
        vehicles.add(
            re.sub(r"[\s-]+", "-", vehicle)
        )

    # Vehicle descriptions
    doc = nlp(text)

    for token in doc:

        word = token.text.lower()

        if word in VEHICLE_WORDS:

            # Example:
            # "white Toyota car"
            start = max(0, token.i - 2)

            phrase = doc[start:token.i + 1].text

            if phrase:
                vehicles.add(clean_entity(phrase))

    return sorted(vehicles)


# ---------------------------------------------------------
# FIR NUMBER
# ---------------------------------------------------------

def extract_fir_number(text):

    match = re.search(
        FIR_PATTERN,
        text,
        flags=re.IGNORECASE
    )

    if match:
        return match.group(1)

    return ""


# ---------------------------------------------------------
# ENTITY EXTRACTION
# ---------------------------------------------------------

def extract_entities(text):

    persons = extract_persons(text)

    locations = extract_locations(text)

    organizations = extract_organizations(text)

    vehicles = extract_vehicles(text)

    phones = extract_phones(text)

    fir_number = extract_fir_number(text)

    # -----------------------------------------------------
    # Remove a person accidentally appearing as a location
    # -----------------------------------------------------

    person_lower = {
        p.lower()
        for p in persons
    }

    locations = [
        location
        for location in locations
        if location.lower() not in person_lower
    ]

    return {
        "persons": persons,
        "locations": locations,
        "organizations": organizations,
        "vehicles": vehicles,
        "phones": phones,
        "fir_number": fir_number
    }


# ---------------------------------------------------------
# RELATIONSHIP EXTRACTION
# ---------------------------------------------------------

def extract_relationships(text, persons):

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
                    (match.start(), person)
                )

        sentence_people.sort(
            key=lambda x: x[0]
        )

        # Need at least two people
        if len(sentence_people) < 2:
            continue

        person1 = sentence_people[0][1]
        person2 = sentence_people[1][1]

        sentence_lower = sentence.text.lower()

        relationship = "associate"

        for word, relation in RELATIONSHIP_WORDS.items():

            if re.search(
                r"\b" + re.escape(word) + r"\b",
                sentence_lower
            ):

                relationship = relation
                break

        relationship_data = {
            "person": person1,
            "related_person": person2,
            "relationship": relationship
        }

        if relationship_data not in relationships:
            relationships.append(
                relationship_data
            )

    return relationships


# ---------------------------------------------------------
# MAIN FIR ANALYSIS
# ---------------------------------------------------------

def analyze_fir_text(text):

    entities = extract_entities(text)

    relationships = extract_relationships(
        text,
        entities["persons"]
    )

    return {
        **entities,
        "relationships": relationships
    }


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    text = """
    FIR No. 178/2025

    Complainant: Rahul Sharma.
    Accused: Ravi Kumar.
    Amit Sharma met Ravi Kumar at Connaught Place.
    Ravi Kumar contacted Sahil Verma using 9876543211.
    Sahil Verma was travelling in a white Toyota car.
    The incident occurred near Rajiv Chowk Metro Station, Delhi.
    """

    results = analyze_fir_text(text)

    print("\nPersons:")
    print(results["persons"])

    print("\nLocations:")
    print(results["locations"])

    print("\nOrganizations:")
    print(results["organizations"])

    print("\nVehicles:")
    print(results["vehicles"])

    print("\nPhone Numbers:")
    print(results["phones"])

    print("\nFIR Number:")
    print(results["fir_number"])

    print("\nRelationships:")
    print(results["relationships"])