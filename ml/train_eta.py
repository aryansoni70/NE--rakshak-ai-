"""
Train ETA & Delay Regressor:
Trains Gradient Boosting models to predict:
- actual_time_mins (accounting for mountain road grades, risk scores, rainfall)
- delay_probability
- delay_mins

Generates explainable factors.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

NUM_FEATURES = [
    "distance_km",
    "nominal_speed_kmph",
    "slope_deg",
    "rainfall_mm",
    "risk_score",
    "elevation_m",
    "nominal_time_mins"
]
CAT_FEATURES = ["vehicle_type"]

def train_eta_model():
    data_path = "ml/data/synthetic/eta_synthetic.csv"
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"{data_path} not found. Run generate_synthetic_data.py first.")
        
    df = pd.read_csv(data_path)
    
    X = df[NUM_FEATURES + CAT_FEATURES]
    y_time = df["actual_time_mins"]
    y_delay_prob = df["delay_probability"]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", NUM_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_FEATURES)
        ]
    )
    
    X_train, X_test, y_t_tr, y_t_te, y_dp_tr, y_dp_te = train_test_split(
        X, y_time, y_delay_prob, test_size=0.2, random_state=42
    )
    
    print("Training ETA Regressor Pipeline...")
    pipeline_eta = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", GradientBoostingRegressor(n_estimators=140, learning_rate=0.08, max_depth=5, random_state=42))
    ])
    pipeline_eta.fit(X_train, y_t_tr)
    eta_preds = pipeline_eta.predict(X_test)
    print(f" ETA Prediction R2: {r2_score(y_t_te, eta_preds):.4f}, MAE: {mean_absolute_error(y_t_te, eta_preds):.2f} mins")
    
    print("Training Delay Probability Regressor...")
    pipeline_prob = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", GradientBoostingRegressor(n_estimators=100, learning_rate=0.08, max_depth=4, random_state=42))
    ])
    pipeline_prob.fit(X_train, y_dp_tr)
    prob_preds = pipeline_prob.predict(X_test)
    print(f" Delay Prob R2: {r2_score(y_dp_te, prob_preds):.4f}, MAE: {mean_absolute_error(y_dp_te, prob_preds):.3f}")
    
    os.makedirs("ml/models", exist_ok=True)
    os.makedirs("backend/app/models", exist_ok=True)
    
    bundle = {
        "num_features": NUM_FEATURES,
        "cat_features": CAT_FEATURES,
        "pipeline_eta": pipeline_eta,
        "pipeline_prob": pipeline_prob,
        "metrics": {
            "eta_r2": float(r2_score(y_t_te, eta_preds)),
            "eta_mae_mins": float(mean_absolute_error(y_t_te, eta_preds)),
            "prob_r2": float(r2_score(y_dp_te, prob_preds))
        }
    }
    
    joblib.dump(bundle, "ml/models/eta_bundle.joblib")
    joblib.dump(bundle, "backend/app/models/eta_bundle.joblib")
    print(" Saved ETA model bundle to ml/models/ and backend/app/models/")

if __name__ == "__main__":
    train_eta_model()
