""" Catalog: Courses Functions """
import os
import json
import bson.json_util
from app import mongo_client

FILE_NAME = "courses.json"
FILE_LOCATION = os.path.join(os.path.dirname(os.path.relpath(__file__)), FILE_NAME)
COLLECTION_NAME = "courses"

DEPARTMENTS = {
    "BIA": "Business Intelligence and Analytics",
    "BIO": "Biology",
    "BME": "Biomedical Engineering",
    "BT": "Business and Technology",
    "CAL": "College of Arts & Letters",
    "CE": "Civil Engineering",
    "CH": "Chemistry and Chemical Biology",
    "CHE": "Chemical Engineering",
    "CM": "Construction Management",
    "COGN": "Practical Seminars",
    "COMM": "Communication",
    "CPE": "Computer Engineering",
    "CS": "Computer Science",
    "D": "Dean's Offices",
    "E": "Interdepartmental Engineering",
    "EE": "Electrical Engineering",
    "EMT": "Economic Management",
    "EM": "Engineering Management",
    "EN": "Environmental Engineering",
    "ES": "Enterprise Systems",
    "FE": "Financial Engineering",
    "FIN": "Finance",
    "H": "Honor Program",
    "HAR": "Humanities/Art",
    "HHS": "Humanities/History",
    "HLI": "Humanities/Literature",
    "HMU": "Humanities/Music",
    "HPL": "Humanities/Philosophy",
    "HSS": "Humanities/Social Sciences",
    "HST": "Humanities/Science and Technology",
    "HTH": "Humanities/Theater",
    "HUM": "Humanities/Miscellaneous",
    "IPD": "Integrated Product Development",
    "LFR": "Language/French",
    "LSP": "Language/Spanish",
    "MA": "Mathematics",
    "ME": "Mechanical Engineering",
    "MGT": "Management",
    "MIS": "Information Systems",
    "MT": "Materials Science and Engineering",
    "NANO": "Nanotechnology",
    "NE": "Naval Engineering",
    "NIS": "Networked Information Systems",
    "OE": "Ocean Engineering",
    "PAE": "Product Architecture and Engineering",
    "PE": "Physical Education",
    "PEP": "Physics & Engineering Physics",
    "PIN": "Pinnacle Scholar",
    "PME": "Pharmaceutical Manufacturing",
    "PRV": "Provost",
    "QF": "Quantitative Finance",
    "REG": "Registrar",
    "SDOE": "Sys Design & Operational Effectiveness",
    "SEF": "Science & Engineering Found. for E",
    "SES": "Systems Engineering Security",
    "SOC": "Service Oriented Computing",
    "SSW": "Software Engineering",
    "SYS": "Systems Engineering",
    "TG": "Technogenesis",
    "TM": "Telecommunications Management"
}


def load_data():
    """ Load Data From JSON File

    :return: List representation of local "courses" data
    :rtype: list
    """
    data = bson.json_util.loads(open(FILE_LOCATION).read())

    # Warn if there are duplicate courses
    h = {}
    for a in data:
        key = (a["letter"], a["number"])
        if key in h:
            print("Duplicate course {0}-{1} in courses.json".format(*key))
        h[key] = 1
    return data


def remove_dup():
    """remove duplicate courses from the file"""
    matched_items = {}
    new_items = []
    doc = bson.json_util.loads(open(FILE_LOCATION).read())
    for entry in sorted(doc, key=lambda x: (x.get("letter"), int(x.get("number")))):
        key = (entry.get("letter"), int(entry.get("number")))
        if key not in matched_items:
            new_items.append(entry)
            matched_items[key] = 1
    with open('courses.sorted.json', 'w') as outfile:
        json.dump(new_items, outfile, sort_keys=True, indent=4, separators=(',', ': '))


def update_db():
    """ Update Database With Current JSON Data """
    db = mongo_client.catalog
    if COLLECTION_NAME not in db.collection_names():
        db[COLLECTION_NAME].insert_many(load_data())
    else:
        db.temp.drop()
        db.temp.insert_many(load_data())
        db.temp.aggregate([{"$out": COLLECTION_NAME}])
        db.temp.drop()


def get_all():
    """

    :return:
    """
    return mongo_client.catalog.courses.find({}, {'_id': False}).sort([("letter", 1), ("number", 1)])


def get_tree():
    """

    :return:
    """
    cursor = mongo_client.catalog.courses.aggregate([{"$sort": {"number": 1}},
                                                     {"$group": {"_id": "$letter",
                                                                 "nodes": {"$push": {
                                                                     "a_attr": {"data-letter": "$letter",
                                                                                "data-number": "$number",
										"data-credits": "$credits"},
                                                                     "text": {"$concat": ["$letter", "-",
                                                                                          "$number", " ",
                                                                                          "$name"]}}}}},
                                                     {"$sort": {"_id": 1}},
                                                     {"$project": {"_id": 0, "text": "$_id", "children": "$nodes"}}])
    for node in cursor:
        node["text"] = "{0}: {1}".format(node["text"], DEPARTMENTS.get(node["text"], ""))
        yield node
