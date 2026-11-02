"""One-time CSV -> MongoDB import using PyMongo."""
from pathlib import Path
import pandas as pd
from pymongo import ASCENDING
from database import get_database

db = get_database()
if db is None:
    raise SystemExit("MongoDB connection failed. Check MONGODB_URI in your .env file.")
collection = db["training_data"]
if collection.count_documents({}) > 0:
    print(f"training_data already contains {collection.count_documents({})} documents; skipping import.")
else:
    csv_path = Path(__file__).resolve().parent / "dataset.csv"
    records = pd.read_csv(csv_path).to_dict(orient="records")
    if records:
        collection.insert_many(records)
    print(f"Imported {len(records)} dataset rows into MongoDB collection training_data.")
db["demand_records"].create_index([("created_at", ASCENDING)])
db["demand_records"].create_index([("item", ASCENDING), ("meal", ASCENDING)])
print("Created indexes for demand_records.")
