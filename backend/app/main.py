"""
NE-RAKSHAK AI — FastAPI Backend Server
Smart Logistics and Accessibility Intelligence Platform for NER (MDoNER / SIH26002)
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
from datetime import datetime

from backend.app.api.routes_roads import router as roads_router
from backend.app.api.routes_route import router as route_router
from backend.app.api.routes_eta import router as eta_router
from backend.app.api.routes_simulate import router as simulate_router
from backend.app.api.routes_operational import (
    alerts_router, vehicles_router, incidents_router, weather_router, facilities_router
)
from backend.app.services.weather_service import weather_service
from backend.app.services.routing_service import routing_service
from backend.app.services.fleet_service import fleet_service
from backend.app.services.alert_service import alert_service

active_connections = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(" [NE-RAKSHAK AI] Initializing GIS networks, Open-Meteo telemetry & ML models...")
    # Initialize weather
    weather_service.initialize_weather()
    print(" [NE-RAKSHAK AI] System Online. Ready for mission control operations.")
    yield
    print(" [NE-RAKSHAK AI] Shutting down...")

app = FastAPI(
    title="NE-RAKSHAK AI Platform",
    description="AI-Based Smart Logistics and Accessibility Intelligence Platform for the North Eastern Region (MDoNER / SIH26002)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(roads_router)
app.include_router(route_router)
app.include_router(eta_router)
app.include_router(simulate_router)
app.include_router(alerts_router)
app.include_router(vehicles_router)
app.include_router(incidents_router)
app.include_router(weather_router)
app.include_router(facilities_router)

@app.get("/")
def root():
    return {
        "platform": "NE-RAKSHAK AI",
        "purpose": "AI-Based Smart Logistics & Accessibility Intelligence Platform for NER",
        "ministry": "Ministry of Development of North Eastern Region (MDoNER)",
        "problem_statement": "SIH26002",
        "status": "OPERATIONAL",
        "active_corridors": len(routing_service.roads),
        "active_convoys": len(fleet_service.get_all_vehicles()),
        "timestamp": datetime.now().isoformat()
    }

@app.websocket("/ws/live")
async def websocket_live_feed(websocket: WebSocket):
    """
    WebSocket endpoint pushing periodic real-time telemetry updates and risk alerts.
    """
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            # Broadcast snapshot every 3 seconds
            payload = {
                "type": "TELEMETRY_PULSE",
                "timestamp": datetime.now().isoformat(),
                "vehicles": fleet_service.get_all_vehicles(),
                "active_alerts": alert_service.get_active_alerts()[:5],
                "corridor_summary": {
                    "total": len(routing_service.roads),
                    "blocked": len(routing_service.road_blockages)
                }
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(3.0)
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception:
        if websocket in active_connections:
            active_connections.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
