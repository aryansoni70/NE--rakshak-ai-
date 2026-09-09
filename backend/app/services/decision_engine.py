"""
Tactical Decision Engine:
Translates numerical model outputs, multi-hazard risk predictions, and corridor closures
into concrete, actionable directives for Disaster Management and Logistics Command.
"""

from typing import Dict, Any, List

class DecisionEngine:
    def generate_simulation_directive(self, impact: Dict[str, Any]) -> str:
        scenario = impact.get("scenario", "Disaster Scenario")
        affected_roads = impact.get("affected_roads", [])
        affected_vehicles = impact.get("affected_vehicles", [])
        affected_hospitals = impact.get("affected_hospitals", [])
        avg_delay = impact.get("average_system_delay_minutes", 0)
        
        directives = []
        directives.append(f"MISSION CONTROL ACTION PLAN — {scenario.upper()}:")
        
        if impact.get("blocked_corridors"):
            directives.append(
                f"1. IMMEDIATE ROAD CLOSURE: {', '.join(impact['blocked_corridors'])} marked IMPASSABLE. Issue BRO / State PWD clearance dispatch."
            )
            
        if affected_vehicles:
            directives.append(
                f"2. CONVOY REROUTE: Divert {len(affected_vehicles)} active supply convoys ({', '.join(affected_vehicles)}) onto the Orang - Kalaktang Bypass. Estimated delay overhead: +{int(avg_delay)} mins."
            )
            
        if affected_hospitals:
            directives.append(
                f"3. HEALTHCARE BUFFER ALERT: Initiate emergency oxygen and blood supply preservation protocol at {', '.join(affected_hospitals)}. Prepare Heli-drop contingency from Guwahati MDoNER Central Depot if road clearance exceeds 18 hours."
            )
            
        directives.append(
            "4. AUTOMATED NOTIFICATION: Push SMS/GIS warning to all NER field transport units and local district collectors."
        )
        
        return "\n\n".join(directives)

    def generate_route_directive(self, rec_route: Dict[str, Any], origin: str, dest: str, cargo: str) -> str:
        r_name = rec_route.get("route_name", "Primary Corridor")
        r_risk = int(rec_route.get("composite_risk_score", 0) * 100)
        eta_h = int(rec_route.get("ai_predicted_time_mins", 0) // 60)
        eta_m = int(rec_route.get("ai_predicted_time_mins", 0) % 60)
        cost = int(rec_route.get("estimated_fuel_cost_inr", 0))
        
        return (
            f"DISPATCH DIRECTIVE for {cargo.upper()} ({origin} → {dest}):\n"
            f"• Authorized Corridor: {r_name}\n"
            f"• AI Verified Arrival: ~{eta_h}h {eta_m}m (Risk Index: {r_risk}% - {rec_route.get('safety_rating')})\n"
            f"• Estimated Logistics Budget: ₹{cost:,}\n"
            f"• Rationale: {rec_route.get('ai_recommendation_reason')}"
        )

decision_engine = DecisionEngine()
