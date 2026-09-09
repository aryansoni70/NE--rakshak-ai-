import {
  RoadRiskResponse,
  WeatherSnapshot,
  VehicleTelemetry,
  RouteOptimizationResponse,
  SimulationImpact,
  AlertItem,
  CriticalFacility
} from '../types';

const API_BASE = 'http://localhost:8000/api';

export const api = {
  async getRoadsRisk(): Promise<RoadRiskResponse> {
    const res = await fetch(`${API_BASE}/roads/risk`);
    if (!res.ok) throw new Error('Failed to fetch road risks');
    return res.json();
  },

  async refreshRoadsRisk(): Promise<{ status: string; message: string }> {
    const res = await fetch(`${API_BASE}/roads/risk/refresh`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to refresh risks');
    return res.json();
  },

  async getWeather(): Promise<WeatherSnapshot[]> {
    const res = await fetch(`${API_BASE}/weather`);
    if (!res.ok) throw new Error('Failed to fetch weather');
    return res.json();
  },

  async getVehicles(): Promise<VehicleTelemetry[]> {
    const res = await fetch(`${API_BASE}/vehicles`);
    if (!res.ok) throw new Error('Failed to fetch fleet telemetry');
    return res.json();
  },

  async getAlerts(): Promise<AlertItem[]> {
    const res = await fetch(`${API_BASE}/alerts`);
    if (!res.ok) throw new Error('Failed to fetch alerts');
    return res.json();
  },

  async getFacilities(): Promise<CriticalFacility[]> {
    const res = await fetch(`${API_BASE}/facilities`);
    if (!res.ok) throw new Error('Failed to fetch facilities');
    return res.json();
  },

  async calculateRoute(
    origin: string,
    destination: string,
    cargoType: string,
    urgency: string
  ): Promise<RouteOptimizationResponse> {
    const params = new URLSearchParams({
      origin,
      destination,
      cargo_type: cargoType,
      urgency
    });
    const res = await fetch(`${API_BASE}/route?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to calculate optimized route');
    return res.json();
  },

  async simulateRainfall(region: string, rainfallInflationMm: number): Promise<SimulationImpact> {
    const res = await fetch(`${API_BASE}/simulate/rainfall`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ region, rainfall_inflation_mm: rainfallInflationMm })
    });
    if (!res.ok) throw new Error('Failed to execute rainfall simulation');
    return res.json();
  },

  async simulateRoadBlock(roadId: string, reason: string): Promise<SimulationImpact> {
    const res = await fetch(`${API_BASE}/simulate/road-block`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ road_id: roadId, reason })
    });
    if (!res.ok) throw new Error('Failed to execute road blockage simulation');
    return res.json();
  },

  async resetSimulation(): Promise<{ status: string; message: string }> {
    const res = await fetch(`${API_BASE}/simulate/reset`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to reset simulation');
    return res.json();
  },

  async submitIncident(data: {
    incident_type: string;
    road_id: string;
    location_desc: string;
    lat: number;
    lng: number;
    severity: string;
    blockage_extent_pct: number;
    reporter_badge: string;
    notes?: string;
  }): Promise<{ id: string }> {
    const res = await fetch(`${API_BASE}/incidents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to submit field incident');
    return res.json();
  }
};
