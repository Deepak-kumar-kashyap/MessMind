"""MessMind REST API: food-demand regression + PyMongo CRUD and analytics."""
from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pymongo import DESCENDING
from pymongo.errors import PyMongoError
from bson import ObjectId

from database import get_database, database_status, clean_mongo_doc
from model import predict_demand, get_metrics

app = FastAPI(
    title="MessMind API",
    description="Campus canteen demand forecasting with regression and MongoDB/PyMongo.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=False,
    allow_methods=["*"], allow_headers=["*"],
)

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MEALS = ["Breakfast", "Lunch", "Snacks", "Dinner"]
ITEMS = ["Rice", "Biryani", "Dosa", "Chapati", "Samosa", "Puff", "Sandwich", "Noodles", "Idli"]
WEATHER = ["Sunny", "Rainy", "Cloudy", "Cold"]
EVENTS = ["No", "Festival", "Holiday", "Exam", "Sports Meet"]

class PredictionInput(BaseModel):
    day: str
    meal: str
    item: str
    weather: str
    event: str
    prepared_quantity: int = Field(default=0, ge=0, le=100000)

class RecordInput(BaseModel):
    day: str
    meal: str
    item: str
    weather: str = "Sunny"
    event: str = "No"
    actual_sold: int = Field(ge=0, le=100000)
    prepared_quantity: int = Field(ge=0, le=100000)
    note: str = ""

class RecordUpdate(BaseModel):
    actual_sold: Optional[int] = Field(default=None, ge=0, le=100000)
    prepared_quantity: Optional[int] = Field(default=None, ge=0, le=100000)
    note: Optional[str] = None

def validate_categories(day, meal, item, weather, event):
    allowed = {"day": DAYS, "meal": MEALS, "item": ITEMS, "weather": WEATHER, "event": EVENTS}
    values = {"day": day, "meal": meal, "item": item, "weather": weather, "event": event}
    for key, value in values.items():
        if value not in allowed[key]:
            raise HTTPException(status_code=422, detail=f"Invalid {key}: {value}")

def collection():
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=503,
            detail="MongoDB is not connected. Set MONGODB_URI in backend/.env and start MongoDB.",
        )
    return db["demand_records"]

def enrich_record(record):
    record["estimated_waste"] = max(0, int(record.get("prepared_quantity", 0)) - int(record.get("actual_sold", record.get("predicted_demand", 0))))
    return record

@app.get("/")
def home():
    return {"project": "MessMind", "message": "Campus Canteen Demand & Food Waste Predictor", "docs": "/docs"}

@app.get("/api/health")
def health():
    return {"api": "ok", "mongodb": database_status()}

@app.get("/api/metrics")
def metrics():
    return get_metrics()

@app.post("/api/predict")
def predict(data: PredictionInput):
    validate_categories(data.day, data.meal, data.item, data.weather, data.event)
    demand = predict_demand(data.day, data.meal, data.item, data.weather, data.event)
    prepared = data.prepared_quantity
    record = {
        "record_type": "prediction",
        "day": data.day, "meal": data.meal, "item": data.item,
        "weather": data.weather, "event": data.event,
        "predicted_demand": demand,
        "prepared_quantity": prepared,
        "estimated_surplus": max(0, prepared - demand) if prepared else None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    saved = False
    try:
        db = get_database()
        if db is not None:
            result = db["demand_records"].insert_one(record)
            record["id"] = str(result.inserted_id)
            saved = True
    except PyMongoError:
        saved = False
    return {
        "predicted_demand": demand,
        "prepared_quantity": prepared,
        "estimated_surplus": record["estimated_surplus"],
        "saved_to_mongodb": saved,
        "mongodb_message": "Prediction saved" if saved else "Prediction calculated, but not saved (connect MongoDB to enable history).",
    }

@app.get("/api/history")
def history(limit: int = Query(default=10, ge=1, le=100)):
    col = collection()
    docs = list(col.find().sort("created_at", DESCENDING).limit(limit))
    return [clean_mongo_doc(d) for d in docs]

@app.post("/api/records", status_code=201)
def create_record(data: RecordInput):
    validate_categories(data.day, data.meal, data.item, data.weather, data.event)
    doc = {
        "record_type": "actual",
        **data.dict(),
        "estimated_waste": max(0, data.prepared_quantity - data.actual_sold),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    result = collection().insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc

@app.patch("/api/records/{record_id}")
def update_record(record_id: str, data: RecordUpdate):
    if not ObjectId.is_valid(record_id):
        raise HTTPException(status_code=400, detail="Invalid record ID")
    updates = {k: v for k, v in data.dict(exclude_unset=True).items()}
    if not updates:
        raise HTTPException(status_code=400, detail="Provide at least one field to update")
    col = collection()
    old = col.find_one({"_id": ObjectId(record_id)})
    if old is None:
        raise HTTPException(status_code=404, detail="Record not found")
    merged = {**old, **updates}
    if "prepared_quantity" in merged and "actual_sold" in merged:
        updates["estimated_waste"] = max(0, int(merged["prepared_quantity"]) - int(merged["actual_sold"]))
    col.update_one({"_id": ObjectId(record_id)}, {"$set": updates})
    return clean_mongo_doc(col.find_one({"_id": ObjectId(record_id)}))

@app.delete("/api/records/{record_id}")
def delete_record(record_id: str):
    if not ObjectId.is_valid(record_id):
        raise HTTPException(status_code=400, detail="Invalid record ID")
    result = collection().delete_one({"_id": ObjectId(record_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"deleted": True, "id": record_id}

@app.get("/api/stats")
def stats():
    col = collection()
    total = col.count_documents({})
    actual_count = col.count_documents({"record_type": "actual"})
    prediction_count = col.count_documents({"record_type": "prediction"})
    pipeline = [
        {"$match": {"record_type": "actual"}},
        {"$group": {"_id": None, "total_prepared": {"$sum": "$prepared_quantity"},
                    "total_sold": {"$sum": "$actual_sold"},
                    "total_waste": {"$sum": "$estimated_waste"}}}
    ]
    summary = list(col.aggregate(pipeline))
    totals = summary[0] if summary else {"total_prepared": 0, "total_sold": 0, "total_waste": 0}
    return {
        "total_records": total, "actual_records": actual_count,
        "prediction_records": prediction_count,
        "total_prepared": int(totals.get("total_prepared", 0)),
        "total_sold": int(totals.get("total_sold", 0)),
        "total_waste": int(totals.get("total_waste", 0)),
    }

@app.post("/api/seed")
def seed_dataset():
    """Import the included sample CSV into MongoDB once; skips duplicate seeding."""
    import pandas as pd
    from pathlib import Path
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB is not connected. Configure MONGODB_URI.")
    training_col = db["training_data"]
    if training_col.count_documents({}) > 0:
        return {"inserted": 0, "message": "Sample dataset already imported"}
    csv_path = Path(__file__).resolve().parent / "dataset.csv"
    data = pd.read_csv(csv_path).to_dict(orient="records")
    if data:
        training_col.insert_many(data)
    return {"inserted": len(data), "message": "Sample dataset imported into MongoDB collection training_data"}
