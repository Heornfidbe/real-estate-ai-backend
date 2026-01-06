from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import pickle
import numpy as np
import pandas as pd
from bson import ObjectId 
import json
import firebase_admin
from firebase_admin import credentials, auth as admin_auth
from datetime import datetime

firebase_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT")

if not firebase_json:
    raise RuntimeError("FIREBASE_SERVICE_ACCOUNT env variable not set")
cred = credentials.Certificate(json.loads(firebase_json))
initialize_app(cred)

# cred = credentials.Certificate("mumbai-real-estate-ai-firebase-adminsdk-fbsvc-854a84cdb6.json")
# firebase_admin.initialize_app(cred)


from database import listings_collection

app = Flask(__name__)
CORS(app)

BASE = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ----------------------------------
# Load ML Model
# ----------------------------------
MODEL_PATH = os.path.join(BASE, "model.pkl")
COLUMNS_PATH = os.path.join(BASE, "columns.pkl")

model = pickle.load(open(MODEL_PATH, "rb"))
columns = pickle.load(open(COLUMNS_PATH, "rb"))
print("✅ Model & columns loaded.")


# ----------------------------------
# GET Regions
# ----------------------------------
@app.route("/regions")
def get_regions():
    region_list = [
        col.replace("region_", "")
        for col in columns if col.startswith("region_")
    ]
    return jsonify({"regions": region_list})


# ----------------------------------
# Predict Price
# ----------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    bhk = float(data.get("bhk", 0))
    area = float(data.get("area", 0))
    region = data.get("region", "")

    row = {col: 0 for col in columns}
    row["bhk"] = bhk
    row["area"] = area

    region_col = f"region_{region}"
    if region_col in row:
        row[region_col] = 1

    X = pd.DataFrame([row], columns=columns)
    log_pred = model.predict(X)[0]
    price = np.expm1(log_pred)

    return jsonify({"prediction": round(float(price), 2)})


# ----------------------------------
# Add Property Listing
# ----------------------------------
@app.route("/add-property", methods=["POST"])
def add_property():
    data = request.form
    file = request.files.get("image")

    print("\n--- NEW PROPERTY SUBMISSION ---")
    print("FORM RECEIVED:", dict(data))
    print("FILES RECEIVED:", file.filename if file else "No File")
    print("--------------------------------\n")

    # 🔒 REQUIRED FIELDS CHECK
    required_fields = [
        "user_id", "owner_name", "contact",
        "title", "region", "bhk", "area", "price"
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "success": False,
                "error": f"Missing field: {field}"
            }), 400

    # IMAGE
    filename = None
    if file and file.filename:
        filename = file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))

    # AMENITIES
    try:
        amenities = json.loads(data.get("amenities", "[]"))
    except:
        amenities = []

    new_listing = {
        "user_id": data.get("user_id"),
        "owner_name": data.get("owner_name"),
        "contact": data.get("contact"),
        "title": data.get("title"),
        "region": data.get("region"),
        "subarea": data.get("subarea", ""),
        "bhk": int(data.get("bhk")),
        "area": float(data.get("area")),
        "price": float(data.get("price")),
        "description": data.get("description", ""),
        "property_type": data.get("property_type", ""),
        "furnish": data.get("furnish", ""),
        "construction_status": data.get("construction_status", ""),
        "property_age": data.get("property_age", ""),
        "builder": data.get("builder", ""),
        "amenities": amenities,
        "image": filename
    }

    listings_collection.insert_one(new_listing)

    return jsonify({"success": True})




# ----------------------------------
# Get All Listings
# ----------------------------------
@app.route("/listings")
def listings():
    region = request.args.get("region")
    bhk = request.args.get("bhk")
    sort = request.args.get("sort", "asc")

    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    skip = (page - 1) * limit

    query = {}

    if region:
        query["region"] = {
            "$regex": f"^{region.strip()}$",
            "$options": "i"
        }

    if bhk:
        try:
            query["bhk"] = int(bhk)
        except:
            pass

    sort_order = 1 if sort == "asc" else -1

    cursor = (
        listings_collection
        .find(query)
        .sort("price", sort_order)
        .skip(skip)
        .limit(limit)
    )

    results = []
    for item in cursor:
        item["_id"] = str(item["_id"])
        results.append(item)

    return jsonify(results)


@app.route("/listing/<listing_id>")
def get_listing(listing_id):
    item = listings_collection.find_one({"_id": ObjectId(listing_id)})
    if not item:
        return jsonify({"error": "Listing not found"}), 404

    item["_id"] = str(item["_id"])
    return jsonify(item)


@app.route("/my-listings/<user_id>")
def my_listings(user_id):
    results = []
    for item in listings_collection.find({"user_id": user_id}):
        item["_id"] = str(item["_id"])
        results.append(item)

    return jsonify(results)

@app.route("/delete-listing/<listing_id>", methods=["DELETE"])
def delete_listing(listing_id):
    listings_collection.delete_one({"_id": ObjectId(listing_id)})
    return jsonify({"success": True})


@app.route("/edit-property/<listing_id>", methods=["POST"])
def edit_property(listing_id):
    data = request.form

    update_data = {
        "title": data.get("title"),
        "region": data.get("region"),
        "subarea": data.get("subarea"),
        "bhk": data.get("bhk"),
        "area": data.get("area"),
        "price": data.get("price"),
        "description": data.get("description"),
        "property_type": data.get("property_type"),
        "furnish": data.get("furnish"),
        "construction_status": data.get("construction_status"),
        "property_age": data.get("property_age"),
        "builder": data.get("builder"),
        "amenities": json.loads(data.get("amenities", "[]")),
    }

    listings_collection.update_one(
        {"_id": ObjectId(listing_id)},
        {"$set": update_data}
    )

    return jsonify({"success": True})




# ----------------------------------
# Serve Uploaded Images
# ----------------------------------
@app.route("/uploads/<filename>")
def serve_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ----------------------------------
# AI Chatbot Route (Short Answers)
# ----------------------------------
import openai
import os
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/ai-chat", methods=["POST"])
def ai_chat():
    data = request.get_json()
    question = data.get("question", "")
    prop = data.get("property", {})

    prompt = f"""
You are an AI real estate assistant.
Give VERY SHORT answers (3–7 words ONLY).
Never write long paragraphs.

Property details:
Price: {prop.get("price")} lakhs
BHK: {prop.get("bhk")}
Area: {prop.get("area")} sq ft
Region: {prop.get("region")}
Description: {prop.get("description")}

User question: "{question}"

Respond in maximum 7 words.
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You answer extremely briefly."},
                {"role": "user", "content": prompt}
            ]
        )

        answer = response.choices[0].message.content.strip()
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------------------
# AI Short Forecast (Chatbot Helper)
# ----------------------------------
@app.route("/ai-forecast", methods=["POST"])
def ai_forecast():
    data = request.get_json()
    prop = data.get("property", {})

    try:
        bhk = float(prop.get("bhk", 0))
        area = float(prop.get("area", 0))
        region = prop.get("region", "")

        # Build model input
        row = {col: 0 for col in columns}
        row["bhk"] = bhk
        row["area"] = area

        region_col = f"region_{region}"
        if region_col in row:
            row[region_col] = 1

        X = pd.DataFrame([row], columns=columns)
        base_price = float(np.expm1(model.predict(X)[0]))  # Lakhs

        # Rounded forecasts
        f1 = round(base_price * 1.05)   # 1 year
        f3 = round(base_price * 1.15)   # 3 years
        f5 = round(base_price * 1.28)   # 5 years

        msg = (
            f"Next year: ₹{f1}L · "
            f"In 3 years: ₹{f3}L · "
            f"In 5 years: ₹{f5}L"
        )

        return jsonify({"answer": msg})

    except Exception:
        return jsonify({"answer": "Future price unavailable."})


# ----------------------------------
# AI Investment Score Route
# ----------------------------------
@app.route("/investment-score", methods=["POST"])
def investment_score():
    data = request.get_json()

    try:
        price = float(data.get("price", 0))     # Listed price
        area = float(data.get("area", 0))
        bhk = float(data.get("bhk", 0))
        region = str(data.get("region", "")).strip()

        # ---- ML PRICE PREDICTION ---- #
        row = {col: 0 for col in columns}
        row["bhk"] = bhk
        row["area"] = area

        region_col = f"region_{region}"
        if region_col in columns:
            row[region_col] = 1

        X = pd.DataFrame([row], columns=columns)
        ml_price = float(np.expm1(model.predict(X)[0]))  # Lakhs

        # ---- PRICE DIFFERENCE ---- #
        diff = ml_price - price   # IMPORTANT: keep direction

        # ---- SCORING LOGIC ---- #
        if diff > 50:
            score = 90
            risk = "Low Risk"
            reason = "Property is significantly undervalued."
        elif diff > 20:
            score = 75
            risk = "Moderate Risk"
            reason = "Property priced below market value."
        elif diff > -10:
            score = 60
            risk = "Neutral"
            reason = "Property priced close to market value."
        else:
            score = 35
            risk = "High Risk"
            reason = "Property appears overpriced."

        return jsonify({
            "ml_price": round(ml_price, 2),
            "market_price": round(price, 2),
            "score": score,
            "risk": risk,
            "reason": reason
        })

    except Exception:
        return jsonify({
            "score": 20,
            "risk": "High Risk",
            "reason": "Unable to evaluate investment."
        })
    
@app.route("/admin/users", methods=["GET"])
def get_all_users():
    users = []

    for user in admin_auth.list_users().iterate_all():
        blocked = False
        if user.custom_claims and user.custom_claims.get("blocked"):
            blocked = True

        users.append({
            "uid": user.uid,
            "email": user.email,
            "name": user.display_name,  # 👈 USER NAME
            "blocked": blocked,
            "createdAt": datetime.fromtimestamp(
                user.user_metadata.creation_timestamp / 1000
            ).strftime("%Y-%m-%d")  # 👈 readable date
        })

    return jsonify({
        "count": len(users),
        "users": users
    })

@app.route("/admin/block-user/<uid>", methods=["POST"])
def block_user(uid):
    from firebase_admin import auth

    auth.set_custom_user_claims(uid, {
        "blocked": True
    })

    return jsonify({"success": True})

@app.route("/admin/unblock-user/<uid>", methods=["POST"])
def unblock_user(uid):
    from firebase_admin import auth

    auth.set_custom_user_claims(uid, {
        "blocked": False
    })

    return jsonify({"success": True})

@app.route("/admin/delete-user/<uid>", methods=["DELETE"])
def delete_user(uid):
    from firebase_admin import auth
    auth.delete_user(uid)
    return jsonify({"success": True})





# ----------------------------------
# Run server
# ----------------------------------
if __name__ == "__main__":
    app.run(port=5000, debug=True)
