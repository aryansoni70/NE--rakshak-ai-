from fastapi import APIRouter, Query
from backend.app.services.eta_service import eta_service

router = APIRouter(prefix="/api/eta", tags=["ETA & Travel Time Prediction"])

@router.get("")
def get_eta_prediction(
    distance_km: float = Query(180.0, description="Distance in km"),
    slope_deg: float = Query(16.5, description="Average terrain slope"),
    elevation_m: float = Query(2100.0, description="Max elevation in meters"),
    road_capacity: str = Query("2-Lane Mountain Road", description="Road type"),
    rainfall_mm: float = Query(45.0, description="Current 24h rainfall"),
    risk_score: float = Query(0.42, description="Assessed road risk score"),
    vehicle_type: str = Query("Refrigerated Medical Van", description="Vehicle classification")
):
    """Returns nominal vs AI-adjusted travel time, delay probability, and top contributing factor"""
    return eta_service.calculate_eta(
        distance_km=distance_km,
        slope_deg=slope_deg,
        elevation_m=elevation_m,
        road_capacity=road_capacity,
        rainfall_mm=rainfall_mm,
        risk_score=risk_score,
        vehicle_type=vehicle_type
    )
