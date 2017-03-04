"""  User Info: User Functions """
import os
import bson.json_util
from app import mongo_client
from werkzeug.security import generate_password_hash


FILE_NAME = "users.json"
FILE_LOCATION = os.path.join(os.path.dirname(os.path.relpath(__file__)), FILE_NAME)
COLLECTION_NAME = "users"


def load_data():
    """ Load Data From JSON File

    :return: List representation of local "users" data
    :rtype: List
    """
    data = bson.json_util.loads(open(FILE_LOCATION).read())
	
    """ Encrypt Passwords """
    #for a in data:
    #   a["password"] = generate_password_hash(a["password"], method='pbkdf2:sha256')
    return data


def update_db():
    """ Update Database With Current JSON Data """
    db = mongo_client.catalog
    new_data = load_data()
    if COLLECTION_NAME not in db.collection_names():
        db[COLLECTION_NAME].insert_many(new_data)
    else:
        db.temp.drop()
        db.temp.insert_many(new_data)
        db.temp.aggregate([{"$out": COLLECTION_NAME}])
        db.temp.drop()
