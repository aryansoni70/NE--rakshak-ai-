"""
Tactical Decision Engine:
Translates numerical model outputs, multi-hazard risk predictions, and corridor closures
into concrete, actionable directives for Disaster Management and Logistics Command.
Supports optional Google Gemini / OpenAI API key integration for AI tactical reasoning.
"""

import os
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class DecisionEngine:
    def __init__(self):
        self.gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.openai_key = os.environ.get("OPENAI_API_KEY")

    def generate_simulation_directive(self, impact: Dict[str, Any]) -> str:
        # Try LLM generation if API key is provided
        if self.gemini_key:
            llm_output = self._call_gemini_directive(impact)
            if llm_output:
                return llm_output
        elif self.openai_key:
            llm_output = self._call_openai_directive(impact)
            if llm_output:
                return llm_output

        # Default Deterministic Military/NDMA Tactical Template
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

    def _call_gemini_directive(self, impact: Dict[str, Any]) -> str:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
            prompt = (
                "You are the AI Logistics Commander for MDoNER / NDMA managing disaster transport in the North Eastern Region. "
                "Synthesize a concise, 4-bullet tactical dispatch directive for this scenario:\n"
                f"Scenario: {impact.get('scenario')}\n"
                f"Blocked Corridors: {impact.get('blocked_corridors')}\n"
                f"Affected Supply Convoys: {impact.get('affected_vehicles')}\n"
                f"Affected Hospitals & Buffers: {impact.get('affected_hospitals')}\n"
                f"Average Fleet Delay Overhead: +{impact.get('average_system_delay_minutes')} mins\n"
                "Format as authoritative numbered orders for convoy drivers, BRO clearance teams, and district emergency officers."
            )
            body = {"contents": [{"parts": [{"text": prompt}]}]}
            resp = requests.post(url, json=body, timeout=4.0)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception:
            pass
        return ""

    def _call_openai_directive(self, impact: Dict[str, Any]) -> str:
        try:
            headers = {"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"}
            prompt = (
                "You are the AI Logistics Commander for MDoNER / NDMA. Synthesize a concise, 4-bullet tactical dispatch directive for:\n"
                f"Scenario: {impact.get('scenario')}\nBlocked: {impact.get('blocked_corridors')}\n"
                f"Convoys: {impact.get('affected_vehicles')}\nHospitals: {impact.get('affected_hospitals')}\n"
                f"Delay: +{impact.get('average_system_delay_minutes')} mins"
            )
            body = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 250
            }
            resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body, timeout=4.0)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception:
            pass
        return ""

decision_engine = DecisionEngine()
