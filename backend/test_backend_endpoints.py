"""
Automated Backend Verification Test Suite
Tests all endpoints: roads, live risk, routing, ETA, simulation, incidents, alerts, facilities.
"""

import sys
import os
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_all():
    print(" [1/8] Testing Root...")
    res = client.get("/")
    assert res.status_code == 200, f"Root failed: {res.text}"
    print("    Root OK:", res.json()["platform"])

    print(" [2/8] Testing /api/roads and /api/roads/risk...")
    res = client.get("/api/roads")
    assert res.status_code == 200
    res_risk = client.get("/api/roads/risk")
    assert res_risk.status_code == 200
    data = res_risk.json()
    assert data["total_corridors"] > 0
    print(f"    Roads OK: {data['total_corridors']} corridors, {data['high_risk_count']} high risk")

    print(" [3/8] Testing /api/route and /api/route/best...")
    res = client.get("/api/route?origin=Guwahati&destination=Tawang&cargo_type=Medical/Oxygen&urgency=CRITICAL")
    assert res.status_code == 200
    r_data = res.json()
    assert len(r_data["evaluated_alternatives"]) >= 2
    assert r_data["recommended_route"] is not None
    print(f"    Routing OK: Recommended '{r_data['recommended_route']['route_name']}'")

    print(" [4/8] Testing /api/eta...")
    res = client.get("/api/eta?distance_km=180&slope_deg=22&elevation_m=2800&road_capacity=Mountain&rainfall_mm=65&risk_score=0.72")
    assert res.status_code == 200
    eta_res = res.json()
    assert eta_res["ai_predicted_time_mins"] > eta_res["nominal_time_mins"]
    print(f"    ETA OK: Nominal {eta_res['nominal_time_mins']}m -> AI Predicted {eta_res['ai_predicted_time_mins']}m ({eta_res['primary_delay_cause']})")

    print(" [5/8] Testing /api/simulate/rainfall (What-If Engine)...")
    sim_res = client.post("/api/simulate/rainfall", json={"region": "Tawang Corridor", "rainfall_inflation_mm": 130.0})
    assert sim_res.status_code == 200
    sim_data = sim_res.json()
    assert len(sim_data["affected_roads"]) > 0
    assert "tactical_dispatch_directive" in sim_data
    print(f"    Simulation OK: {len(sim_data['affected_roads'])} roads impacted, {len(sim_data['affected_hospitals'])} hospitals alerted")

    print(" [6/8] Testing /api/incidents (Field Officer Geo-Report)...")
    inc_res = client.post("/api/incidents", json={
        "incident_type": "LANDSLIDE",
        "road_id": "RD-TEZ-BHK-02",
        "location_desc": "Km 42 Bhalukpong Gate Debris",
        "lat": 27.012,
        "lng": 92.646,
        "severity": "CRITICAL",
        "blockage_extent_pct": 100,
        "reporter_badge": "NER-OFFICER-44"
    })
    assert inc_res.status_code == 200
    print("    Field Incident OK:", inc_res.json()["id"])

    print(" [7/8] Testing /api/alerts and /api/facilities...")
    assert client.get("/api/alerts").status_code == 200
    assert client.get("/api/facilities").status_code == 200
    print("    Alerts & Facilities OK")

    print(" [8/8] Testing /api/simulate/reset...")
    reset_res = client.post("/api/simulate/reset")
    assert reset_res.status_code == 200
    print("    Simulation Reset OK")

    print("\n ALL BACKEND TESTS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    test_all()
