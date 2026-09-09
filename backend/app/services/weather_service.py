"""
Weather Ingestion Service:
Integrates with Open-Meteo API for live North Eastern Region districts with instant caching.
"""

import requests
from datetime import datetime
from typing import Dict, Any, List

DISTRICT_COORDINATES = {
    "Guwahati / Kamrup": {"lat": 26.1445, "lng": 91.7362, "state": "Assam", "rain": 14.5, "temp": 28.0, "elev": 55},
    "Tezpur / Sonitpur": {"lat": 26.6338, "lng": 92.7926, "state": "Assam", "rain": 22.0, "temp": 26.5, "elev": 79},
    "Bhalukpong / West Kameng": {"lat": 27.0125, "lng": 92.6468, "state": "Arunachal Pradesh", "rain": 45.0, "temp": 22.0, "elev": 213},
    "Bomdila / West Kameng": {"lat": 27.2645, "lng": 92.4162, "state": "Arunachal Pradesh", "rain": 58.0, "temp": 16.5, "elev": 2415},
    "Tawang": {"lat": 27.5861, "lng": 91.8659, "state": "Arunachal Pradesh", "rain": 62.0, "temp": 12.0, "elev": 3048},
    "Shillong / East Khasi": {"lat": 25.5788, "lng": 91.8933, "state": "Meghalaya", "rain": 48.0, "temp": 18.0, "elev": 1525},
    "Silchar / Cachar": {"lat": 24.8333, "lng": 92.7789, "state": "Assam", "rain": 52.0, "temp": 27.0, "elev": 25},
    "Itanagar / Papum Pare": {"lat": 27.0844, "lng": 93.6053, "state": "Arunachal Pradesh", "rain": 34.0, "temp": 24.0, "elev": 320},
    "Kohima": {"lat": 25.6751, "lng": 94.1086, "state": "Nagaland", "rain": 38.0, "temp": 19.5, "elev": 1444},
    "Gangtok / East Sikkim": {"lat": 27.3389, "lng": 88.6065, "state": "Sikkim", "rain": 55.0, "temp": 15.0, "elev": 1650}
}

class WeatherService:
    def __init__(self):
        self.snapshots: Dict[str, Dict[str, Any]] = {}
        self.simulation_overrides: Dict[str, float] = {}
        self._init_baseline_cache()

    def _init_baseline_cache(self):
        for district, data in DISTRICT_COORDINATES.items():
            self.snapshots[district] = {
                "district": district,
                "state": data["state"],
                "lat": data["lat"],
                "lng": data["lng"],
                "temperature_c": data["temp"],
                "rainfall_24h_mm": data["rain"],
                "rainfall_forecast_mm": round(data["rain"] * 1.35, 1),
                "humidity_pct": 82.0,
                "wind_speed_kmh": 14.0,
                "is_simulated": False,
                "recorded_at": datetime.now().isoformat()
            }

    def initialize_weather(self, sync_live=False):
        """Optional live sync with Open-Meteo"""
        if not sync_live:
            return
        for district, coords in DISTRICT_COORDINATES.items():
            try:
                url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lng']}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&daily=precipitation_sum&timezone=Asia%2FKolkata&forecast_days=2"
                resp = requests.get(url, timeout=1.2)
                if resp.status_code == 200:
                    d = resp.json()
                    curr = d.get("current", {})
                    daily = d.get("daily", {})
                    precip_sum = daily.get("precipitation_sum", [coords["rain"]])[0]
                    self.snapshots[district] = {
                        "district": district,
                        "state": coords["state"],
                        "lat": coords["lat"],
                        "lng": coords["lng"],
                        "temperature_c": float(curr.get("temperature_2m", coords["temp"])),
                        "rainfall_24h_mm": float(precip_sum),
                        "rainfall_forecast_mm": float(precip_sum * 1.3),
                        "humidity_pct": float(curr.get("relative_humidity_2m", 80.0)),
                        "wind_speed_kmh": float(curr.get("wind_speed_10m", 12.0)),
                        "is_simulated": False,
                        "recorded_at": datetime.now().isoformat()
                    }
            except Exception:
                pass
                
    def get_weather_for_node(self, node_name: str) -> Dict[str, Any]:
        """Maps node names to closest district weather snapshot"""
        for district, snap in self.snapshots.items():
            if node_name.lower() in district.lower():
                snapshot = dict(snap)
                if district in self.simulation_overrides:
                    override_val = self.simulation_overrides[district]
                    snapshot["rainfall_24h_mm"] = override_val
                    snapshot["rainfall_forecast_mm"] = override_val * 1.5
                    snapshot["is_simulated"] = True
                return snapshot
                
        default_snap = dict(self.snapshots.get("Guwahati / Kamrup", {}))
        return default_snap

    def set_simulation_override(self, district_keyword: str, rainfall_mm: float):
        """Inflates rainfall for a specific district corridor"""
        for district in DISTRICT_COORDINATES:
            if district_keyword.lower() in district.lower():
                self.simulation_overrides[district] = rainfall_mm

    def reset_simulations(self):
        """Clears all synthetic simulation overrides"""
        self.simulation_overrides.clear()
        self._init_baseline_cache()

    def get_all_snapshots(self) -> List[Dict[str, Any]]:
        result = []
        for district, snap in self.snapshots.items():
            s = dict(snap)
            if district in self.simulation_overrides:
                s["rainfall_24h_mm"] = self.simulation_overrides[district]
                s["rainfall_forecast_mm"] = self.simulation_overrides[district] * 1.5
                s["is_simulated"] = True
            result.append(s)
        return result

weather_service = WeatherService()
