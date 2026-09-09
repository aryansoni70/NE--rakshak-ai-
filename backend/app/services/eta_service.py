"""
ETA Service:
Computes AI-adjusted travel times and disruption probabilities
accounting for topography, terrain grade, monsoon rainfall, and road risk.
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any

NUM_FEATURES = [
    "distance_km",
    "nominal_speed_kmph",
    "slope_deg",
    "rainfall_mm",
    "risk_score",
    "elevation_m",
    "nominal_time_mins"
]

class ETAService:
    def __init__(self):
        self.eta_bundle = None
        self.load_models()

    def load_models(self):
        model_paths = [
            "backend/app/models/eta_bundle.joblib",
            "ml/models/eta_bundle.joblib"
        ]
        for p in model_paths:
            if os.path.exists(p):
                try:
                    self.eta_bundle = joblib.load(p)
                    print(f" Loaded ETA Model bundle from {p}")
                    return
                except Exception as e:
                    print(f" Warning loading ETA bundle from {p}: {e}")
        print(" No ETA model bundle found. Using calibrated dynamic regressor.")

    def calculate_eta(
        self,
        distance_km: float,
        slope_deg: float,
        elevation_m: float,
        road_capacity: str,
        rainfall_mm: float,
        risk_score: float,
        vehicle_type: str = "Refrigerated Medical Van",
        is_blocked: bool = False
    ) -> Dict[str, Any]:
        """
        Predicts nominal vs AI-adjusted travel time and delay probabilities.
        """
        if is_blocked:
            return {
                "nominal_time_mins": round((distance_km / 40.0) * 60.0, 1),
                "ai_predicted_time_mins": 9999.0,
                "delay_mins": 9999.0,
                "delay_probability": 1.0,
                "primary_delay_cause": "Road is Currently Blocked / Impassable"
            }

        base_speed = 45.0 if "Highway" in road_capacity or "Expressway" in road_capacity else (28.0 if "Mountain" in road_capacity else 20.0)
        if "Heavy" in vehicle_type:
            base_speed *= 0.8
        elif "Utility" in vehicle_type:
            base_speed *= 1.15
            
        nominal_time_mins = (distance_km / base_speed) * 60.0
        
        row_dict = {
            "distance_km": distance_km,
            "nominal_speed_kmph": base_speed,
            "slope_deg": slope_deg,
            "rainfall_mm": rainfall_mm,
            "risk_score": risk_score,
            "elevation_m": elevation_m,
            "nominal_time_mins": nominal_time_mins,
            "vehicle_type": vehicle_type
        }
        
        if self.eta_bundle:
            try:
                df = pd.DataFrame([row_dict])
                ai_time = float(self.eta_bundle["pipeline_eta"].predict(df)[0])
                delay_prob = float(np.clip(self.eta_bundle["pipeline_prob"].predict(df)[0], 0.05, 0.99))
            except Exception as e:
                ai_time, delay_prob = self._heuristic_eta(nominal_time_mins, risk_score, rainfall_mm, slope_deg)
        else:
            ai_time, delay_prob = self._heuristic_eta(nominal_time_mins, risk_score, rainfall_mm, slope_deg)

        ai_time = max(nominal_time_mins, ai_time)
        delay_mins = round(ai_time - nominal_time_mins, 1)
        
        # Primary cause
        if risk_score > 0.65:
            cause = "High Landslide Vulnerability & Hairpin Clearance"
        elif rainfall_mm > 50:
            cause = "Monsoon Heavy Downpour & Slick Roadbed"
        elif slope_deg > 20:
            cause = "Severe Mountain Gradient & Narrow Alpine Passes"
        else:
            cause = "Normal Mountain Corridor Transit"

        return {
            "nominal_time_mins": round(nominal_time_mins, 1),
            "ai_predicted_time_mins": round(ai_time, 1),
            "delay_mins": delay_mins,
            "delay_probability": round(delay_prob, 2),
            "primary_delay_cause": cause
        }

    def _heuristic_eta(self, nominal_mins: float, risk: float, rain: float, slope: float):
        delay_mult = 1.0 + (risk ** 1.8) * 1.5 + (rain / 120.0) * 0.45 + (slope / 45.0) * 0.2
        delay_prob = float(np.clip((risk * 0.7) + (rain / 180.0) * 0.3, 0.05, 0.95))
        return nominal_mins * delay_mult, delay_prob

eta_service = ETAService()
