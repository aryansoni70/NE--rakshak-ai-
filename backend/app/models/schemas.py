"""
Pydantic Schemas for NE-RAKSHAK AI:
Defines stable API contracts for roads, telemetry, risk metrics, routes, simulations, alerts, and field incidents.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class Coordinate(BaseModel):
    lat: float
    lng: float
    name: Optional[str] = None
    elevation_m: Optional[float] = None
    state: Optional[str] = None

class RoadSegment(BaseModel):
    id: str
    name: str
    start_node: str
    end_node: str
    highway_num: str
    length_km: float
    slope_avg: float
    max_elevation: float
    terrain_type: str
    road_capacity: str
    base_risk_score: float
    river_proximity_km: float
    landslide_prone_score: float
    flood_prone_score: float
    coordinates: List[List[float]] = []  # [[lng, lat], ...] GeoJSON standard
    
    # Dynamic runtime risk attributes
    current_rainfall_mm: float = 0.0
    landslide_risk: float = 0.0
    flood_risk: float = 0.0
    overall_risk: float = 0.0
    is_blocked: bool = False
    blockage_reason: Optional[str] = None
    status: str = "PASSABLE"  # PASSABLE, CAUTION, HIGH_RISK, BLOCKED

class RoadRiskResponse(BaseModel):
    timestamp: str
    total_corridors: int
    high_risk_count: int
    blocked_count: int
    roads: List[RoadSegment]

class WeatherSnapshot(BaseModel):
    district: str
    state: str
    lat: float
    lng: float
    temperature_c: float
    rainfall_24h_mm: float
    rainfall_forecast_mm: float
    humidity_pct: float
    wind_speed_kmh: float
    is_simulated: bool = False
    recorded_at: str

class VehicleTelemetry(BaseModel):
    id: str
    label: str
    driver_name: str
    cargo_type: str  # Medical/Oxygen, Essential Food, Fuel/Power, Military/Relief, General
    priority_level: str  # CRITICAL, HIGH, STANDARD
    origin: str
    destination: str
    current_lat: float
    current_lng: float
    speed_kmh: float
    status: str  # IN_TRANSIT, DELAYED, REROUTING, COMPLETED
    assigned_route_id: str
    eta_mins: float
    ai_risk_delay_mins: float
    recommendation: Optional[str] = None

class ShipmentCreate(BaseModel):
    cargo_type: str  # Medical, Food, Relief, Fuel, General
    origin: str
    destination: str
    destination_type: str = "District Hospital / Relief Base"  # Hospital, Army Post, Relief Camp, Warehouse
    urgency_level: str = "CRITICAL"  # CRITICAL, HIGH, NORMAL
    weight_tons: float = 8.5
    vehicle_type: str = "Refrigerated Medical Van"

class RouteAlternative(BaseModel):
    route_id: str
    route_name: str
    highway_corridors: List[str]
    waypoints: List[List[float]]  # [[lat, lng], ...]
    distance_km: float
    nominal_time_mins: float
    ai_predicted_time_mins: float
    delay_probability: float
    composite_risk_score: float
    estimated_fuel_cost_inr: float
    weighted_optimization_score: float
    is_recommended: bool
    ai_recommendation_reason: str
    safety_rating: str  # SAFE, MODERATE_CAUTION, HIGH_VULNERABILITY, IMPASSABLE

class RouteOptimizationResponse(BaseModel):
    origin: str
    destination: str
    cargo_type: str
    priority_score: float
    evaluated_alternatives: List[RouteAlternative]
    recommended_route: RouteAlternative
    tactical_rationale: str
    disruption_warnings: List[str] = []

class IncidentReportCreate(BaseModel):
    incident_type: str  # LANDSLIDE, FLASH_FLOOD, BRIDGE_COLLAPSE, ROCKFALL, ROAD_EROSION
    road_id: str
    location_desc: str
    lat: float
    lng: float
    severity: str  # HIGH, CRITICAL, MODERATE
    blockage_extent_pct: int = 100
    reporter_badge: str = "NER-DISPATCH-FLD-09"
    notes: Optional[str] = None

class SimulationRainfallRequest(BaseModel):
    region: str = "Tawang / West Kameng Corridor"
    rainfall_inflation_mm: float = 120.0
    include_flash_flood: bool = True

class SimulationRoadBlockRequest(BaseModel):
    road_id: str = "RD-BHK-BMD-03"
    reason: str = "Severe Landslide Debris at Bhalukpong Pass"

class SimulationImpactResponse(BaseModel):
    scenario: str
    triggered_at: str
    affected_roads: List[str]
    blocked_corridors: List[str]
    affected_vehicles: List[str]
    affected_critical_shipments: List[str]
    affected_hospitals: List[str]
    average_system_delay_minutes: float
    total_cost_escalation_inr: float
    immediate_actions: List[str]
    tactical_dispatch_directive: str

class AlertItem(BaseModel):
    id: str
    road_id: Optional[str] = None
    severity: str  # CRITICAL, WARNING, INFO
    title: str
    message: str
    timestamp: str
    active: bool = True
