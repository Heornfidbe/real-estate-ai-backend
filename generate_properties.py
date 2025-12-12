import pandas as pd
import random
import os
import numpy as np
from database import listings_collection
import pickle

# -----------------------------
# LOAD MODEL + COLUMNS
# -----------------------------
model = pickle.load(open("model.pkl", "rb"))
columns = pickle.load(open("columns.pkl", "rb"))

# -----------------------------
# LOAD CSV TO GET REGIONS
# -----------------------------
df = pd.read_csv("mumbai.csv").dropna()
df["region"] = df["region"].astype(str).str.strip()
unique_regions = df["region"].unique().tolist()

# -----------------------------
# OWNER NAMES (100+ UNIQUE)
# -----------------------------
owner_names = [
    "Amit Sharma", "Neha Rao", "Karan Mehta", "Riya Shah", "Pratik Deshmukh",
    "Sneha Kulkarni", "Rahul Patil", "Vishal Sawant", "Pooja Joshi", "Ankita Nair",
    "Deepak Shetty", "Minal Fernandes", "Sagar Kadam", "Komal More", "Rohan Jadhav",
    "Nisha Chavan", "Yash Bhobe", "Meera Kamble", "Aakash Singh", "Priya Desai",
    "Arjun Thakur", "Pallavi Wagle", "Chetan Gokhale", "Harsh Kapadia",
    "Dinesh Shukla", "Ayesha Merchant", "Farhan Contractor", "Zara Kapur",
    "Nikita Bhandari", "Omkar Khot", "Ritika Jain", "Gaurav Bedi", "Isha Sinha",
    "Harshit Purohit", "Devanshi Shah", "Chirag Shah", "Manan Doshi",
    "Sana Sheikh", "Aarav Verma", "Vihaan Mukherjee", "Ishita Roy",
    "Kabir Chatterjee", "Rehan Ali", "Suresh Pawar", "Ajay Tiwari",
    "Lavanya Iyer", "Anushka Krishnan", "Harshita Gopal", "Rohit Suresh",
    "Ritika Kannan", "Jayesh Mistry", "Aditya Menon", "Shreya Mohanty",
    "Param Singh", "Madhav Dixit", "Rupali Salve", "Tejas Patkar",
    "Vipul Khedekar", "Rashmi Javeri", "Soham Bhave", "Kritika Ghosh",
    "Shraddha Talwalkar", "Rohini Vartak", "Deven Makwana", "Pushkar Jog",
    "Ravina Purohit", "Jinal Shah", "Bhavesh Trivedi", "Aashna Contractor",
    "Sumeet Dalvi", "Mahima Kothari", "Shantanu Bhide", "Tanvi Satpute",
    "Vikrant Acharya", "Krisha Zaveri", "Hemant Gawli", "Nauheed Shaikh",
    "Mansi Rawat", "Rajkiran Vyas", "Roshni Mathew", "Sanjay Iyer",
    "Aparna Bhosale", "Rohit Shirodkar", "Simran Kaur", "Mohit Paliwal"
]

# -----------------------------
# VARIED DESCRIPTIONS (30+)
# -----------------------------
descriptions = [
    "A beautiful family-friendly apartment with excellent connectivity.",
    "Situated in a peaceful locality with green surroundings.",
    "Premium interiors and excellent ventilation, perfect for modern living.",
    "Close to schools, malls, and metro stations.",
    "Ideal for investment with high rental demand.",
    "Well-designed flat with spacious rooms and natural lighting.",
    "Prime location with excellent resale potential.",
    "Modern architecture with luxury amenities.",
    "Located in a highly safe and well-connected neighborhood.",
    "Affordable yet premium living with great accessibility.",
    "A rare property offering premium comfort at a great price.",
    "Designed for luxury living with elegant interiors.",
    "Well-maintained building with 24/7 security.",
    "Located in a fast-growing area with high appreciation.",
    "Perfect for families looking for convenience and comfort.",
    "Surrounded by greenery with peaceful surroundings.",
    "Premium floor-level apartment with scenic views.",
    "Loaded with modern amenities for a luxury lifestyle.",
    "A great choice for both living and investment.",
    "Spacious floor plan with modern fittings.",
    "Close to business hubs and entertainment zones.",
    "Located in a prestigious locality with excellent facilities.",
    "Recently renovated with premium-quality materials.",
    "Vastu-compliant layout ensuring good energy flow.",
    "High-demand locality with rising prices.",
    "Excellent cross-ventilation and natural light.",
    "Modern gated society with top-notch security.",
    "A perfect blend of luxury and comfort.",
    "Open view property with zero traffic noise."
]

# -----------------------------
# TITLES (30+)
# -----------------------------
titles = [
    "Luxury Apartment", "Modern Family Home", "Premium High-Rise Flat",
    "Spacious Apartment", "Elegant Residential Suite", "Urban Lifestyle Home",
    "Exclusive Property Offer", "Affordable Comfort Apartment",
    "Designer Home in Prime Area", "High-End Apartment with View",
    "Luxury Tower Residence", "Stylish Living Space", "Elite Apartment",
    "Smart City Home", "Premium Locality Residence", "Vastu-Perfect Home",
    "Investor-Friendly Property", "Luxury Corner Apartment",
    "Central City Residence", "Exclusive Penthouse-Style Flat"
]

# -----------------------------
# OTHER FEATURES
# -----------------------------
property_types = ["Apartment", "Villa", "Studio", "Penthouse", "Row House", "Duplex"]
furnish_levels = ["Unfurnished", "Semi-Furnished", "Fully Furnished"]
construction_status = ["Ready to Move", "Under Construction", "New Launch"]
amenities_list = [
    "Lift", "Parking", "Security", "Gym", "Swimming Pool",
    "CCTV", "Garden", "Club House", "Kids Play Area", "Power Backup"
]
property_age_choices = ["0-2 years", "2-5 years", "5-10 years", "10+ years"]
builders = [
    "Lodha Group", "Oberoi Realty", "Runwal Group", "Hiranandani Developers",
    "Godrej Properties", "Kalpataru", "Shapoorji Pallonji", "Rustomjee"
]

sub_regions = {
    "Andheri": ["Lokhandwala", "Versova", "DN Nagar"],
    "Bandra": ["Pali Hill", "Linking Road", "BKC"],
    "Colaba": ["Cuffe Parade", "Navy Nagar", "Cusrow Baug"],
    "Dadar": ["Shivaji Park", "Hindu Colony", "Matunga"],
    "Thane": ["Vartak Nagar", "Ghodbunder Road", "Majiwada"],
}

default_subareas = ["Central Market", "West End", "Sector 4", "Main Road"]

AREA_RANGE = {
    1: (350, 550), 2: (550, 900), 3: (900, 1300), 4: (1300, 1700),
    5: (1700, 2200), 6: (2200, 2700), 7: (2700, 3300), 8: (3300, 4000),
}

# -----------------------------------
# MAIN LOOP — 10 PROPERTIES PER BHK PER REGION
# -----------------------------------
count = 0

for region in unique_regions:
    cleaned_region = region.strip()

    for bhk in range(1, 9):
        for _ in range(10):

            # AREA
            min_a, max_a = AREA_RANGE[bhk]
            area = random.randint(min_a, max_a)

            # ML price
            row = {col: 0 for col in columns}
            row["bhk"] = bhk
            row["area"] = area
            if f"region_{cleaned_region}" in columns:
                row[f"region_{cleaned_region}"] = 1

            X = pd.DataFrame([row], columns=columns)
            base_price = float(np.expm1(model.predict(X)[0]))
            final_price = float(round(base_price * random.uniform(0.9, 1.25), 2))

            subarea = random.choice(sub_regions.get(cleaned_region, default_subareas))
            amenities = random.sample(amenities_list, random.randint(3, 7))

            listing = {
                "title": f"{random.choice(titles)} in {cleaned_region}",
                "owner_name": random.choice(owner_names),
                "contact": f"9{random.randint(100000000,999999999)}",
                "region": cleaned_region,
                "subarea": subarea,
                "bhk": bhk,
                "area": area,
                "price": final_price,
                "description": random.choice(descriptions),
                "furnish": random.choice(furnish_levels),
                "construction_status": random.choice(construction_status),
                "property_age": random.choice(property_age_choices),
                "builder": random.choice(builders),
                "amenities": amenities,
                "property_type": random.choice(property_types),
                "image": None
            }

            listings_collection.insert_one(listing)
            count += 1

print(f"\n✔ SUCCESS: Inserted {count} enhanced properties with unique names & descriptions (NO IMAGES)\n")
