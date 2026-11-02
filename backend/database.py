"""MongoDB connection and collection helpers for MessMind."""
import os
from datetime import datetime, timezone
from pymongo import MongoClient, DESCENDING
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).resolve().parent / ".env")
from pymongo.errors import PyMongoError

_client = None
_db = None
_last_error = None

def get_database():
    """Return the configured database, or None when MongoDB is not configured/reachable."""
    global _client, _db, _last_error
    uri = os.getenv("MONGODB_URI", "").strip()
    if not uri:
        _last_error = "MONGODB_URI is not set"
        return None
    if _db is not None:
        return _db
    try:
        _client = MongoClient(uri, serverSelectionTimeoutMS=2500)
        _client.admin.command("ping")
        _db = _client[os.getenv("MONGODB_DATABASE", "messmind")]
        _last_error = None
        return _db
    except PyMongoError as exc:
        _last_error = str(exc)
        _client = None
        _db = None
        return None

def database_status():
    db = get_database()
    return {
        "connected": db is not None,
        "database": db.name if db is not None else os.getenv("MONGODB_DATABASE", "messmind"),
        "message": "Connected to MongoDB" if db is not None else (_last_error or "MongoDB unavailable"),
    }

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def clean_mongo_doc(doc):
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id"))
    return doc
