"""  Student Info: User Functions """
import os
import json
import bson.json_util
from app import mongo_client


FILE_NAME = "students.json"
FILE_LOCATION = os.path.join(os.path.dirname(os.path.relpath(__file__)), FILE_NAME)
COLLECTION_NAME = "students"


MAJORS = {
    "BIO": "Biology",
    "BME": "Biomedical Engineering",
    "BT": "Business and Technology",
    "CE": "Civil Engineering",
    "CH": "Chemistry and Chemical Biology",
    "CHE": "Chemical Engineering",
    "CM": "Construction Management",
    "CPE": "Computer Engineering",
    "CS": "Computer Science",
    "EE": "Electrical Engineering",
    "EM": "Engineering Management",
    "EN": "Environmental Engineering",
    "MA": "Mathematics",
    "ME": "Mechanical Engineering",
    "MGT": "Management",
    "NE": "Naval Engineering",
    "PEP": "Physics & Engineering Physics",
    "PIN": "Pinnacle Scholar",
    "SSW": "Software Engineering",
    "SYS": "Systems Engineering",	
    "TM": "Telecommunications Management"
}

REQCOURSES = {
    "SSW" : ["SSW 540", "SSW 555", "SSW 564", "SSW 565", "SSW 567", "SSW 533", "SSW 690","SSW 695"],
    "FE" : ["FE 610", "FE 620", "FE 621", "FE 630", "FE 580", "FE 800"],
    "EM" : ["EM 600", "EM 605", "EM 612", "EM 624", "SYS 660", "SYS 611"],
    "SYS" : ["SYS 671", "SYS 672", "SYS 673", "SYS 674", "SYS 612", "SYS 800"]
}

def load_data():
    """ Load Data From JSON File

    :return: List representation of local "student" data
    :rtype: List
    """
    return bson.json_util.loads(open(FILE_LOCATION).read())



def update_db():
    """ Update Database With Current JSON Data """
    db = mongo_client.students
    new_data = load_data()
    if COLLECTION_NAME not in db.collection_names():
        db[COLLECTION_NAME].insert_many(new_data)
    else:
        db.temp.drop()
        db.temp.insert_many(new_data)
        db.temp.aggregate([{"$out": COLLECTION_NAME}])
        db.temp.drop()

def get_all():
    """

    :return:
    """
    return mongo_client.students.students.find({}, {'_id': False}).sort([("name", 1)])

"""def get_req():

    cursor = mongo_client.students.students.aggregate(["$project": {diff:{$setUnion:[{$setDifference:["$courses", REQCOURSES.get("$major")]}, {$setDifference:[REQCOURSES.get("$major"), "$courses"]}]}
"""   

def get_tree():
    """

    :return:
    """
    cursor = mongo_client.students.students.aggregate([{"$sort": {"major": 1}},
                                                     {"$group": {"_id": "$major",
                                                                 "nodes": {"$push": {
                                                                     "a_attr": {"data-name": "$name",
                                                                                "data-cwid": "$cwid",
                                                                                "data-major": "$major",
                                                                                "data-courses": "$courses"},
                                                                     "text": {"$concat": ["$name", " (", "$cwid", ")"]}}}}},
                                                     {"$sort": {"_id": 1}},
                                                     {"$project": {"_id": 0, "text": "$_id", "children": "$nodes"}}])
    for node in cursor:
        node["text"] = "{0}: {1}".format(node["text"], MAJORS.get(node["text"], ""))
        yield node
