import React from 'react';
import { Truck, AlertCircle, ShieldAlert, ArrowUpRight, Compass } from 'lucide-react';
import { VehicleTelemetry } from '../types';

interface FleetTelemetryPanelProps {
  vehicles: VehicleTelemetry[];
  onFocusVehicle?: (v: VehicleTelemetry) => void;
}

export const FleetTelemetryPanel: React.FC<FleetTelemetryPanelProps> = ({ vehicles, onFocusVehicle }) => {
  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2">
          <Truck className="w-4 h-4 text-indigo-400" />
          <h2 className="text-sm font-bold uppercase tracking-wider text-white">
            Active Convoy Telemetry & Logistics Feed
          </h2>
        </div>
        <span className="text-xs text-slate-400">{vehicles.length} Units Deployed</span>
      </div>

      <div className="space-y-2.5">
        {vehicles.map((v) => {
          const isCritical = v.priority_level === 'CRITICAL';
          const isRerouting = v.status === 'REROUTING' || v.status === 'DELAYED';

          return (
            <div
              key={v.id}
              className="bg-slate-950 p-3 rounded-lg border border-slate-800/80 hover:border-slate-700 transition"
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white">{v.label}</span>
                    <span
                      className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${
                        isCritical
                          ? 'bg-rose-950 text-rose-300 border border-rose-800'
                          : 'bg-blue-950 text-blue-300 border border-blue-800'
                      }`}
                    >
                      {v.priority_level}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-0.5">
                    Driver: <span className="text-slate-300 font-medium">{v.driver_name}</span> • Cargo: <span className="text-blue-300 font-medium">{v.cargo_type}</span>
                  </div>
                </div>

                <span
                  className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                    isRerouting
                      ? 'bg-amber-950 text-amber-300 border border-amber-800'
                      : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                  }`}
                >
                  {v.status}
                </span>
              </div>

              {/* Transit Stats */}
              <div className="grid grid-cols-3 gap-2 mt-2 pt-2 border-t border-slate-900 text-[11px]">
                <div>
                  <span className="text-[9px] text-slate-400 block uppercase">Route Target</span>
                  <span className="text-slate-200 truncate block">{v.origin.split(' ')[0]} → {v.destination.split(' ')[0]}</span>
                </div>
                <div>
                  <span className="text-[9px] text-slate-400 block uppercase">Current Speed</span>
                  <span className="text-slate-200">{v.speed_kmh} km/h</span>
                </div>
                <div>
                  <span className="text-[9px] text-slate-400 block uppercase">AI Adjusted ETA</span>
                  <span className={isRerouting ? 'text-amber-400 font-semibold' : 'text-slate-200'}>
                    {Math.floor(v.eta_mins / 60)}h {Math.round(v.eta_mins % 60)}m
                  </span>
                </div>
              </div>

              {v.recommendation && (
                <div className="mt-2 text-[11px] bg-slate-900/80 p-2 rounded border border-slate-800 text-amber-200/90 flex items-start gap-1.5">
                  <ShieldAlert className="w-3.5 h-3.5 text-amber-400 flex-shrink-0 mt-0.5" />
                  <span>{v.recommendation}</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
