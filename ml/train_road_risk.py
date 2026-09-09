"""
Train Road Risk ML Models:
Trains Gradient Boosting and Random Forest Regressors/Classifiers to predict:
- landslide_risk (0.0 to 1.0)
- flood_risk (0.0 to 1.0)
- overall_risk (0.0 to 1.0)
- is_disrupted (0 or 1)

Exports feature importance and model metrics for full transparency.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, r2_score, classification_report

FEATURE_COLS = [
    "slope_deg",
    "elevation_m",
    "rainfall_24h_mm",
    "rainfall_7d_accum_mm",
    "temp_c",
    "soil_saturation",
    "river_proximity_km",
    "hist_disruptions",
    "satellite_water_proxy"
]

def train_road_risk():
    data_path = "ml/data/synthetic/road_risk_synthetic.csv"
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"{data_path} not found. Run generate_synthetic_data.py first.")
        
    df = pd.read_csv(data_path)
    X = df[FEATURE_COLS]
    
    y_landslide = df["landslide_risk"]
    y_flood = df["flood_risk"]
    y_overall = df["overall_risk"]
    y_disrupted = df["is_disrupted"]
    
    X_train, X_test, y_ls_tr, y_ls_te, y_fl_tr, y_fl_te, y_ov_tr, y_ov_te, y_dis_tr, y_dis_te = train_test_split(
        X, y_landslide, y_flood, y_overall, y_disrupted, test_size=0.2, random_state=42
    )
    
    print("Training Landslide Risk Regressor (Gradient Boosting)...")
    model_ls = GradientBoostingRegressor(n_estimators=120, learning_rate=0.08, max_depth=4, random_state=42)
    model_ls.fit(X_train, y_ls_tr)
    ls_preds = model_ls.predict(X_test)
    print(f" Landslide Risk R2: {r2_score(y_ls_te, ls_preds):.4f}, RMSE: {np.sqrt(mean_squared_error(y_ls_te, ls_preds)):.4f}")
    
    print("Training Flood Risk Regressor (Gradient Boosting)...")
    model_fl = GradientBoostingRegressor(n_estimators=120, learning_rate=0.08, max_depth=4, random_state=42)
    model_fl.fit(X_train, y_fl_tr)
    fl_preds = model_fl.predict(X_test)
    print(f" Flood Risk R2: {r2_score(y_fl_te, fl_preds):.4f}, RMSE: {np.sqrt(mean_squared_error(y_fl_te, fl_preds)):.4f}")
    
    print("Training Overall Road Risk Regressor (Gradient Boosting)...")
    model_ov = GradientBoostingRegressor(n_estimators=150, learning_rate=0.08, max_depth=5, random_state=42)
    model_ov.fit(X_train, y_ov_tr)
    ov_preds = model_ov.predict(X_test)
    print(f" Overall Risk R2: {r2_score(y_ov_te, ov_preds):.4f}, RMSE: {np.sqrt(mean_squared_error(y_ov_te, ov_preds)):.4f}")
    
    print("Training Disruption Classifier (Random Forest)...")
    model_clf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    model_clf.fit(X_train, y_dis_tr)
    clf_preds = model_clf.predict(X_test)
    print(" Disruption Classification Report:")
    print(classification_report(y_dis_te, clf_preds, digits=4))
    
    # Feature importances
    importances = dict(zip(FEATURE_COLS, [round(float(v), 4) for v in model_ov.feature_importances_]))
    print(f" Feature Importances (Overall Risk): {importances}")
    
    os.makedirs("ml/models", exist_ok=True)
    os.makedirs("backend/app/models", exist_ok=True)
    
    bundle = {
        "features": FEATURE_COLS,
        "model_landslide": model_ls,
        "model_flood": model_fl,
        "model_overall": model_ov,
        "model_disruption_clf": model_clf,
        "feature_importances": importances,
        "metrics": {
            "landslide_r2": float(r2_score(y_ls_te, ls_preds)),
            "flood_r2": float(r2_score(y_fl_te, fl_preds)),
            "overall_r2": float(r2_score(y_ov_te, ov_preds))
        }
    }
    
    joblib.dump(bundle, "ml/models/road_risk_bundle.joblib")
    joblib.dump(bundle, "backend/app/models/road_risk_bundle.joblib")
    print(" Saved road risk model bundle to ml/models/ and backend/app/models/")

if __name__ == "__main__":
    train_road_risk()
