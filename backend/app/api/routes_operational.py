from fastapi import APIRouter
from backend.app.services.alert_service import alert_service
from backend.app.services.fleet_service import fleet_service
from backend.app.services.weather_service import weather_service
from backend.app.services.routing_service import CRITICAL_FACILITIES
from backend.app.models.schemas import IncidentReportCreate

alerts_router = APIRouter(prefix="/api/alerts", tags=["Alerts & Warnings"])
vehicles_router = APIRouter(prefix="/api/vehicles", tags=["Fleet & Telemetry"])
incidents_router = APIRouter(prefix="/api/incidents", tags=["Field Incident Reports"])
weather_router = APIRouter(prefix="/api/weather", tags=["Live Meteorological Feeds"])
facilities_router = APIRouter(prefix="/api/facilities", tags=["Critical Infrastructure & Hospitals"])

@alerts_router.get("")
def get_active_alerts():
    return alert_service.get_active_alerts()

@vehicles_router.get("")
def get_fleet_telemetry():
    return fleet_service.get_all_vehicles()

@incidents_router.get("")
def get_all_incidents():
    return alert_service.get_all_incidents()

@incidents_router.post("")
def report_field_incident(report: IncidentReportCreate):
    return alert_service.record_field_incident(report.dict())

@weather_router.get("")
def get_all_weather():
    return weather_service.get_all_snapshots()

@facilities_router.get("")
def get_critical_facilities():
    return CRITICAL_FACILITIES
