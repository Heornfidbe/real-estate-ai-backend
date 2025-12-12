import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

# -----------------------------
# LOAD CSV
# -----------------------------
df = pd.read_csv("mumbai.csv")
df = df.dropna()

# -----------------------------
# FIX PRICE to Lakhs
# -----------------------------
if "price_lakhs" in df:
    df["price_lakhs"] = df["price_lakhs"].astype(float)

elif "price" in df.columns:
    df["price"] = df["price"].astype(float)

    def to_lakhs(row):
        unit = str(row.get("price_unit", "")).lower()
        if unit.startswith("cr"):
            return row["price"] * 100
        return row["price"]

    df["price_lakhs"] = df.apply(to_lakhs, axis=1)

else:
    raise Exception("CSV must contain price or price_lakhs")

# -----------------------------
# CLEAN DATA
# -----------------------------
df["region"] = df["region"].astype(str).str.strip()

df = df[["bhk", "area", "region", "price_lakhs"]].dropna()
df = df[df["area"] > 50]        # remove bad values
df = df[df["price_lakhs"] > 5]  # remove bad entries

# -----------------------------
# ENCODING
# -----------------------------
X = df[["bhk", "area", "region"]]
y = df["price_lakhs"]

# One-hot encode region
X = pd.get_dummies(X, columns=["region"], prefix="region")

columns = X.columns.tolist()

# Log-transform for smoother prediction
y_log = np.log1p(y)

# -----------------------------
# TRAIN SPLIT
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y_log, test_size=0.15, random_state=42
)

# -----------------------------
# BEST MODEL: XGBoost
# -----------------------------
model = XGBRegressor(
    n_estimators=700,
    learning_rate=0.05,
    max_depth=8,
    subsample=0.9,
    colsample_bytree=0.8,
    reg_lambda=1.2,
    random_state=42,
)

model.fit(X_train, y_train)

# -----------------------------
# SAVE MODEL + COLUMNS
# -----------------------------
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("columns.pkl", "wb") as f:
    pickle.dump(columns, f)

print("\n🎉 NEW MODEL TRAINED SUCCESSFULLY!")
print("Total rows used:", len(df))
print("Feature columns:", columns)
