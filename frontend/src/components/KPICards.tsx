import React from 'react';
import { Route, Truck, CloudRain, HeartPulse, AlertCircle } from 'lucide-react';
import { RoadSegment, VehicleTelemetry, WeatherSnapshot, CriticalFacility } from '../types';

interface KPICardsProps {
  roads: RoadSegment[];
  vehicles: VehicleTelemetry[];
  weather: WeatherSnapshot[];
  facilities: CriticalFacility[];
}

export const KPICards: React.FC<KPICardsProps> = ({ roads, vehicles, weather, facilities }) => {
  const totalCorridors = roads.length;
  const highRiskCorridors = roads.filter(r => r.overall_risk >= 0.65).length;
  const blockedCorridors = roads.filter(r => r.is_blocked).length;
  
  const activeConvoys = vehicles.length;
  const reroutingConvoys = vehicles.filter(v => v.status === 'REROUTING' || v.status === 'DELAYED').length;
  
  const maxRainfall = weather.reduce((max, w) => (w.rainfall_24h_mm > max ? w.rainfall_24h_mm : max), 0);
  const highestRainDistrict = weather.find(w => w.rainfall_24h_mm === maxRainfall)?.district || 'NER General';
  
  const minOxygenFacility = facilities.reduce((min, f) => (f.critical_oxygen_hours < min.critical_oxygen_hours ? f : min), facilities[0] || { name: 'None', critical_oxygen_hours: 0 });

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 px-6 py-3 bg-slate-950/40 border-b border-slate-800">
      {/* KPI 1: Highway Network */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg p-3 flex items-center justify-between">
        <div>
          <span className="text-[11px] font-medium uppercase text-slate-400 tracking-wider flex items-center gap-1.5">
            <Route className="w-3.5 h-3.5 text-blue-400" /> Corridors Monitored
          </span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-xl font-bold text-white">{totalCorridors}</span>
            <span className="text-xs text-slate-400">
              {blockedCorridors > 0 ? (
                <span className="text-rose-400 font-semibold">{blockedCorridors} Blocked</span>
              ) : highRiskCorridors > 0 ? (
                <span className="text-amber-400 font-semibold">{highRiskCorridors} At Risk</span>
              ) : (
                <span className="text-emerald-400">All Passable</span>
              )}
            </span>
          </div>
        </div>
        <div className="w-9 h-9 rounded-md bg-blue-950/50 border border-blue-800/30 flex items-center justify-center text-blue-400">
          <Route className="w-5 h-5" />
        </div>
      </div>

      {/* KPI 2: Active Convoys */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg p-3 flex items-center justify-between">
        <div>
          <span className="text-[11px] font-medium uppercase text-slate-400 tracking-wider flex items-center gap-1.5">
            <Truck className="w-3.5 h-3.5 text-indigo-400" /> Active Supply Convoys
          </span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-xl font-bold text-white">{activeConvoys}</span>
            <span className="text-xs">
              {reroutingConvoys > 0 ? (
                <span className="text-amber-400 font-semibold">{reroutingConvoys} Rerouting/Delayed</span>
              ) : (
                <span className="text-emerald-400 font-semibold">On Schedule</span>
              )}
            </span>
          </div>
        </div>
        <div className="w-9 h-9 rounded-md bg-indigo-950/50 border border-indigo-800/30 flex items-center justify-center text-indigo-400">
          <Truck className="w-5 h-5" />
        </div>
      </div>

      {/* KPI 3: Weather / Monsoon Peak */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg p-3 flex items-center justify-between">
        <div>
          <span className="text-[11px] font-medium uppercase text-slate-400 tracking-wider flex items-center gap-1.5">
            <CloudRain className="w-3.5 h-3.5 text-cyan-400" /> 24h Peak Rainfall
          </span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-xl font-bold text-cyan-300">{Math.round(maxRainfall)} <span className="text-xs font-normal text-slate-400">mm</span></span>
            <span className="text-[11px] text-slate-400 truncate max-w-[110px]" title={highestRainDistrict}>
              {highestRainDistrict.split('/')[0]}
            </span>
          </div>
        </div>
        <div className="w-9 h-9 rounded-md bg-cyan-950/50 border border-cyan-800/30 flex items-center justify-center text-cyan-400">
          <CloudRain className="w-5 h-5" />
        </div>
      </div>

      {/* KPI 4: Healthcare Buffer */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg p-3 flex items-center justify-between">
        <div>
          <span className="text-[11px] font-medium uppercase text-slate-400 tracking-wider flex items-center gap-1.5">
            <HeartPulse className="w-3.5 h-3.5 text-rose-400" /> Hospital Oxygen Reserve
          </span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-xl font-bold text-rose-300">{minOxygenFacility?.critical_oxygen_hours || 36} <span className="text-xs font-normal text-slate-400">hrs</span></span>
            <span className="text-[11px] text-slate-400 truncate max-w-[110px]" title={minOxygenFacility?.name}>
              {minOxygenFacility?.node || 'Tawang'} Base
            </span>
          </div>
        </div>
        <div className="w-9 h-9 rounded-md bg-rose-950/50 border border-rose-800/30 flex items-center justify-center text-rose-400">
          <HeartPulse className="w-5 h-5" />
        </div>
      </div>
    </div>
  );
};
