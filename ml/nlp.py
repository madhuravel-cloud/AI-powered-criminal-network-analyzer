import spacy
import re


nlp = spacy.load("en_core_web_sm")


VEHICLE_WORDS = [
    "car",
    "bike",
    "motorcycle",
    "vehicle",
    "truck",
    "van",
    "bus",
    "scooter"
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
    "spoke_to": "associate",
    "friend": "friend",
    "friends": "friend",
    "relative": "relative",
    "relatives": "relative",
    "brother": "relative",
    "sister": "relative"
}


def extract_entities(text):

    doc = nlp(text)

    persons = []
    locations = []
    organizations = []
    vehicles = []

    for ent in doc.ents:

        if ent.label_ == "PERSON":
            persons.append(ent.text)

        elif ent.label_ in ["GPE", "LOC", "FAC"]:
            locations.append(ent.text)

        elif ent.label_ == "ORG":
            organizations.append(ent.text)

    for token in doc:

        if token.text.lower() in VEHICLE_WORDS:

            start = token.i
            end = token.i + 1

            if start > 0:
                vehicle = doc[start - 1:end].text

                if vehicle.lower() not in VEHICLE_WORDS:
                    vehicles.append(vehicle)

            vehicles.append(token.text)

    phones = re.findall(
        r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b",
        text
    )

    persons = list(set(persons))
    locations = list(set(locations))
    organizations = list(set(organizations))
    vehicles = list(set(vehicles))
    phones = list(set(phones))

    for person in persons:
        locations = [
            location
            for location in locations
            if location.lower() != person.lower()
        ]

    return {
        "persons": sorted(persons),
        "locations": sorted(locations),
        "organizations": sorted(organizations),
        "vehicles": sorted(vehicles),
        "phones": sorted(phones)
    }


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

        if len(sentence_people) < 2:
            continue

        person1 = sentence_people[0][1]
        person2 = sentence_people[1][1]

        relationship = "associate"

        sentence_lower = sentence.text.lower()

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
            relationships.append(relationship_data)

    return relationships


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


if __name__ == "__main__":

    text = """
    Ravi met Arun at Kochi railway station.
    Arun contacted Kumar using 9876543211.
    Kumar was travelling in a white Toyota car.
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

    print("\nRelationships:")
    print(results["relationships"])

