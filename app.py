from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import pickle
import numpy as np
import pandas as pd
from bson import ObjectId
import json

# MongoDB
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

    # ✅ DEBUG PRINTS (Will show in terminal)
    print("\n--- NEW PROPERTY SUBMISSION ---")
    print("FORM RECEIVED:", dict(data))
    print("FILES RECEIVED:", file.filename if file else "No File")
    print("--------------------------------\n")

    # USER ID from Google login
    user_id = data.get("user_id")

    # IMAGE HANDLING (optional)
    filename = None
    if file and file.filename:
        filename = file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))

    # AMENITIES HANDLING
    try:
        amenities = json.loads(data.get("amenities", "[]"))
    except:
        amenities = []

    new_listing = {
        "user_id": user_id,
        "owner_name": data.get("owner_name"),
        "contact": data.get("contact"),
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
    results = []
    for item in listings_collection.find():
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
        price = float(data.get("price", 0))
        area = float(data.get("area", 0))
        bhk = float(data.get("bhk", 0))
        region = str(data.get("region", "")).strip()

        # ---- ML PRICE PREDICTION ---- #
        # Build vector like /predict
        row = {col: 0 for col in columns}
        row["bhk"] = bhk
        row["area"] = area

        region_col = f"region_{region}"
        if region_col in columns:
            row[region_col] = 1

        X = pd.DataFrame([row], columns=columns)
        log_pred = model.predict(X)[0]
        ml_price = float(np.expm1(log_pred))  # Lakhs

        # ---- MARKET PRICE FROM USER LISTING ---- #
        market_price = price  # already in lakhs

        # ---- SCORE CALCULATION ---- #
        diff = abs(market_price - ml_price)

        if diff < 10:
            score = 90
            risk = "Low Risk"
            reason = "Price matches market trends."
        elif diff < 25:
            score = 70
            risk = "Moderate Risk"
            reason = "Price slightly different than expected."
        else:
            score = 40
            risk = "High Risk"
            reason = "Price far from expected valuation."

        return jsonify({
            "ml_price": round(ml_price, 2),
            "market_price": round(market_price, 2),
            "final_price": round((ml_price + market_price) / 2, 2),
            "score": score,
            "risk": risk,
            "reason": reason
        })

    except Exception as e:
        return jsonify({
            "ml_price": 0,
            "market_price": price,
            "final_price": price,
            "score": 20,
            "risk": "High Risk",
            "reason": "Uncertain future value"
        })


# ----------------------------------
# Run server
# ----------------------------------
if __name__ == "__main__":
    app.run(port=5000, debug=True)
