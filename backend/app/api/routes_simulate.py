from fastapi import APIRouter
from backend.app.models.schemas import SimulationRainfallRequest, SimulationRoadBlockRequest
from backend.app.services.simulation_engine import simulation_engine

router = APIRouter(prefix="/api/simulate", tags=["Digital Risk Twin / Simulation"])

@router.post("/rainfall")
def simulate_monsoon_rainfall(payload: SimulationRainfallRequest):
    """Simulates extreme rainfall in a specified corridor and cascades impacts"""
    return simulation_engine.simulate_rainfall(
        region=payload.region,
        rainfall_mm=payload.rainfall_inflation_mm
    )

@router.post("/road-block")
def simulate_corridor_blockage(payload: SimulationRoadBlockRequest):
    """Simulates physical road obstruction/rockfall on a specific corridor"""
    return simulation_engine.simulate_road_block(
        road_id=payload.road_id,
        reason=payload.reason
    )

@router.post("/reset")
def reset_simulation_state():
    """Resets all simulation parameters back to live state"""
    return simulation_engine.reset_all_simulations()
