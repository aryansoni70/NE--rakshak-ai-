"""
Alert and Incident Service:
Manages active disaster warnings, critical corridor closures,
field officer incident reports, and real-time event broadcasting.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

class AlertService:
    def __init__(self):
        self.alerts: List[Dict[str, Any]] = []
        self.incidents: List[Dict[str, Any]] = []
        self.initialize_default_alerts()

    def initialize_default_alerts(self):
        self.alerts = [
            {
                "id": "ALT-001",
                "road_id": "RD-DRG-SELA-05",
                "severity": "WARNING",
                "title": "Sela Pass High-Altitude Freezing Rain Alert",
                "message": "Heavy sleet and reduced traction between Dirang & Sela Pass. Chains required for 16T heavy transport vehicles.",
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "active": True
            },
            {
                "id": "ALT-002",
                "road_id": "RD-SHL-SIL-08",
                "severity": "CRITICAL",
                "title": "NH-06 Meghalaya-Barak Valley Mudslide Vulnerability",
                "message": "Continuous 72hr rainfall detected in East Jaintia Hills. AI landslide vulnerability score elevated to 85%.",
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "active": True
            }
        ]

    def add_alert(self, severity: str, title: str, message: str, road_id: Optional[str] = None) -> Dict[str, Any]:
        alert = {
            "id": f"ALT-{uuid.uuid4().hex[:6].upper()}",
            "road_id": road_id,
            "severity": severity,
            "title": title,
            "message": message,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "active": True
        }
        self.alerts.insert(0, alert)
        return alert

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        return self.alerts

    def record_field_incident(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        incident = {
            "id": f"INC-{uuid.uuid4().hex[:6].upper()}",
            "incident_type": report_data.get("incident_type", "LANDSLIDE"),
            "road_id": report_data.get("road_id"),
            "location_desc": report_data.get("location_desc"),
            "lat": report_data.get("lat"),
            "lng": report_data.get("lng"),
            "severity": report_data.get("severity", "CRITICAL"),
            "blockage_extent_pct": report_data.get("blockage_extent_pct", 100),
            "reporter_badge": report_data.get("reporter_badge", "FLD-DISPATCH"),
            "notes": report_data.get("notes"),
            "created_at": datetime.now().isoformat()
        }
        self.incidents.insert(0, incident)
        
        # Also auto-create a high severity alert
        self.add_alert(
            severity="CRITICAL",
            title=f"Field Incident: {incident['incident_type']} on {incident['road_id']}",
            message=f"{incident['location_desc']} - Extent: {incident['blockage_extent_pct']}% blockage. Reported by Officer {incident['reporter_badge']}.",
            road_id=incident["road_id"]
        )
        return incident

    def get_all_incidents(self) -> List[Dict[str, Any]]:
        return self.incidents

    def clear_all(self):
        self.alerts.clear()
        self.incidents.clear()
        self.initialize_default_alerts()

alert_service = AlertService()
