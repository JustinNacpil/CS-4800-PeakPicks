import os
from pymongo import MongoClient

uri = os.getenv("MONGODB_URI")
if not uri:
    raise RuntimeError("Set MONGODB_URI first.")

client = MongoClient(uri)
db = client[os.getenv("MONGODB_DB", "peakpicks")]

print("Databases:", client.list_database_names())
print("Collections in peakpicks:", db.list_collection_names())
