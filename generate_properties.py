import random
from database import listings_collection

# -----------------------------
# ALL REGIONS (FROM YOUR DATA)
# -----------------------------
REGIONS = [
    "Adaigaon","Agripada","Airoli","Ambarnath","Ambernath East","Ambernath West",
    "Ambivali","Andheri East","Andheri West","Antop Hill","Asangaon",
    "Badlapur","Badlapur East","Badlapur West","Bandra","Bandra East",
    "Bandra West","Belapur","Bhandup East","Bhandup West","Bhayandar East",
    "Bhayandar West","Bhiwandi","Boisar","Borivali East","Borivali West",
    "Byculla","Chembur","Churchgate","Colaba","Dadar East","Dadar West",
    "Dahisar East","Dahisar West","Diva","Dombivli East","Dombivli West",
    "Ghansoli","Ghatkopar East","Ghatkopar West","Goregaon East",
    "Goregaon West","Jogeshwari East","Jogeshwari West","Juhu",
    "Kalamboli","Kalwa","Kalyan East","Kalyan West","Kamothe",
    "Kandivali East","Kandivali West","Khar","Kharghar","Kurla",
    "Lower Parel","Mahim","Malad East","Malad West","Marine Lines",
    "Matunga","Mazgaon","Mira Road","Mulund East","Mulund West",
    "Mumbai Central","Mumbra","Nalasopara East","Nalasopara West",
    "Nerul","Palava","Palghar","Panvel","Parel","Powai","Prabhadevi",
    "Sanpada","Santacruz East","Santacruz West","Seawoods","Sion",
    "Thane East","Thane West","Ulwe","Vashi","Versova","Vikhroli",
    "Vile Parle East","Vile Parle West","Virar East","Virar West",
    "Wadala","Worli"
]

# -----------------------------
# PRICE PER SQ.FT BY ZONE
# -----------------------------
def base_rate(region):
    if region in ["Colaba","Malabar Hill","Worli","Bandra West","Prabhadevi"]:
        return random.randint(22000, 28000)
    if region in ["Andheri West","Juhu","Lower Parel","Powai"]:
        return random.randint(17000, 22000)
    if region in ["Borivali West","Malad West","Goregaon West","Kandivali West"]:
        return random.randint(14000, 18000)
    if region in ["Thane West","Nerul","Vashi","Kharghar","Sanpada"]:
        return random.randint(11000, 15000)
    return random.randint(6000, 10000)

# -----------------------------
# AREA RANGE PER BHK
# -----------------------------
AREA = {
    1: (400, 550),
    2: (600, 850),
    3: (900, 1200),
    4: (1300, 1800),
    5: (1800, 2400),
    6: (2400, 3000),
    7: (3000, 3600),
    8: (3600, 4500)
}

# -----------------------------
# MIN PRICE FLOOR (LAKHS)
# -----------------------------
MIN_PRICE = {
    1: 20, 2: 40, 3: 65, 4: 95,
    5: 125, 6: 160, 7: 200, 8: 240
}

OWNERS = [
    "Amit Sharma","Rohit Patil","Neha Shah","Deepak Shetty",
    "Karan Mehta","Pooja Desai","Suresh Pawar","Vikram Singh"
]

TITLES = [
    "Spacious Apartment in","Premium Residence in",
    "Modern Family Home in","Luxury Apartment in",
    "Elegant City Home in"
]

AMENITIES = [
    "Lift","Parking","Security","Gym",
    "Power Backup","Swimming Pool","Garden"
]

# -----------------------------
# INSERT
# -----------------------------
# listings_collection.delete_many({})

count = 0

for region in REGIONS:
    rate = base_rate(region)

    for bhk in range(1, 9):
        for _ in range(10):
            area = random.randint(*AREA[bhk])

            price = (area * rate) / 100000
            price *= random.uniform(0.95, 1.15)
            price = round(max(price, MIN_PRICE[bhk]), 2)

            listing = {
                "title": f"{random.choice(TITLES)} {region}",
                "owner_name": random.choice(OWNERS),
                "contact": f"9{random.randint(100000000,999999999)}",
                "region": region,
                "subarea": region,
                "bhk": bhk,
                "area": area,
                "price": price,
                "description": "Well-planned residential property in a prime locality.",
                "property_type": "Apartment",
                "furnish": random.choice(["Unfurnished","Semi-Furnished","Fully Furnished"]),
                "construction_status": random.choice(["Ready to Move","Under Construction"]),
                "property_age": random.choice(["0-2 years","2-5 years","5-10 years"]),
                "builder": random.choice(["Lodha","Godrej","Runwal","Kalpataru"]),
                "amenities": random.sample(AMENITIES, 4),
                "image": None
            }

            listings_collection.insert_one(listing)
            count += 1

print(f"\n✅ INSERTED {count} REALISTIC LISTINGS SUCCESSFULLY\n")
