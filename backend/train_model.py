from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "dataset.csv"
MODEL_PATH = BASE_DIR / "model.joblib"
PREDICTIONS_PATH = BASE_DIR / "test_predictions.csv"
CATEGORICAL_FEATURES = ["day", "meal", "item", "weather", "event"]
TARGET = "demand"


def train():
    data = pd.read_csv(DATA_PATH)
    required = CATEGORICAL_FEATURES + [TARGET]
    missing = [column for column in required if column not in data.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
    data = data.dropna(subset=required).copy()

    X = data[CATEGORICAL_FEATURES]
    y = data[TARGET]
    # Use 70% of rows for training and keep 30% unseen for evaluation.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    preprocessor = ColumnTransformer(
        [("categories", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES)],
        remainder="drop",
    )
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(
            n_estimators=160, random_state=42, min_samples_leaf=2, n_jobs=-1
        )),
    ])
    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)
    # Compare against a simple baseline that always predicts the training-set mean.
    baseline_predictions = [float(y_train.mean())] * len(y_test)
    metrics = {
        "mae": round(float(mean_absolute_error(y_test, predictions)), 2),
        "rmse": round(float(mean_squared_error(y_test, predictions) ** 0.5), 2),
        "r2": round(float(r2_score(y_test, predictions)), 3),
        "baseline_mae": round(float(mean_absolute_error(y_test, baseline_predictions)), 2),
        "training_rows": int(len(X_train)),
        "testing_rows": int(len(X_test)),
        "total_rows": int(len(data)),
        "train_percent": 70,
        "test_percent": 30,
    }
    comparison = X_test.reset_index(drop=True).copy()
    comparison["actual_demand"] = y_test.reset_index(drop=True)
    comparison["predicted_demand"] = [round(float(value), 2) for value in predictions]
    comparison["absolute_error"] = (comparison["actual_demand"] - comparison["predicted_demand"]).abs().round(2)
    comparison.to_csv(PREDICTIONS_PATH, index=False)
    joblib.dump({"pipeline": pipeline, "metrics": metrics}, MODEL_PATH)

    print("MessMind regression model trained and evaluated.")
    print(f"Dataset rows: {metrics['total_rows']}")
    print(f"Training rows: {metrics['training_rows']} (70%)")
    print(f"Testing rows: {metrics['testing_rows']} (30%, unseen during training)")
    print(f"Test MAE: {metrics['mae']} plates | Baseline MAE: {metrics['baseline_mae']} plates")
    print(f"Test RMSE: {metrics['rmse']} plates | Test R²: {metrics['r2']}")
    print(f"Saved model: {MODEL_PATH}")
    print(f"Saved actual-vs-predicted test results: {PREDICTIONS_PATH}")
    return metrics

if __name__ == "__main__":
    train()


