"""Prediction helper. The regression pipeline is trained in train_model.py."""
from pathlib import Path
import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model.joblib"
_bundle = None

def get_model_bundle():
    global _bundle
    if _bundle is None:
        if not MODEL_PATH.exists():
            raise RuntimeError("Trained model not found. Run: python train_model.py")
        _bundle = joblib.load(MODEL_PATH)
    return _bundle

def predict_demand(day, meal, item, weather, event):
    row = pd.DataFrame([{
        "day": day, "meal": meal, "item": item,
        "weather": weather, "event": event
    }])
    bundle = get_model_bundle()
    prediction = float(bundle["pipeline"].predict(row)[0])
    return max(0, int(round(prediction)))

def get_metrics():
    return get_model_bundle()["metrics"]
