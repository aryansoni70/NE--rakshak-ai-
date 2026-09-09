export interface RoadSegment {
  id: string;
  name: string;
  start_node: string;
  end_node: string;
  highway_num: string;
  length_km: number;
  slope_avg: number;
  max_elevation: number;
  terrain_type: string;
  road_capacity: string;
  base_risk_score: number;
  river_proximity_km: number;
  landslide_prone_score: number;
  flood_prone_score: number;
  coordinates: [number, number][]; // [lat, lng]
  current_rainfall_mm: number;
  landslide_risk: number;
  flood_risk: number;
  overall_risk: number;
  is_blocked: boolean;
  blockage_reason?: string;
  status: 'PASSABLE' | 'CAUTION' | 'HIGH_RISK' | 'BLOCKED';
}

export interface RoadRiskResponse {
  timestamp: string;
  total_corridors: number;
  high_risk_count: number;
  blocked_count: number;
  roads: RoadSegment[];
}

export interface WeatherSnapshot {
  district: string;
  state: string;
  lat: number;
  lng: number;
  temperature_c: number;
  rainfall_24h_mm: number;
  rainfall_forecast_mm: number;
  humidity_pct: number;
  wind_speed_kmh: number;
  is_simulated: boolean;
  recorded_at: string;
}

export interface VehicleTelemetry {
  id: string;
  label: string;
  driver_name: string;
  cargo_type: string;
  priority_level: 'CRITICAL' | 'HIGH' | 'STANDARD';
  origin: string;
  destination: string;
  current_lat: number;
  current_lng: number;
  speed_kmh: number;
  status: 'IN_TRANSIT' | 'DELAYED' | 'REROUTING' | 'COMPLETED';
  assigned_route_id: string;
  eta_mins: number;
  ai_risk_delay_mins: number;
  recommendation?: string;
}

export interface RouteAlternative {
  route_id: string;
  route_name: string;
  highway_corridors: string[];
  waypoints: [number, number][];
  distance_km: number;
  nominal_time_mins: number;
  ai_predicted_time_mins: number;
  delay_probability: number;
  composite_risk_score: number;
  estimated_fuel_cost_inr: number;
  weighted_optimization_score: number;
  is_recommended: boolean;
  ai_recommendation_reason: string;
  safety_rating: 'SAFE' | 'MODERATE_CAUTION' | 'HIGH_VULNERABILITY' | 'IMPASSABLE';
}

export interface RouteOptimizationResponse {
  origin: string;
  destination: string;
  cargo_type: string;
  priority_score: number;
  evaluated_alternatives: RouteAlternative[];
  recommended_route: RouteAlternative;
  tactical_rationale: string;
  disruption_warnings: string[];
}

export interface SimulationImpact {
  scenario: string;
  triggered_at: string;
  affected_roads: string[];
  blocked_corridors: string[];
  affected_vehicles: string[];
  affected_critical_shipments: string[];
  affected_hospitals: string[];
  average_system_delay_minutes: number;
  total_cost_escalation_inr: number;
  immediate_actions: string[];
  tactical_dispatch_directive: string;
}

export interface AlertItem {
  id: string;
  road_id?: string;
  severity: 'CRITICAL' | 'WARNING' | 'INFO';
  title: string;
  message: string;
  timestamp: string;
  active: boolean;
}

export interface CriticalFacility {
  id: string;
  name: string;
  node: string;
  lat: number;
  lng: number;
  type: string;
  critical_oxygen_hours: number;
  blood_stock_pct: number;
  bed_occupancy_pct: number;
}
