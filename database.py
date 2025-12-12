from pymongo import MongoClient

MONGO_URI = "mongodb+srv://partht349_db_user:parth0057@cluster0.xsstakm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(MONGO_URI)

db = client["realestate_db"]      # Database name
listings_collection = db["listings"]   # Collection for properties

