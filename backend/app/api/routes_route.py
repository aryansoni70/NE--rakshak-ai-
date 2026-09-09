from fastapi import APIRouter, Query, Body
from typing import Optional, Dict, Any
from backend.app.services.routing_service import routing_service
from backend.app.models.schemas import ShipmentCreate

router = APIRouter(prefix="/api", tags=["Routing & Optimization"])

@router.get("/route")
def get_base_route(
    origin: str = Query("Guwahati", description="Origin city/base"),
    destination: str = Query("Tawang", description="Destination city/district"),
    cargo_type: str = Query("General Freight", description="Cargo type"),
    urgency: str = Query("NORMAL", description="Urgency: CRITICAL, HIGH, NORMAL")
):
    """Calculates multi-criteria routes between any NER origin and destination"""
    return routing_service.find_routes(
        origin=origin,
        destination=destination,
        cargo_type=cargo_type,
        urgency=urgency
    )

@router.get("/route/best")
def get_best_route(
    origin: str = Query("Guwahati"),
    destination: str = Query("Tawang"),
    cargo_type: str = Query("Medical/Oxygen"),
    urgency: str = Query("CRITICAL")
):
    """Returns the single top AI-recommended route with detailed tactical rationale"""
    result = routing_service.find_routes(
        origin=origin,
        destination=destination,
        cargo_type=cargo_type,
        urgency=urgency
    )
    return {
        "origin": origin,
        "destination": destination,
        "recommended_route": result["recommended_route"],
        "tactical_rationale": result["tactical_rationale"],
        "priority_score": result["priority_score"]
    }

@router.post("/shipments")
def create_and_score_shipment(payload: ShipmentCreate):
    """Creates a critical shipment, evaluates priority score, and generates optimal route alternatives"""
    res = routing_service.find_routes(
        origin=payload.origin,
        destination=payload.destination,
        cargo_type=payload.cargo_type,
        urgency=payload.urgency_level,
        vehicle_type=payload.vehicle_type
    )
    return {
        "shipment_id": "SHP-NER-9901",
        "cargo_type": payload.cargo_type,
        "destination_type": payload.destination_type,
        "urgency_level": payload.urgency_level,
        "priority_score": res["priority_score"],
        "recommended_route": res["recommended_route"],
        "evaluated_alternatives": res["evaluated_alternatives"],
        "tactical_rationale": res["tactical_rationale"]
    }
