from fastapi import APIRouter
from datetime import datetime
from typing import List, Dict, Any
from backend.app.services.routing_service import routing_service
from backend.app.services.weather_service import weather_service

router = APIRouter(prefix="/api/roads", tags=["Roads & GIS Network"])

@router.get("")
def get_all_roads():
    """Returns all NER road network edges with basic geometry"""
    roads = routing_service.get_all_roads_with_live_risk()
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": r["id"],
                "properties": {
                    "id": r["id"],
                    "name": r["name"],
                    "highway_num": r["highway_num"],
                    "start_node": r["start_node"],
                    "end_node": r["end_node"],
                    "length_km": r["length_km"],
                    "slope_avg": r["slope_avg"],
                    "max_elevation": r["max_elevation"],
                    "terrain_type": r["terrain_type"],
                    "status": r["status"],
                    "overall_risk": r["overall_risk"]
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[pt[1], pt[0]] for pt in r.get("coordinates", [])] # GeoJSON [lng, lat]
                }
            }
            for r in roads
        ]
    }

@router.get("/risk")
def get_roads_with_risk():
    """Returns all road corridors with live multi-hazard risk scores and meteorological context"""
    roads = routing_service.get_all_roads_with_live_risk()
    high_risk = sum(1 for r in roads if r["overall_risk"] >= 0.65)
    blocked = sum(1 for r in roads if r["is_blocked"])
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total_corridors": len(roads),
        "high_risk_count": high_risk,
        "blocked_count": blocked,
        "roads": roads
    }

@router.post("/risk/refresh")
def refresh_risk():
    """Refreshes live weather readings from Open-Meteo and recomputes all road risk scores"""
    weather_service.initialize_weather()
    roads = routing_service.get_all_roads_with_live_risk()
    return {
        "status": "SUCCESS",
        "message": "Live meteorological data and road risk assessments refreshed.",
        "timestamp": datetime.now().isoformat(),
        "total_roads_updated": len(roads)
    }
