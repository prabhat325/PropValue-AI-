"""
Machine Learning Training Pipeline for House Price Prediction.
Trains a Scikit-Learn regression pipeline on property data and saves the artifact.
"""

import os
import json
import time
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "dataset.csv")
MODEL_DIR = os.path.join(BASE_DIR, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "model.joblib")
METADATA_PATH = os.path.join(MODEL_DIR, "metadata.json")

NUMERICAL_FEATURES = [
    "square_footage",
    "bedrooms",
    "bathrooms",
    "year_built",
    "lot_size_acres",
    "garage_spaces"
]

CATEGORICAL_FEATURES = [
    "zip_code",
    "renovation_status",
    "property_type"
]

TARGET = "price"

def load_data(filepath: str = DATA_PATH) -> pd.DataFrame:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at {filepath}. Please generate or provide dataset.csv")
    
    df = pd.read_csv(filepath)
    print(f"Loaded dataset from {filepath} with shape: {df.shape}", flush=True)
    
    # Ensure zip_code is treated as string for categorical one-hot encoding
    df["zip_code"] = df["zip_code"].astype(str)
    return df

def build_pipeline() -> Pipeline:
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERICAL_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES)
        ],
        remainder="drop"
    )

    # Use single-threaded n_jobs=1 to avoid any Python 3.14 Windows multiprocessing pool lock
    regressor = RandomForestRegressor(
        n_estimators=80,
        max_depth=16,
        min_samples_split=4,
        n_jobs=1,
        random_state=42
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", regressor)
    ])

    return pipeline

def train_and_evaluate():
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    start_time = time.time()
    df = load_data()

    # Verify columns
    required_cols = NUMERICAL_FEATURES + CATEGORICAL_FEATURES + [TARGET]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in dataset: {missing}")

    X = df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"Training set: {X_train.shape[0]} samples, Test set: {X_test.shape[0]} samples", flush=True)
    print("Fitting preprocessing pipeline and Random Forest regressor...", flush=True)

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    print("Pipeline fitting complete. Computing evaluation metrics...", flush=True)

    # Predictions & evaluation
    y_pred_train = pipeline.predict(X_train)
    y_pred_test = pipeline.predict(X_test)

    train_mae = mean_absolute_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)

    train_mse = mean_squared_error(y_train, y_pred_train)
    test_mse = mean_squared_error(y_test, y_pred_test)

    train_rmse = np.sqrt(train_mse)
    test_rmse = np.sqrt(test_mse)

    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    
    mape = float(np.mean(np.abs((y_test - y_pred_test) / y_test)) * 100)

    duration = time.time() - start_time

    print("=" * 60, flush=True)
    print("MODEL TRAINING & EVALUATION REPORT", flush=True)
    print("=" * 60, flush=True)
    print(f"Train R² Score : {train_r2:.4f}", flush=True)
    print(f"Test R² Score  : {test_r2:.4f}", flush=True)
    print(f"Test MAE       : ${test_mae:,.2f}", flush=True)
    print(f"Test RMSE      : ${test_rmse:,.2f}", flush=True)
    print(f"Test MAPE      : {mape:.2f}%", flush=True)
    print(f"Training Time  : {duration:.2f} seconds", flush=True)
    print("=" * 60, flush=True)

    # Save trained pipeline
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Trained model saved to: {MODEL_PATH}", flush=True)

    # Unique categories for validation
    unique_zips = sorted([str(x) for x in df["zip_code"].dropna().unique().tolist()])
    unique_renovations = sorted([str(x) for x in df["renovation_status"].dropna().unique().tolist()])
    unique_prop_types = sorted([str(x) for x in df["property_type"].dropna().unique().tolist()])

    metadata = {
        "model_name": "PropValue_RandomForest_Valuator",
        "version": "1.0.0",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "metrics": {
            "r2_score": round(test_r2, 4),
            "mae": round(test_mae, 2),
            "rmse": round(test_rmse, 2),
            "mape_percent": round(mape, 2)
        },
        "features": {
            "numerical": NUMERICAL_FEATURES,
            "categorical": CATEGORICAL_FEATURES
        },
        "allowed_categories": {
            "zip_code": unique_zips,
            "renovation_status": unique_renovations,
            "property_type": unique_prop_types
        },
        "training_samples": len(df)
    }

    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Model metadata saved to: {METADATA_PATH}", flush=True)

if __name__ == "__main__":
    train_and_evaluate()
