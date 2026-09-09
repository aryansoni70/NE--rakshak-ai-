"""
Risk Service:
Loads offline-trained Gradient Boosting and Random Forest models to perform
real-time multi-hazard assessment on road corridors (Landslide, Flash Flood, Overall Vulnerability).
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from backend.app.services.weather_service import weather_service

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

class RiskService:
    def __init__(self):
        self.model_bundle = None
        self.load_models()

    def load_models(self):
        model_paths = [
            "backend/app/models/road_risk_bundle.joblib",
            "ml/models/road_risk_bundle.joblib"
        ]
        for p in model_paths:
            if os.path.exists(p):
                try:
                    self.model_bundle = joblib.load(p)
                    print(f" Loaded Road Risk Model bundle from {p}")
                    return
                except Exception as e:
                    print(f" Warning loading model bundle from {p}: {e}")
        print(" No pre-trained model bundle found yet. Initializing heuristic-calibrated fallback predictor.")

    def predict_road_risk(self, road: Dict[str, Any], weather_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """
        Computes real-time landslide risk, flood risk, and overall risk for a road segment.
        """
        rainfall_24h = weather_snapshot.get("rainfall_24h_mm", 20.0)
        rainfall_7d = rainfall_24h * 3.5
        temp_c = weather_snapshot.get("temperature_c", 22.0)
        slope = road.get("slope_avg", 10.0)
        elevation = road.get("max_elevation", 100.0)
        river_dist = road.get("river_proximity_km", 1.0)
        hist_disruptions = int(road.get("landslide_prone_score", 0.3) * 6)
        
        soil_saturation = min(1.0, (rainfall_7d / 300.0) + (0.3 if river_dist < 0.5 else 0.05))
        satellite_water_proxy = min(1.0, max(0.0, (rainfall_24h / 150.0) * 0.7 + (1.0 / (river_dist + 0.5)) * 0.2))
        
        features_dict = {
            "slope_deg": slope,
            "elevation_m": elevation,
            "rainfall_24h_mm": rainfall_24h,
            "rainfall_7d_accum_mm": rainfall_7d,
            "temp_c": temp_c,
            "soil_saturation": soil_saturation,
            "river_proximity_km": river_dist,
            "hist_disruptions": hist_disruptions,
            "satellite_water_proxy": satellite_water_proxy
        }
        
        if self.model_bundle:
            try:
                X = pd.DataFrame([features_dict])[FEATURE_COLS]
                ls_pred = float(np.clip(self.model_bundle["model_landslide"].predict(X)[0], 0.0, 1.0))
                fl_pred = float(np.clip(self.model_bundle["model_flood"].predict(X)[0], 0.0, 1.0))
                ov_pred = float(np.clip(self.model_bundle["model_overall"].predict(X)[0], 0.0, 1.0))
            except Exception as e:
                ls_pred, fl_pred, ov_pred = self._calibrated_fallback(features_dict, road)
        else:
            ls_pred, fl_pred, ov_pred = self._calibrated_fallback(features_dict, road)

        # Status categorization
        if ov_pred >= 0.70:
            status = "HIGH_RISK"
        elif ov_pred >= 0.38:
            status = "CAUTION"
        else:
            status = "PASSABLE"

        return {
            "road_id": road["id"],
            "current_rainfall_mm": round(rainfall_24h, 1),
            "landslide_risk": round(ls_pred, 3),
            "flood_risk": round(fl_pred, 3),
            "overall_risk": round(ov_pred, 3),
            "status": status,
            "soil_saturation": round(soil_saturation, 2),
            "satellite_water_proxy": round(satellite_water_proxy, 2),
            "dominant_threat": "Landslide / Slope Failure" if ls_pred > fl_pred else "Flash Flood / River Overflow"
        }

    def _calibrated_fallback(self, features: Dict[str, Any], road: Dict[str, Any]):
        slope = features["slope_deg"]
        rain = features["rainfall_24h_mm"]
        soil = features["soil_saturation"]
        river_dist = features["river_proximity_km"]
        
        ls_logits = (slope / 45.0) * 0.40 + (rain / 120.0) * 0.35 + soil * 0.25 - 0.20
        ls_risk = 1.0 / (1.0 + np.exp(-ls_logits * 4.5))
        
        fl_logits = (rain / 100.0) * 0.45 + (1.0 / (river_dist + 0.3)) * 0.30 - 0.30
        fl_risk = 1.0 / (1.0 + np.exp(-fl_logits * 4.0))
        
        ov_risk = max(ls_risk, fl_risk) * 0.85 + (ls_risk * fl_risk) * 0.15 + road.get("base_risk_score", 0.1) * 0.1
        return float(np.clip(ls_risk, 0.0, 1.0)), float(np.clip(fl_risk, 0.0, 1.0)), float(np.clip(ov_risk, 0.0, 1.0))

risk_service = RiskService()
