"""  Course Popularity: User Functions """
import os
import json
import bson.json_util
from app import mongo_client


FILE_NAME = "popularity.json"
FILE_LOCATION = os.path.join(os.path.dirname(os.path.relpath(__file__)), FILE_NAME)
COLLECTION_NAME = "popularity"


def load_data():
    """ Load Data From JSON File

    :return: List representation of local "popularity" data
    :rtype: List
    """
    return bson.json_util.loads(open(FILE_LOCATION).read())



def update_db():
    """ Update Database With Current JSON Data """
    db = mongo_client.popularity
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
    return mongo_client.popularity.popularity.find({}, {'_id': False}).sort([("course", 1)])
