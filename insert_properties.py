import pandas as pd
import random
import requests
import os
from bson import ObjectId
from database import listings_collection   # your MongoDB connection

# -----------------------------
# LOAD CSV
# -----------------------------
df = pd.read_csv("mumbai.csv")  # <-- CHANGE THIS TO YOUR FILE NAME
df = df.dropna()

# -----------------------------
# FIX PRICE → Convert to Lakhs
# -----------------------------
if "price_lakhs" in df.columns:
    df["price_lakhs"] = df["price_lakhs"].astype(float)

elif "price" in df.columns:
    df["price"] = df["price"].astype(float)

    if "price_unit" in df.columns:
        def convert_to_lakhs(row):
            price = row["price"]
            unit = str(row["price_unit"]).lower()

            if unit.startswith("cr"):   # crore → lakhs
                return price * 100
            else:  # assume already lakhs
                return price

        df["price_lakhs"] = df.apply(convert_to_lakhs, axis=1)
    else:
        df["price_lakhs"] = df["price"]  # assume price is already in lakhs

else:
    raise Exception("CSV must contain price or price_lakhs column.")


# -----------------------------
# RANDOM DATA GENERATORS
# -----------------------------
owner_names = [
    "Rohan Mehta", "Anjali Sharma", "Vikram Kapoor", "Nisha Patel",
    "Arjun Singh", "Priya Desai", "Karan Thakur", "Meera Joshi"
]

descriptions = [
    "A beautiful property with excellent connectivity and premium amenities.",
    "Spacious rooms, modern design, and located in a peaceful neighbourhood.",
    "Prime location with great investment potential.",
    "Well-maintained flat with ample sunlight and ventilation.",
    "Luxury apartment with top-class facilities.",
    "Affordable home in a fast-growing locality."
]

titles = [
    "Luxury Apartment for Sale",
    "Spacious Family Home",
    "Modern Flat in Prime Area",
    "Affordable Housing Opportunity",
    "Premium Residential Property",
    "Exclusive Listing — Must See!"
]


# -----------------------------
# IMAGE DOWNLOAD DIRECTORY
# -----------------------------
IMAGE_DIR = "uploads"
os.makedirs(IMAGE_DIR, exist_ok=True)

UNSPLASH_QUERY = "luxury apartment interior"
UNSPLASH_URL = f"https://source.unsplash.com/random/900x600/?{UNSPLASH_QUERY}"


# -----------------------------
# INSERTING INTO MONGODB
# -----------------------------
count = 0

for _, row in df.iterrows():

    # Download random HQ image
    try:
        img_data = requests.get(UNSPLASH_URL).content
        img_filename = f"prop_{random.randint(100000, 999999)}.jpg"
        img_path = os.path.join(IMAGE_DIR, img_filename)

        with open(img_path, "wb") as f:
            f.write(img_data)
    except:
        img_filename = None

    # Build property object
    listing = {
        "owner_name": random.choice(owner_names),
        "contact": f"9{random.randint(100000000, 999999999)}",
        "title": random.choice(titles),
        "region": str(row["region"]),
        "bhk": int(row["bhk"]),
        "area": float(row["area"]),
        "price": float(row["price_lakhs"]),
        "description": random.choice(descriptions),
        "image": img_filename
    }

    listings_collection.insert_one(listing)
    count += 1


print(f"✅ SUCCESS: Inserted {count} properties into MongoDB!")
print("📸 Images saved inside /uploads/")
