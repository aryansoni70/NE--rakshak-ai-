import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import { RoadSegment, VehicleTelemetry, CriticalFacility, RouteAlternative } from '../types';

interface MapViewProps {
  roads: RoadSegment[];
  vehicles: VehicleTelemetry[];
  facilities: CriticalFacility[];
  selectedRoutes: RouteAlternative[];
  highlightedRoadId?: string | null;
  onSelectRoad?: (road: RoadSegment) => void;
}

export const MapView: React.FC<MapViewProps> = ({
  roads,
  vehicles,
  facilities,
  selectedRoutes,
  highlightedRoadId,
  onSelectRoad
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const roadLayerGroupRef = useRef<L.LayerGroup | null>(null);
  const vehicleLayerGroupRef = useRef<L.LayerGroup | null>(null);
  const facilityLayerGroupRef = useRef<L.LayerGroup | null>(null);
  const routeLayerGroupRef = useRef<L.LayerGroup | null>(null);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    // Centered around Assam / Arunachal / Meghalaya NER core
    const map = L.map(mapContainerRef.current, {
      center: [26.6, 92.6],
      zoom: 7,
      minZoom: 6,
      maxZoom: 14,
      zoomControl: false
    });

    L.control.zoom({ position: 'topright' }).addTo(map);

    // High quality dark topographic tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
      subdomains: 'abcd',
      maxZoom: 19
    }).addTo(map);

    roadLayerGroupRef.current = L.layerGroup().addTo(map);
    routeLayerGroupRef.current = L.layerGroup().addTo(map);
    facilityLayerGroupRef.current = L.layerGroup().addTo(map);
    vehicleLayerGroupRef.current = L.layerGroup().addTo(map);

    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Render Roads
  useEffect(() => {
    if (!mapInstanceRef.current || !roadLayerGroupRef.current) return;
    roadLayerGroupRef.current.clearLayers();

    roads.forEach(road => {
      if (!road.coordinates || road.coordinates.length < 2) return;

      let color = '#10b981'; // Passable Green
      let dashArray = undefined;
      let weight = 4;
      let opacity = 0.85;

      if (road.is_blocked) {
        color = '#e11d48';
        dashArray = '6, 8';
        weight = 6;
        opacity = 1.0;
      } else if (road.overall_risk >= 0.65) {
        color = '#ef4444'; // Red
        weight = 5;
      } else if (road.overall_risk >= 0.35) {
        color = '#f59e0b'; // Amber
        weight = 4;
      }

      if (highlightedRoadId === road.id) {
        weight += 3;
        opacity = 1.0;
      }

      const polyline = L.polyline(road.coordinates, {
        color,
        weight,
        opacity,
        dashArray
      });

      // Interactive Popup
      const popupHtml = `
        <div style="font-family: inherit; font-size: 12px; min-width: 220px;">
          <div style="font-weight: bold; font-size: 13px; margin-bottom: 4px; color: ${color};">
            ${road.name}
          </div>
          <div style="display: flex; justify-content: space-between; margin-bottom: 3px; color: #cbd5e1;">
            <span>Highway:</span> <strong style="color: #fff;">${road.highway_num}</strong>
          </div>
          <div style="display: flex; justify-content: space-between; margin-bottom: 3px; color: #cbd5e1;">
            <span>Terrain / Max Elev:</span> <strong style="color: #fff;">${road.max_elevation}m (${road.slope_avg}°)</strong>
          </div>
          <div style="display: flex; justify-content: space-between; margin-bottom: 3px; color: #cbd5e1;">
            <span>24h Rainfall:</span> <strong style="color: #38bdf8;">${road.current_rainfall_mm} mm</strong>
          </div>
          <div style="display: flex; justify-content: space-between; margin-bottom: 3px; color: #cbd5e1;">
            <span>AI Landslide Risk:</span> <strong style="color: ${road.landslide_risk > 0.6 ? '#f87171' : '#facc15'};">${Math.round(road.landslide_risk * 100)}%</strong>
          </div>
          <div style="display: flex; justify-content: space-between; margin-bottom: 3px; color: #cbd5e1;">
            <span>AI Flood Risk:</span> <strong style="color: ${road.flood_risk > 0.6 ? '#f87171' : '#facc15'};">${Math.round(road.flood_risk * 100)}%</strong>
          </div>
          <div style="display: flex; justify-content: space-between; margin-top: 6px; padding-top: 4px; border-top: 1px solid #334155;">
            <span>Status:</span> <strong style="color: ${color};">${road.status} ${road.is_blocked ? '(BLOCKED)' : ''}</strong>
          </div>
          ${road.blockage_reason ? `<div style="margin-top: 4px; color: #fca5a5; font-size: 11px;">⚠️ ${road.blockage_reason}</div>` : ''}
        </div>
      `;

      polyline.bindPopup(popupHtml);
      polyline.on('click', () => {
        if (onSelectRoad) onSelectRoad(road);
      });

      polyline.addTo(roadLayerGroupRef.current!);
    });
  }, [roads, highlightedRoadId, onSelectRoad]);

  // Render Alternative Routes overlay
  useEffect(() => {
    if (!mapInstanceRef.current || !routeLayerGroupRef.current) return;
    routeLayerGroupRef.current.clearLayers();

    selectedRoutes.forEach(route => {
      if (!route.waypoints || route.waypoints.length < 2) return;

      const isRec = route.is_recommended;
      const color = isRec ? '#3b82f6' : '#8b5cf6'; // Blue for recommended, Purple for alternative

      const polyline = L.polyline(route.waypoints, {
        color,
        weight: isRec ? 6 : 4,
        opacity: 0.9,
        dashArray: isRec ? undefined : '5, 10'
      });

      polyline.bindPopup(`
        <div style="font-size: 12px;">
          <div style="font-weight: bold; color: ${color};">${route.route_name}</div>
          <div style="margin-top: 4px;">Distance: <strong>${route.distance_km} km</strong></div>
          <div>AI ETA: <strong>${Math.floor(route.ai_predicted_time_mins / 60)}h ${Math.round(route.ai_predicted_time_mins % 60)}m</strong></div>
          <div>Safety: <strong>${route.safety_rating}</strong></div>
          <div style="margin-top: 4px; color: #94a3b8; font-size: 11px;">${route.ai_recommendation_reason}</div>
        </div>
      `);

      polyline.addTo(routeLayerGroupRef.current!);
    });
  }, [selectedRoutes]);

  // Render Critical Facilities & Hospitals
  useEffect(() => {
    if (!mapInstanceRef.current || !facilityLayerGroupRef.current) return;
    facilityLayerGroupRef.current.clearLayers();

    facilities.forEach(fac => {
      const isHospital = fac.type.includes('Hospital') || fac.type.includes('Trauma');
      const iconHtml = `
        <div style="
          background-color: ${isHospital ? '#e11d48' : '#2563eb'};
          color: white;
          width: 26px;
          height: 26px;
          border-radius: 50%;
          border: 2px solid white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          font-size: 11px;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
        ">
          ${isHospital ? 'H' : 'D'}
        </div>
      `;

      const customIcon = L.divIcon({
        className: 'facility-marker',
        html: iconHtml,
        iconSize: [26, 26],
        iconAnchor: [13, 13]
      });

      const marker = L.marker([fac.lat, fac.lng], { icon: customIcon });
      marker.bindPopup(`
        <div style="font-size: 12px; min-width: 200px;">
          <div style="font-weight: bold; color: #f43f5e;">${fac.name}</div>
          <div style="font-size: 11px; color: #94a3b8; margin-bottom: 6px;">${fac.type}</div>
          <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
            <span>Critical Oxygen Reserve:</span> <strong style="color: ${fac.critical_oxygen_hours < 48 ? '#f87171' : '#34d399'};">${fac.critical_oxygen_hours} hrs</strong>
          </div>
          <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
            <span>Blood Stock:</span> <strong>${fac.blood_stock_pct}%</strong>
          </div>
          <div style="display: flex; justify-content: space-between;">
            <span>Bed Occupancy:</span> <strong>${fac.bed_occupancy_pct}%</strong>
          </div>
        </div>
      `);

      marker.addTo(facilityLayerGroupRef.current!);
    });
  }, [facilities]);

  // Render Vehicles / Convoys
  useEffect(() => {
    if (!mapInstanceRef.current || !vehicleLayerGroupRef.current) return;
    vehicleLayerGroupRef.current.clearLayers();

    vehicles.forEach(v => {
      const isCritical = v.priority_level === 'CRITICAL';
      const isRerouting = v.status === 'REROUTING' || v.status === 'DELAYED';
      const bg = isRerouting ? '#f59e0b' : (isCritical ? '#3b82f6' : '#10b981');

      const iconHtml = `
        <div style="position: relative; width: 30px; height: 30px;">
          <div style="
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            border-radius: 50%;
            background-color: ${bg};
            opacity: 0.4;
            animation: pulse-ring 1.8s infinite ease-in-out;
          "></div>
          <div style="
            position: absolute;
            top: 3px; left: 3px; width: 24px; height: 24px;
            background-color: ${bg};
            color: white;
            border-radius: 50%;
            border: 2px solid white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: bold;
            box-shadow: 0 4px 6px rgba(0,0,0,0.6);
          ">
            🚚
          </div>
        </div>
      `;

      const customIcon = L.divIcon({
        className: 'vehicle-marker',
        html: iconHtml,
        iconSize: [30, 30],
        iconAnchor: [15, 15]
      });

      const marker = L.marker([v.current_lat, v.current_lng], { icon: customIcon });
      marker.bindPopup(`
        <div style="font-size: 12px; min-width: 220px;">
          <div style="font-weight: bold; color: ${bg}; font-size: 13px;">${v.label}</div>
          <div style="color: #cbd5e1; font-size: 11px;">Driver: ${v.driver_name}</div>
          <div style="margin-top: 4px; padding-top: 4px; border-top: 1px solid #334155;">
            <div>Cargo: <strong style="color: #60a5fa;">${v.cargo_type}</strong></div>
            <div>Route: <strong>${v.origin} → ${v.destination}</strong></div>
            <div>Speed: <strong>${v.speed_kmh} km/h</strong></div>
            <div>Status: <strong style="color: ${isRerouting ? '#fbbf24' : '#34d399'};">${v.status}</strong></div>
          </div>
          ${v.recommendation ? `<div style="margin-top: 5px; color: #fde047; font-size: 11px; background: rgba(234,179,8,0.15); padding: 4px; border-radius: 4px;">📢 ${v.recommendation}</div>` : ''}
        </div>
      `);

      marker.addTo(vehicleLayerGroupRef.current!);
    });
  }, [vehicles]);

  return (
    <div className="relative w-full h-full min-h-[520px] rounded-lg overflow-hidden border border-slate-800 bg-slate-950">
      <div ref={mapContainerRef} className="w-full h-full" />

      {/* Map Legend */}
      <div className="absolute bottom-4 left-4 z-[400] bg-slate-900/90 backdrop-blur border border-slate-800 px-3 py-2.5 rounded-lg text-xs text-slate-300 shadow-xl pointer-events-auto">
        <div className="font-semibold text-white mb-1.5 flex items-center justify-between gap-4">
          <span>Corridor Risk Index</span>
          <span className="text-[10px] text-slate-400 font-normal">Real-Time GIS</span>
        </div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="w-3.5 h-1 bg-emerald-500 rounded"></span>
            <span>Passable (&lt;35% Risk)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3.5 h-1 bg-amber-500 rounded"></span>
            <span>Moderate Caution (35-65%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3.5 h-1 bg-rose-500 rounded"></span>
            <span>High Vulnerability (&gt;65%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3.5 h-1 border-t-2 border-dashed border-rose-600"></span>
            <span>Closed / Blocked Corridor</span>
          </div>
        </div>
        <div className="mt-2 pt-2 border-t border-slate-800 flex items-center justify-between text-[11px]">
          <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-rose-600 inline-block"></span> Hospital</span>
          <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-blue-600 inline-block"></span> Depot</span>
          <span className="flex items-center gap-1">🚚 Convoy</span>
        </div>
      </div>
    </div>
  );
};
