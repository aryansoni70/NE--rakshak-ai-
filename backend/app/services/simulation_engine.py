"""
Digital Risk Twin / Simulation Engine:
Executes What-If disaster scenarios, cascades topological disruptions across
road networks, recalculates supply convoy schedules, evaluates hospital buffer stocks,
and synthesizes strategic rerouting directives.
"""

from datetime import datetime
from typing import Dict, Any, List
from backend.app.services.weather_service import weather_service
from backend.app.services.routing_service import routing_service, CRITICAL_FACILITIES
from backend.app.services.fleet_service import fleet_service
from backend.app.services.alert_service import alert_service
from backend.app.services.decision_engine import decision_engine

class SimulationEngine:
    def simulate_rainfall(self, region: str = "Tawang / West Kameng Corridor", rainfall_mm: float = 120.0) -> Dict[str, Any]:
        """
        Simulates extreme monsoon / cloudburst event in targeted district corridors.
        """
        # 1. Apply weather override
        weather_service.set_simulation_override("Kameng", rainfall_mm)
        weather_service.set_simulation_override("Tawang", rainfall_mm)
        
        # 2. Block vulnerable steep alpine gorge segment under severe rainfall
        blocked_roads = []
        if rainfall_mm >= 90.0:
            routing_service.block_road("RD-BHK-BMD-03", "Massive Rain-Triggered Landslide & Debris Flow at Bhalukpong Pass")
            blocked_roads.append("NH-13 Bhalukpong - Bomdila Pass (RD-BHK-BMD-03)")
            
        # 3. Assess affected roads
        all_roads = routing_service.get_all_roads_with_live_risk()
        affected_roads = [r["name"] for r in all_roads if r["overall_risk"] > 0.5 or r["is_blocked"]]
        
        # 4. Cascade to affected vehicles
        affected_vehicles = []
        for v in fleet_service.get_all_vehicles():
            if "TWG" in v["assigned_route_id"] or "Tawang" in v["destination"] or "Bomdila" in v["destination"]:
                fleet_service.update_vehicle_status(
                    v["id"],
                    status="REROUTING",
                    route_id="RTE-GHY-TWG-BYPASS-KALAKTANG",
                    recommendation=f"Reroute immediately via Orang - Kalaktang Bypass. Bhalukpong gorge blocked by {rainfall_mm}mm rain."
                )
                affected_vehicles.append(f"{v['label']} ({v['cargo_type']})")

        # 5. Assess affected hospital facilities
        affected_hospitals = []
        for h in CRITICAL_FACILITIES:
            if h["node"] in ["Tawang", "Bomdila"]:
                affected_hospitals.append(f"{h['name']} ({h['node']}) — Buffer remaining: {h['critical_oxygen_hours']}h")

        avg_delay = 58.0 if rainfall_mm > 100 else 32.0
        cost_escalation = 1850.0 * len(affected_vehicles) if affected_vehicles else 2400.0

        impact_data = {
            "scenario": f"Severe Monsoon Event: {int(rainfall_mm)}mm Precipitation in {region}",
            "triggered_at": datetime.now().isoformat(),
            "affected_roads": affected_roads,
            "blocked_corridors": blocked_roads,
            "affected_vehicles": affected_vehicles,
            "affected_critical_shipments": ["Oxygen Cylinder Consignment #OX-88", "Refrigerated Vaccines #VAC-104"],
            "affected_hospitals": affected_hospitals,
            "average_system_delay_minutes": avg_delay,
            "total_cost_escalation_inr": cost_escalation,
            "immediate_actions": [
                "Issue Emergency Red Alert on NH-13 Bhalukpong Mountain Cut.",
                "Activate Orang - Kalaktang - Rupa Bypass for all high-priority convoys.",
                "Alert Border Roads Organisation (BRO Project Vartak) for clearing equipment.",
                "Verify backup generator fuel and cryogenic liquid oxygen reserves at Tawang District Hospital."
            ]
        }
        
        directive = decision_engine.generate_simulation_directive(impact_data)
        impact_data["tactical_dispatch_directive"] = directive
        
        # Push to alert service
        alert_service.add_alert(
            severity="CRITICAL",
            title=f"Disaster Simulation: {int(rainfall_mm)}mm Monsoon Surge",
            message=f"{len(affected_roads)} road segments impacted. Bhalukpong Pass closed. Convoys rerouted via Kalaktang."
        )
        
        return impact_data

    def simulate_road_block(self, road_id: str, reason: str) -> Dict[str, Any]:
        """
        Simulates sudden physical obstruction / rockfall on any specific road corridor.
        """
        routing_service.block_road(road_id, reason)
        road_info = routing_service.roads.get(road_id, {})
        road_name = road_info.get("name", road_id)
        
        affected_vehicles = []
        for v in fleet_service.get_all_vehicles():
            fleet_service.update_vehicle_status(
                v["id"],
                status="REROUTING",
                recommendation=f"Diversion active: {road_name} blocked ({reason})."
            )
            affected_vehicles.append(f"{v['label']}")
            
        impact_data = {
            "scenario": f"Physical Corridor Obstruction on {road_name}",
            "triggered_at": datetime.now().isoformat(),
            "affected_roads": [road_name],
            "blocked_corridors": [f"{road_name} ({road_id})"],
            "affected_vehicles": affected_vehicles,
            "affected_critical_shipments": ["Emergency Medical Consignment #OX-88"],
            "affected_hospitals": ["Tawang District Hospital", "Bomdila General Hospital"],
            "average_system_delay_minutes": 45.0,
            "total_cost_escalation_inr": 3600.0,
            "immediate_actions": [
                f"Close entry checkposts to {road_name}.",
                "Divert all military & civilian freight to alternative regional bypass.",
                "Dispatch Earthmoving and Excavation Units to coordinate clearance."
            ]
        }
        
        directive = decision_engine.generate_simulation_directive(impact_data)
        impact_data["tactical_dispatch_directive"] = directive
        
        alert_service.add_alert(
            severity="CRITICAL",
            title=f"Corridor Closure: {road_name}",
            message=f"Traffic halted due to: {reason}. Alternate routes automatically calculated."
        )
        
        return impact_data

    def reset_all_simulations(self):
        """Resets weather and graph states back to live conditions"""
        weather_service.reset_simulations()
        routing_service.reset_blockages()
        fleet_service.reset_fleet()
        alert_service.clear_all()
        return {"status": "SUCCESS", "message": "All simulation overrides reset to live sensor/API state."}

simulation_engine = SimulationEngine()
