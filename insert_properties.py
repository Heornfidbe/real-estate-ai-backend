import random
import pandas as pd
from pymongo import MongoClient

# ---------------- CONFIG ---------------- #

MONGO_URI = "mongodb+srv://partht349_db_user:parth0057@cluster0.xsstakm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "realestate_db"
COLLECTION = "listings"

CSV_PATH = "mumbai.csv"   # keep this file in same folder
TOTAL_LISTINGS = 10000    # how many you want

# ---------------- DATA POOLS ---------------- #

OWNER_NAMES = [
    "Amit Sharma", "Rohit Verma", "Suresh Iyer", "Nikhil Patil",
    "Ankit Jain", "Rahul Mehta", "Kunal Shah", "Vikas Singh",
    "Sanjay Gupta", "Deepak Malhotra", "Harsh Kapoor",
    "Manish Agarwal", "Arjun Rao", "Akash Kulkarni",
    "Pratik Deshmukh", "Naveen Joshi", "Vivek Mishra"
]

DESCRIPTIONS = [
    "Spacious flat with excellent ventilation",
    "Prime location with easy metro access",
    "Ideal for families, peaceful locality",
    "Well maintained society with amenities",
    "Close to schools, malls and hospitals",
    "Modern interiors with premium fittings",
    "Great investment opportunity",
    "Ready to move property",
    "Sea breeze and open view",
    "Low density residential area"
]

PROPERTY_TYPES = [
    "Apartment", "Villa", "Studio",
    "Penthouse", "Row House", "Duplex"
]

FURNISHING = [
    "Unfurnished", "Semi-Furnished", "Fully Furnished"
]

# ---------------- LOAD CSV ---------------- #

df = pd.read_csv(CSV_PATH)

# Expecting at least a "region" column
regions = df["region"].dropna().unique().tolist()

# ---------------- DB CONNECT ---------------- #

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION]

# ---------------- GENERATE LISTINGS ---------------- #

listings = []

for _ in range(TOTAL_LISTINGS):
    bhk = random.randint(1, 8)
    area = random.randint(350, 2500)

    # 🔑 PRICE IN LAKHS ONLY
    price = round((area * random.uniform(0.008, 0.02)), 2)
    price = max(15, min(price, 250))  # clamp between 15L and 2.5Cr (but still Lakhs)

    listing = {
        "user_id": "seeded_admin",
        "owner_name": random.choice(OWNER_NAMES),
        "contact": f"9{random.randint(100000000, 999999999)}",
        "title": f"{bhk} BHK {random.choice(PROPERTY_TYPES)}",
        "region": random.choice(regions),
        "subarea": "Mumbai",
        "bhk": bhk,
        "area": area,
        "price": price,  # ✅ ALWAYS LAKHS
        "description": random.choice(DESCRIPTIONS),
        "property_type": random.choice(PROPERTY_TYPES),
        "furnish": random.choice(FURNISHING),
        "amenities": ["Parking", "Lift", "Security"],
        "image": None
    }

    listings.append(listing)

# ---------------- INSERT ---------------- #

collection.insert_many(listings)

print(f"✅ Successfully inserted {len(listings)} listings (prices in Lakhs only)")
