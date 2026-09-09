"""
Fleet & Telemetry Service:
Tracks simulated disaster logistics convoys across North Eastern Region corridors.
Simulates realistic GPS movement along waypoints, speed adjustments for terrain, and rerouting.
"""

from typing import List, Dict, Any, Optional
import random

INITIAL_VEHICLES = [
    {
        "id": "VH-101",
        "label": "Convoy Alpha-1 (Medical Oxygen)",
        "driver_name": "Subedar T. Dorjee",
        "cargo_type": "Critical Medical Oxygen Cylinders",
        "priority_level": "CRITICAL",
        "origin": "Guwahati Central Depot",
        "destination": "Tawang District Hospital",
        "current_lat": 26.8520,
        "current_lng": 92.7150,
        "speed_kmh": 34.0,
        "status": "IN_TRANSIT",
        "assigned_route_id": "RTE-GHY-TWG-NH13-PRIMARY",
        "eta_mins": 310.0,
        "ai_risk_delay_mins": 45.0,
        "recommendation": "Maintain safe convoy distance through Bhalukpong foothills."
    },
    {
        "id": "VH-102",
        "label": "Convoy Bravo-4 (Blood Plasma & Vaccines)",
        "driver_name": "Havildar R. Saikia",
        "cargo_type": "Refrigerated Vaccines & Blood Bank Units",
        "priority_level": "CRITICAL",
        "origin": "Guwahati Central Depot",
        "destination": "Bomdila General Hospital",
        "current_lat": 27.1200,
        "current_lng": 92.5100,
        "speed_kmh": 28.0,
        "status": "IN_TRANSIT",
        "assigned_route_id": "RTE-GHY-TWG-NH13-PRIMARY",
        "eta_mins": 140.0,
        "ai_risk_delay_mins": 30.0,
        "recommendation": "Approaching high-risk rockfall zone. Speed restricted to 30 km/h."
    },
    {
        "id": "VH-103",
        "label": "Convoy Charlie-9 (Emergency Food Rations)",
        "driver_name": "Naik K. Jamatia",
        "cargo_type": "Dry Rations & Water Purification Units",
        "priority_level": "HIGH",
        "origin": "Guwahati Central Depot",
        "destination": "Silchar Relief Hub",
        "current_lat": 25.4200,
        "current_lng": 92.2100,
        "speed_kmh": 42.0,
        "status": "IN_TRANSIT",
        "assigned_route_id": "RTE-GHY-SIL-NH06-DIRECT",
        "eta_mins": 220.0,
        "ai_risk_delay_mins": 75.0,
        "recommendation": "Caution advised along Jowai hillside cuts due to water pooling."
    },
    {
        "id": "VH-104",
        "label": "Convoy Delta-2 (Generators & Grid Repair)",
        "driver_name": "L/Nk P. Sangma",
        "cargo_type": "Disaster Power Generation Gear",
        "priority_level": "HIGH",
        "origin": "Guwahati Central Depot",
        "destination": "Itanagar Base",
        "current_lat": 26.6800,
        "current_lng": 93.0500,
        "speed_kmh": 55.0,
        "status": "IN_TRANSIT",
        "assigned_route_id": "RTE-GHY-ITA-TRUNK",
        "eta_mins": 115.0,
        "ai_risk_delay_mins": 12.0,
        "recommendation": "Smooth transit along NH-15 Northern Trunk."
    }
]

class FleetService:
    def __init__(self):
        self.vehicles: Dict[str, Dict[str, Any]] = {v["id"]: dict(v) for v in INITIAL_VEHICLES}

    def get_all_vehicles(self) -> List[Dict[str, Any]]:
        return list(self.vehicles.values())

    def update_vehicle_status(self, vehicle_id: str, status: str, route_id: Optional[str] = None, recommendation: Optional[str] = None):
        if vehicle_id in self.vehicles:
            self.vehicles[vehicle_id]["status"] = status
            if route_id:
                self.vehicles[vehicle_id]["assigned_route_id"] = route_id
            if recommendation:
                self.vehicles[vehicle_id]["recommendation"] = recommendation

    def reset_fleet(self):
        self.vehicles = {v["id"]: dict(v) for v in INITIAL_VEHICLES}

fleet_service = FleetService()
