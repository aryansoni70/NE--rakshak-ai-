"""
Routing & GIS Corridor Service:
Maintains the complete North Eastern Region highway graph, coordinates,
live road states (open/caution/blocked), and multi-criteria route optimization.
"""

import json
import os
import heapq
import requests
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv
from backend.app.services.weather_service import weather_service
from backend.app.services.risk_service import risk_service
from backend.app.services.eta_service import eta_service

load_dotenv()

# Detailed waypoint coordinates representing authentic North Eastern corridors
CORRIDOR_WAYPOINTS = {
    "RD-GHY-TEZ-01": [
        [26.1445, 91.7362], [26.1820, 91.9540], [26.3120, 92.2150], [26.5120, 92.5180], [26.6338, 92.7926]
    ],
    "RD-TEZ-BHK-02": [
        [26.6338, 92.7926], [26.8120, 92.7210], [26.9450, 92.6840], [27.0125, 92.6468]
    ],
    "RD-BHK-BMD-03": [
        [27.0125, 92.6468], [27.0850, 92.5620], [27.1820, 92.4850], [27.2645, 92.4162]
    ],
    "RD-BMD-DRG-04": [
        [27.2645, 92.4162], [27.3100, 92.3300], [27.3577, 92.2346]
    ],
    "RD-DRG-SELA-05": [
        [27.3577, 92.2346], [27.4250, 92.1750], [27.5042, 92.1026]
    ],
    "RD-SELA-TWG-06": [
        [27.5042, 92.1026], [27.5450, 92.0120], [27.5861, 91.8659]
    ],
    "RD-GHY-SHL-07": [
        [26.1445, 91.7362], [25.9820, 91.8120], [25.7920, 91.8840], [25.5788, 91.8933]
    ],
    "RD-SHL-SIL-08": [
        [25.5788, 91.8933], [25.4450, 92.1850], [25.1250, 92.4120], [24.8333, 92.7789]
    ],
    "RD-GHY-ITA-09": [
        [26.1445, 91.7362], [26.4250, 92.3120], [26.8520, 93.1250], [27.0844, 93.6053]
    ],
    "RD-GHY-NAG-10": [
        [26.1445, 91.7362], [26.3120, 92.8520], [25.9090, 93.7266], [25.6751, 94.1086]
    ],
    "RD-TEZ-ITA-11": [
        [26.6338, 92.7926], [26.7820, 93.1520], [26.9850, 93.4520], [27.0844, 93.6053]
    ],
    "RD-GHY-GTK-12": [
        [26.1445, 91.7362], [26.4520, 90.2520], [26.7210, 88.4210], [27.3389, 88.6065]
    ],
    # Strategic High-Altitude Bypass Corridor: Tezpur -> Orang -> Kalaktang -> Shergaon -> Rupa -> Dirang
    "RD-ORANG-KLK-13": [
        [26.6338, 92.7926], [26.8920, 92.1520], [27.1210, 92.1050], [27.3577, 92.2346]
    ]
}

# Authentic Critical Facilities for Disaster Logistics
CRITICAL_FACILITIES = [
    {
        "id": "HOSP-TWG-01",
        "name": "Khandro Drowa Tsangmu District Hospital",
        "node": "Tawang",
        "lat": 27.5890,
        "lng": 91.8670,
        "type": "District Hospital & High-Altitude Trauma Center",
        "critical_oxygen_hours": 36,
        "blood_stock_pct": 72,
        "bed_occupancy_pct": 88
    },
    {
        "id": "HOSP-BMD-02",
        "name": "Bomdila General Hospital & Army Base Medical Wing",
        "node": "Bomdila",
        "lat": 27.2680,
        "lng": 92.4210,
        "type": "General Hospital / Army Liaison",
        "critical_oxygen_hours": 54,
        "blood_stock_pct": 85,
        "bed_occupancy_pct": 65
    },
    {
        "id": "HOSP-SHL-03",
        "name": "NEIGRIHMS Super-Specialty Medical Institute",
        "node": "Shillong",
        "lat": 25.5920,
        "lng": 91.9340,
        "type": "Apex Regional Tertiary Care Referral Center",
        "critical_oxygen_hours": 120,
        "blood_stock_pct": 95,
        "bed_occupancy_pct": 92
    },
    {
        "id": "HOSP-SIL-04",
        "name": "Silchar Medical College & Hospital (SMCH)",
        "node": "Silchar",
        "lat": 24.8150,
        "lng": 92.7910,
        "type": "Barak Valley Regional Hub Hospital",
        "critical_oxygen_hours": 42,
        "blood_stock_pct": 68,
        "bed_occupancy_pct": 96
    },
    {
        "id": "DEPOT-GHY-01",
        "name": "MDoNER Central Disaster Logistics & Supply Base",
        "node": "Guwahati",
        "lat": 26.1490,
        "lng": 91.7450,
        "type": "Strategic Supply Depot & Heli-Dispatch",
        "critical_oxygen_hours": 999,
        "blood_stock_pct": 100,
        "bed_occupancy_pct": 0
    }
]

class RoutingService:
    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.roads: Dict[str, Dict[str, Any]] = {}
        self.road_blockages: Dict[str, str] = {}  # road_id -> reason
        self.ors_key = os.environ.get("OPENROUTESERVICE_API_KEY")
        self.google_key = os.environ.get("GOOGLE_MAPS_API_KEY")
        self.load_graph()

    def load_graph(self):
        data_path = "backend/app/data/ner_corridors.json"
        if os.path.exists(data_path):
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.nodes = data.get("nodes", {})
                for r in data.get("roads", []):
                    self.roads[r["id"]] = r
        else:
            print(" Corridor JSON not found. Initializing empty.")

        # Ensure strategic bypass road exists in memory
        if "RD-ORANG-KLK-13" not in self.roads:
            self.roads["RD-ORANG-KLK-13"] = {
                "id": "RD-ORANG-KLK-13",
                "name": "Orang - Kalaktang - Rupa Strategic Bypass Corridor",
                "start_node": "Tezpur",
                "end_node": "Dirang",
                "highway_num": "Bypass-OK",
                "length_km": 165.0,
                "slope_avg": 14.2,
                "max_elevation": 1820,
                "terrain_type": "Moderate Forested Ridge (Landslide Protected)",
                "road_capacity": "2-Lane Highway (Paved)",
                "base_risk_score": 0.22,
                "river_proximity_km": 1.8,
                "landslide_prone_score": 0.28,
                "flood_prone_score": 0.15
            }

    def block_road(self, road_id: str, reason: str = "Severe Landslide / Rockfall"):
        if road_id in self.roads:
            self.road_blockages[road_id] = reason
            return True
        return False

    def unblock_road(self, road_id: str):
        if road_id in self.road_blockages:
            del self.road_blockages[road_id]
            return True
        return False

    def reset_blockages(self):
        self.road_blockages.clear()

    def get_all_roads_with_live_risk(self) -> List[Dict[str, Any]]:
        """
        Returns full GeoJSON-compatible list of road segments with real-time AI risk scores.
        """
        results = []
        for r_id, road in self.roads.items():
            r = dict(road)
            is_blocked = r_id in self.road_blockages
            
            # Weather snapshot for the start node
            weather_snap = weather_service.get_weather_for_node(r["start_node"])
            risk_metrics = risk_service.predict_road_risk(r, weather_snap)
            
            r["current_rainfall_mm"] = risk_metrics["current_rainfall_mm"]
            r["landslide_risk"] = risk_metrics["landslide_risk"]
            r["flood_risk"] = risk_metrics["flood_risk"]
            r["overall_risk"] = 1.0 if is_blocked else risk_metrics["overall_risk"]
            r["is_blocked"] = is_blocked
            r["blockage_reason"] = self.road_blockages.get(r_id, None)
            r["status"] = "BLOCKED" if is_blocked else risk_metrics["status"]
            
            # Coordinates
            coords = CORRIDOR_WAYPOINTS.get(r_id, [
                [self.nodes[r["start_node"]]["lat"], self.nodes[r["start_node"]]["lng"]],
                [self.nodes[r["end_node"]]["lat"], self.nodes[r["end_node"]]["lng"]]
            ]) if (r["start_node"] in self.nodes and r["end_node"] in self.nodes) else []
            
            r["coordinates"] = coords
            results.append(r)
        return results

    def find_routes(
        self,
        origin: str = "Guwahati",
        destination: str = "Tawang",
        cargo_type: str = "Medical/Oxygen",
        urgency: str = "CRITICAL",
        vehicle_type: str = "Refrigerated Medical Van"
    ) -> Dict[str, Any]:
        """
        Generates 2-3 candidate routes (Primary Highway, Strategic Bypass, River/Plateau Alternative)
        and scores each using multi-criteria optimization.
        """
        roads_live = {r["id"]: r for r in self.get_all_roads_with_live_risk()}
        
        # Define candidate route options for typical NER corridors
        candidate_specs = []
        
        if origin == "Guwahati" and destination == "Tawang":
            candidate_specs = [
                {
                    "route_id": "RTE-GHY-TWG-NH13-PRIMARY",
                    "route_name": "Standard Arterial: NH-27 → NH-13 (via Bhalukpong & Sela Pass)",
                    "corridor_ids": [
                        "RD-GHY-TEZ-01",
                        "RD-TEZ-BHK-02",
                        "RD-BHK-BMD-03",
                        "RD-BMD-DRG-04",
                        "RD-DRG-SELA-05",
                        "RD-SELA-TWG-06"
                    ],
                    "corridor_tags": ["Arterial Highway", "NH-13", "Sela Tunnel"]
                },
                {
                    "route_id": "RTE-GHY-TWG-BYPASS-KALAKTANG",
                    "route_name": "Strategic Landslide-Resilient Bypass (via Orang - Kalaktang - Dirang)",
                    "corridor_ids": [
                        "RD-GHY-TEZ-01",
                        "RD-ORANG-KLK-13",
                        "RD-DRG-SELA-05",
                        "RD-SELA-TWG-06"
                    ],
                    "corridor_tags": ["Disaster Bypass", "Stable Ridge", "NH-13 Upper"]
                }
            ]
        elif origin == "Guwahati" and destination == "Silchar":
            candidate_specs = [
                {
                    "route_id": "RTE-GHY-SIL-NH06-DIRECT",
                    "route_name": "Direct Highway: NH-06 (Guwahati → Shillong → Jowai → Silchar)",
                    "corridor_ids": ["RD-GHY-SHL-07", "RD-SHL-SIL-08"],
                    "corridor_tags": ["Primary NH-06", "Meghalaya Plateau"]
                }
            ]
        else:
            # General fallback corridor
            candidate_specs = [
                {
                    "route_id": f"RTE-{origin.upper()}-{destination.upper()}-DIRECT",
                    "route_name": f"Direct Trunk: {origin} → {destination}",
                    "corridor_ids": ["RD-GHY-TEZ-01", "RD-TEZ-ITA-11"] if "Itanagar" in destination else ["RD-GHY-TEZ-01"],
                    "corridor_tags": ["National Highway"]
                }
            ]

        # Calculate metrics for each candidate
        evaluated_routes = []
        is_medical_or_critical = "Medical" in cargo_type or "Oxygen" in cargo_type or urgency == "CRITICAL"
        
        # Priority Weights:
        # For critical life-saving cargo: heavily penalize risk (w_risk = 0.55), lower cost importance
        # For general freight: balance time and cost
        if is_medical_or_critical:
            w_time = 0.25
            w_risk = 0.55
            w_cost = 0.10
            w_dist = 0.10
            priority_score = 9.5
        else:
            w_time = 0.40
            w_risk = 0.25
            w_cost = 0.20
            w_dist = 0.15
            priority_score = 5.0

        for spec in candidate_specs:
            total_dist_km = 0.0
            total_nom_time = 0.0
            total_ai_time = 0.0
            max_risk = 0.0
            weighted_risk_sum = 0.0
            any_blocked = False
            blocked_names = []
            all_coords = []
            
            for cid in spec["corridor_ids"]:
                road_info = roads_live.get(cid)
                if not road_info:
                    continue
                    
                total_dist_km += road_info["length_km"]
                risk_val = road_info["overall_risk"]
                max_risk = max(max_risk, risk_val)
                weighted_risk_sum += risk_val * road_info["length_km"]
                
                if road_info["is_blocked"]:
                    any_blocked = True
                    blocked_names.append(road_info["name"])
                    
                eta_eval = eta_service.calculate_eta(
                    distance_km=road_info["length_km"],
                    slope_deg=road_info["slope_avg"],
                    elevation_m=road_info["max_elevation"],
                    road_capacity=road_info["road_capacity"],
                    rainfall_mm=road_info["current_rainfall_mm"],
                    risk_score=risk_val,
                    vehicle_type=vehicle_type,
                    is_blocked=road_info["is_blocked"]
                )
                
                total_nom_time += eta_eval["nominal_time_mins"]
                total_ai_time += eta_eval["ai_predicted_time_mins"]
                
                # Append coordinates
                if road_info.get("coordinates"):
                    all_coords.extend(road_info["coordinates"])

            composite_risk = (weighted_risk_sum / total_dist_km) if total_dist_km > 0 else 0.5
            if any_blocked:
                composite_risk = 1.0
                total_ai_time = 9999.0
                
            fuel_cost = round(total_dist_km * 28.5 + (max_risk * 1200.0), 0)
            
            # Optimization objective score (lower is better)
            opt_score = (
                w_time * (total_ai_time / 60.0) +
                w_risk * (composite_risk * 100.0) +
                w_cost * (fuel_cost / 1000.0) +
                w_dist * (total_dist_km / 100.0)
            )
            
            if any_blocked:
                opt_score = 9999.0
                safety_rating = "IMPASSABLE"
                rec_reason = f"Impassable due to active road closure on: {', '.join(blocked_names)}"
            elif composite_risk > 0.65:
                safety_rating = "HIGH_VULNERABILITY"
                rec_reason = "High vulnerability to monsoon rockfalls & flash floods. Recommended only if alternative routes are unavailable."
            elif composite_risk > 0.35:
                safety_rating = "MODERATE_CAUTION"
                rec_reason = "Moderate risk. Pilot escorts and reduced speed advisories in effect."
            else:
                safety_rating = "SAFE"
                rec_reason = "Lowest risk corridor. Maximum terrain stability and weather resilience."

            evaluated_routes.append({
                "route_id": spec["route_id"],
                "route_name": spec["route_name"],
                "highway_corridors": spec["corridor_tags"],
                "waypoints": all_coords,
                "distance_km": round(total_dist_km, 1),
                "nominal_time_mins": round(total_nom_time, 1),
                "ai_predicted_time_mins": round(total_ai_time, 1),
                "delay_probability": round(min(0.98, composite_risk * 1.1), 2),
                "composite_risk_score": round(composite_risk, 3),
                "estimated_fuel_cost_inr": fuel_cost,
                "weighted_optimization_score": round(opt_score, 2),
                "is_recommended": False,
                "ai_recommendation_reason": rec_reason,
                "safety_rating": safety_rating
            })

        # Pick best route
        evaluated_routes.sort(key=lambda x: x["weighted_optimization_score"])
        if evaluated_routes:
            evaluated_routes[0]["is_recommended"] = True
            
        recommended = evaluated_routes[0] if evaluated_routes else None
        
        # Build transparent tactical rationale
        if recommended:
            if is_medical_or_critical:
                rationale = (
                    f"Selected {recommended['route_name']} prioritizing SAFETY & MISSION RELIABILITY. "
                    f"Risk index is {int(recommended['composite_risk_score']*100)}% with AI ETA of {int(recommended['ai_predicted_time_mins']//60)}h {int(recommended['ai_predicted_time_mins']%60)}m. "
                    f"Safeguards urgent delivery to {destination} facilities against monsoon landslides."
                )
            else:
                rationale = (
                    f"Recommended {recommended['route_name']} optimizing overall transit time ({int(recommended['ai_predicted_time_mins']//60)}h {int(recommended['ai_predicted_time_mins']%60)}m) "
                    f"and logistical expenditure (₹{int(recommended['estimated_fuel_cost_inr'])})."
                )
        else:
            rationale = "No viable routes currently passable across the requested corridor."

        return {
            "origin": origin,
            "destination": destination,
            "cargo_type": cargo_type,
            "priority_score": priority_score,
            "evaluated_alternatives": evaluated_routes,
            "recommended_route": recommended,
            "tactical_rationale": rationale,
            "disruption_warnings": [r["ai_recommendation_reason"] for r in evaluated_routes if r["composite_risk_score"] > 0.6]
        }

routing_service = RoutingService()
