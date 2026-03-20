import os
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.get_database("flowmotive")
queue_collection = db.get_collection("email_queue")

def init_db():
    queue_collection.create_index([("status", 1), ("priority", -1), ("_id", 1)])

def add_to_queue(email, data_dict, template, priority):
    doc = {
        "email": email,
        "data_json": json.dumps(data_dict),
        "template": template,
        "status": "pending",
        "priority": priority
    }
    queue_collection.insert_one(doc)

def get_next_pending():
    doc = queue_collection.find_one(
        {"status": "pending"},
        sort=[("priority", -1), ("_id", 1)]
    )
    
    if doc:
        doc["id"] = str(doc["_id"])
        return doc
    return None

def mark_as_sent(row_id):
    queue_collection.update_one(
        {"_id": ObjectId(row_id)},
        {"$set": {"status": "sent"}}
    )
