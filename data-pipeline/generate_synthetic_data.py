"""
Data Pipeline: Generates realistic NER road network features, terrain profiles,
historical disruption logs, and training sets for Road Risk and ETA models.
Data Provenance: Authentic NER geographic coordinates and highway nodes (NH-13, NH-15, NH-27, NH-10, NH-29, etc.)
fused with realistic terrain/weather disruption physics.
"""

import os
import json
import random
import numpy as np
import pandas as pd

# Authentic NER Corridor Nodes with accurate Coordinates
NER_NODES = {
    "Guwahati": {"lat": 26.1445, "lng": 91.7362, "elevation_m": 55, "state": "Assam"},
    "Tezpur": {"lat": 26.6338, "lng": 92.7926, "elevation_m": 79, "state": "Assam"},
    "Bhalukpong": {"lat": 27.0125, "lng": 92.6468, "elevation_m": 213, "state": "Arunachal Pradesh"},
    "Bomdila": {"lat": 27.2645, "lng": 92.4162, "elevation_m": 2415, "state": "Arunachal Pradesh"},
    "Dirang": {"lat": 27.3577, "lng": 92.2346, "elevation_m": 1560, "state": "Arunachal Pradesh"},
    "Sela Pass": {"lat": 27.5042, "lng": 92.1026, "elevation_m": 4170, "state": "Arunachal Pradesh"},
    "Tawang": {"lat": 27.5861, "lng": 91.8659, "elevation_m": 3048, "state": "Arunachal Pradesh"},
    "Itanagar": {"lat": 27.0844, "lng": 93.6053, "elevation_m": 320, "state": "Arunachal Pradesh"},
    "Shillong": {"lat": 25.5788, "lng": 91.8933, "elevation_m": 1525, "state": "Meghalaya"},
    "Cherrapunji": {"lat": 25.2986, "lng": 91.7167, "elevation_m": 1430, "state": "Meghalaya"},
    "Silchar": {"lat": 24.8333, "lng": 92.7789, "elevation_m": 25, "state": "Assam"},
    "Jorhat": {"lat": 26.7509, "lng": 94.2037, "elevation_m": 116, "state": "Assam"},
    "Dibrugarh": {"lat": 27.4728, "lng": 94.9120, "elevation_m": 108, "state": "Assam"},
    "Dimapur": {"lat": 25.9090, "lng": 93.7266, "elevation_m": 145, "state": "Nagaland"},
    "Kohima": {"lat": 25.6751, "lng": 94.1086, "elevation_m": 1444, "state": "Nagaland"},
    "Aizawl": {"lat": 23.7271, "lng": 92.7176, "elevation_m": 1132, "state": "Mizoram"},
    "Agartala": {"lat": 23.8315, "lng": 91.2868, "elevation_m": 15, "state": "Tripura"},
    "Gangtok": {"lat": 27.3389, "lng": 88.6065, "elevation_m": 1650, "state": "Sikkim"}
}

# Authentic Road Corridor Edges
NER_ROADS = [
    {
        "id": "RD-GHY-TEZ-01",
        "name": "NH-27 / NH-15 Guwahati - Tezpur Corridor",
        "start_node": "Guwahati",
        "end_node": "Tezpur",
        "highway_num": "NH-15",
        "length_km": 178.0,
        "slope_avg": 4.2,
        "max_elevation": 95,
        "terrain_type": "Plains / River Basin",
        "road_capacity": "4-Lane Highway",
        "base_risk_score": 0.12,
        "river_proximity_km": 0.8,
        "landslide_prone_score": 0.05,
        "flood_prone_score": 0.55
    },
    {
        "id": "RD-TEZ-BHK-02",
        "name": "NH-13 Tezpur - Bhalukpong Foothill Segment",
        "start_node": "Tezpur",
        "end_node": "Bhalukpong",
        "highway_num": "NH-13",
        "length_km": 54.0,
        "slope_avg": 12.8,
        "max_elevation": 240,
        "terrain_type": "Dense Foothills / Gorge",
        "road_capacity": "2-Lane Highway",
        "base_risk_score": 0.35,
        "river_proximity_km": 0.2,
        "landslide_prone_score": 0.48,
        "flood_prone_score": 0.40
    },
    {
        "id": "RD-BHK-BMD-03",
        "name": "NH-13 Bhalukpong - Bomdila Mountain Pass",
        "start_node": "Bhalukpong",
        "end_node": "Bomdila",
        "highway_num": "NH-13",
        "length_km": 96.0,
        "slope_avg": 26.5,
        "max_elevation": 2450,
        "terrain_type": "Steep Alpine Gorge",
        "road_capacity": "2-Lane Mountain Road",
        "base_risk_score": 0.58,
        "river_proximity_km": 0.4,
        "landslide_prone_score": 0.82,
        "flood_prone_score": 0.20
    },
    {
        "id": "RD-BMD-DRG-04",
        "name": "Trans-Arunachal Bomdila - Dirang Valley",
        "start_node": "Bomdila",
        "end_node": "Dirang",
        "highway_num": "NH-13",
        "length_km": 42.0,
        "slope_avg": 16.0,
        "max_elevation": 2100,
        "terrain_type": "Himalayan Valley",
        "road_capacity": "2-Lane Mountain Road",
        "base_risk_score": 0.38,
        "river_proximity_km": 1.2,
        "landslide_prone_score": 0.52,
        "flood_prone_score": 0.15
    },
    {
        "id": "RD-DRG-SELA-05",
        "name": "NH-13 Dirang - Sela Pass Alpine Ascent",
        "start_node": "Dirang",
        "end_node": "Sela Pass",
        "highway_num": "NH-13",
        "length_km": 62.0,
        "slope_avg": 31.4,
        "max_elevation": 4170,
        "terrain_type": "High Alpine / Scree Slope",
        "road_capacity": "Single/2-Lane Alpine",
        "base_risk_score": 0.72,
        "river_proximity_km": 2.5,
        "landslide_prone_score": 0.89,
        "flood_prone_score": 0.08
    },
    {
        "id": "RD-SELA-TWG-06",
        "name": "NH-13 Sela Pass - Tawang Strategic Road",
        "start_node": "Sela Pass",
        "end_node": "Tawang",
        "highway_num": "NH-13",
        "length_km": 78.0,
        "slope_avg": 24.2,
        "max_elevation": 3200,
        "terrain_type": "High Altitude Border Corridor",
        "road_capacity": "2-Lane Mountain Road",
        "base_risk_score": 0.62,
        "river_proximity_km": 1.8,
        "landslide_prone_score": 0.76,
        "flood_prone_score": 0.10
    },
    {
        "id": "RD-GHY-SHL-07",
        "name": "NH-06 Guwahati - Shillong Expressway",
        "start_node": "Guwahati",
        "end_node": "Shillong",
        "highway_num": "NH-06",
        "length_km": 98.0,
        "slope_avg": 14.5,
        "max_elevation": 1550,
        "terrain_type": "Rolling Plateau",
        "road_capacity": "4-Lane Expressway",
        "base_risk_score": 0.18,
        "river_proximity_km": 3.0,
        "landslide_prone_score": 0.25,
        "flood_prone_score": 0.12
    },
    {
        "id": "RD-SHL-SIL-08",
        "name": "NH-06 Shillong - Jowai - Silchar Lifeline",
        "start_node": "Shillong",
        "end_node": "Silchar",
        "highway_num": "NH-06",
        "length_km": 215.0,
        "slope_avg": 22.0,
        "max_elevation": 1400,
        "terrain_type": "Rain-soaked Hill Cut / Clay Slopes",
        "road_capacity": "2-Lane Highway",
        "base_risk_score": 0.65,
        "river_proximity_km": 0.5,
        "landslide_prone_score": 0.85,
        "flood_prone_score": 0.60
    },
    {
        "id": "RD-GHY-ITA-09",
        "name": "NH-15 / NH-415 Guwahati - Itanagar Northern Trunk",
        "start_node": "Guwahati",
        "end_node": "Itanagar",
        "highway_num": "NH-415",
        "length_km": 320.0,
        "slope_avg": 8.5,
        "max_elevation": 350,
        "terrain_type": "Plains into Sub-Himalayan Foot",
        "road_capacity": "2/4-Lane Highway",
        "base_risk_score": 0.28,
        "river_proximity_km": 1.1,
        "landslide_prone_score": 0.35,
        "flood_prone_score": 0.45
    },
    {
        "id": "RD-GHY-NAG-10",
        "name": "NH-29 / NH-27 Guwahati - Dimapur - Kohima",
        "start_node": "Guwahati",
        "end_node": "Kohima",
        "highway_num": "NH-29",
        "length_km": 345.0,
        "slope_avg": 18.0,
        "max_elevation": 1500,
        "terrain_type": "Hill Range / Sinking Zones (Pagla Pahar)",
        "road_capacity": "2/4-Lane Highway",
        "base_risk_score": 0.52,
        "river_proximity_km": 0.9,
        "landslide_prone_score": 0.78,
        "flood_prone_score": 0.30
    },
    {
        "id": "RD-TEZ-ITA-11",
        "name": "NH-15 Tezpur - Gohpur - Itanagar Link",
        "start_node": "Tezpur",
        "end_node": "Itanagar",
        "highway_num": "NH-15",
        "length_km": 155.0,
        "slope_avg": 6.0,
        "max_elevation": 320,
        "terrain_type": "Assam Valley Bypass",
        "road_capacity": "2-Lane Highway",
        "base_risk_score": 0.22,
        "river_proximity_km": 1.5,
        "landslide_prone_score": 0.20,
        "flood_prone_score": 0.45
    },
    {
        "id": "RD-GHY-GTK-12",
        "name": "NH-27 / NH-10 Guwahati - Siliguri - Gangtok Arterial",
        "start_node": "Guwahati",
        "end_node": "Gangtok",
        "highway_num": "NH-10",
        "length_km": 540.0,
        "slope_avg": 21.0,
        "max_elevation": 1650,
        "terrain_type": "Teesta River Valley / Landslide Corridor",
        "road_capacity": "2-Lane Mountain Highway",
        "base_risk_score": 0.60,
        "river_proximity_km": 0.3,
        "landslide_prone_score": 0.88,
        "flood_prone_score": 0.50
    }
]

def generate_road_risk_dataset(n_samples=6000):
    """
    Generates synthetic training records simulating historical sensor/satellite/weather readings
    and resulting road disruption probabilities for training XGBoost/GradientBoost models.
    """
    random.seed(42)
    np.random.seed(42)
    
    rows = []
    
    for _ in range(n_samples):
        road = random.choice(NER_ROADS)
        
        # Weather features
        rainfall_24h = max(0.0, np.random.exponential(scale=35.0))
        if random.random() < 0.25:
            rainfall_24h += np.random.uniform(60.0, 180.0)
            
        rainfall_7d_accum = rainfall_24h * np.random.uniform(2.5, 5.0)
        temp_c = np.random.uniform(4.0, 34.0)
        
        # Terrain features
        slope = max(1.0, road["slope_avg"] + np.random.normal(0, 3.0))
        elevation = max(10, road["max_elevation"] + np.random.normal(0, 50.0))
        river_dist_km = max(0.05, road["river_proximity_km"] + np.random.normal(0, 0.2))
        
        # Soil moisture proxy (0.0 to 1.0)
        soil_saturation = min(1.0, (rainfall_7d_accum / 300.0) + (0.3 if river_dist_km < 0.5 else 0.05))
        
        # Historical disruption count on this segment in past 2 years
        hist_disruptions = int(road["landslide_prone_score"] * 8 + np.random.poisson(lam=1.2))
        
        # Satellite SAR surface change / water extent proxy (0.0 to 1.0)
        satellite_water_proxy = min(1.0, max(0.0, (rainfall_24h / 150.0) * 0.7 + (1.0 / (river_dist_km + 0.5)) * 0.2))
        
        # Ground truth generation (Disaster Physics formulation)
        landslide_logits = (
            (slope / 45.0) * 0.35 +
            (rainfall_24h / 120.0) * 0.30 +
            soil_saturation * 0.20 +
            road["landslide_prone_score"] * 0.25 +
            (hist_disruptions / 10.0) * 0.15 - 0.25
        )
        landslide_risk = 1.0 / (1.0 + np.exp(-landslide_logits * 5.0))
        landslide_risk = float(np.clip(landslide_risk + np.random.normal(0, 0.03), 0.0, 1.0))
        
        flood_logits = (
            (rainfall_24h / 100.0) * 0.45 +
            (1.0 / (river_dist_km + 0.2)) * 0.25 +
            (1.0 - min(1.0, elevation / 500.0)) * 0.20 +
            road["flood_prone_score"] * 0.30 - 0.30
        )
        flood_risk = 1.0 / (1.0 + np.exp(-flood_logits * 4.5))
        flood_risk = float(np.clip(flood_risk + np.random.normal(0, 0.03), 0.0, 1.0))
        
        overall_risk = float(np.clip(max(landslide_risk, flood_risk) * 0.85 + (landslide_risk * flood_risk) * 0.15 + road["base_risk_score"] * 0.1, 0.0, 1.0))
        is_disrupted = 1 if overall_risk > 0.65 else 0
        
        rows.append({
            "road_id": road["id"],
            "length_km": road["length_km"],
            "slope_deg": slope,
            "elevation_m": elevation,
            "rainfall_24h_mm": round(rainfall_24h, 2),
            "rainfall_7d_accum_mm": round(rainfall_7d_accum, 2),
            "temp_c": round(temp_c, 1),
            "soil_saturation": round(soil_saturation, 3),
            "river_proximity_km": round(river_dist_km, 2),
            "hist_disruptions": hist_disruptions,
            "satellite_water_proxy": round(satellite_water_proxy, 3),
            "landslide_risk": round(landslide_risk, 4),
            "flood_risk": round(flood_risk, 4),
            "overall_risk": round(overall_risk, 4),
            "is_disrupted": is_disrupted
        })
        
    return pd.DataFrame(rows)

def generate_eta_dataset(n_samples=5000):
    """
    Generates synthetic trip logs for ETA training:
    models non-linear delays based on mountain grade, rainfall, road risk, vehicle cargo load, and disruptions.
    """
    random.seed(42)
    np.random.seed(42)
    
    rows = []
    vehicle_types = ["Heavy Supply Truck (16T)", "4x4 Hill Freight Carrier", "Refrigerated Medical Van", "Light Disaster Utility (4WD)"]
    
    for _ in range(n_samples):
        road = random.choice(NER_ROADS)
        v_type = random.choice(vehicle_types)
        
        dist_km = road["length_km"] * np.random.uniform(0.8, 1.5)
        base_speed = 45.0 if "Highway" in road["road_capacity"] else (30.0 if "Mountain" in road["road_capacity"] else 20.0)
        
        if "Heavy" in v_type:
            base_speed *= 0.75
        elif "Light" in v_type:
            base_speed *= 1.15
            
        rainfall_mm = max(0.0, np.random.exponential(scale=30.0))
        risk_score = min(1.0, max(0.05, road["base_risk_score"] + (rainfall_mm / 150.0) * 0.6 + np.random.normal(0, 0.05)))
        
        # Nominal time without disruptions
        nominal_time_mins = (dist_km / base_speed) * 60.0
        
        # Weather/Risk delay multiplier
        delay_factor = 1.0 + (risk_score ** 1.8) * 1.6 + (rainfall_mm / 100.0) * 0.5
        
        # Random roadblock or heavy clearance delay if risk is high
        bottleneck_delay_mins = 0.0
        if risk_score > 0.65:
            if random.random() < 0.60:
                bottleneck_delay_mins = np.random.uniform(45.0, 240.0)
        elif risk_score > 0.35:
            if random.random() < 0.25:
                bottleneck_delay_mins = np.random.uniform(15.0, 60.0)
                
        actual_travel_time_mins = nominal_time_mins * delay_factor + bottleneck_delay_mins
        delay_mins = max(0.0, actual_travel_time_mins - nominal_time_mins)
        delay_prob = float(np.clip((risk_score * 0.7) + (rainfall_mm / 200.0) * 0.3, 0.05, 0.98))
        
        # Dominant cause
        if bottleneck_delay_mins > 30:
            cause = "Active Landslide Clearance / Road Blockage"
        elif rainfall_mm > 60:
            cause = "Torrential Rainfall & Reduced Visibility"
        elif road["slope_avg"] > 20:
            cause = "Steep Mountain Grade & Hairpin Bends"
        else:
            cause = "Standard Mountain Traffic Flow"
            
        rows.append({
            "distance_km": round(dist_km, 2),
            "nominal_speed_kmph": round(base_speed, 1),
            "slope_deg": road["slope_avg"],
            "rainfall_mm": round(rainfall_mm, 2),
            "risk_score": round(risk_score, 3),
            "elevation_m": road["max_elevation"],
            "vehicle_type": v_type,
            "nominal_time_mins": round(nominal_time_mins, 1),
            "actual_time_mins": round(actual_travel_time_mins, 1),
            "delay_mins": round(delay_mins, 1),
            "delay_probability": round(delay_prob, 3),
            "primary_delay_cause": cause
        })
        
    return pd.DataFrame(rows)

if __name__ == "__main__":
    os.makedirs("ml/data/synthetic", exist_ok=True)
    os.makedirs("backend/app/data", exist_ok=True)
    
    print("[1/3] Generating synthetic Road Risk dataset...")
    df_risk = generate_road_risk_dataset(7000)
    df_risk.to_csv("ml/data/synthetic/road_risk_synthetic.csv", index=False)
    print(f" Saved {len(df_risk)} road risk samples to ml/data/synthetic/road_risk_synthetic.csv")
    
    print("[2/3] Generating synthetic ETA & Delay dataset...")
    df_eta = generate_eta_dataset(6000)
    df_eta.to_csv("ml/data/synthetic/eta_synthetic.csv", index=False)
    print(f" Saved {len(df_eta)} ETA samples to ml/data/synthetic/eta_synthetic.csv")
    
    print("[3/3] Exporting NER Corridor Graph Metadata...")
    corridor_data = {
        "nodes": NER_NODES,
        "roads": NER_ROADS
    }
    with open("backend/app/data/ner_corridors.json", "w", encoding="utf-8") as f:
        json.dump(corridor_data, f, indent=2)
    print(" Saved corridor network metadata to backend/app/data/ner_corridors.json")
    print(" Data generation completed successfully!")
