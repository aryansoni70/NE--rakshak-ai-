import React from 'react';
import { ShieldAlert, RefreshCw, Radio, RotateCcw, AlertTriangle, PlusCircle } from 'lucide-react';

interface HeaderProps {
  onRefreshWeather: () => void;
  onResetSimulation: () => void;
  onOpenIncidentModal: () => void;
  isSimulating: boolean;
  activeAlertCount: number;
  blockedCount: number;
  isLoading: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  onRefreshWeather,
  onResetSimulation,
  onOpenIncidentModal,
  isSimulating,
  activeAlertCount,
  blockedCount,
  isLoading
}) => {
  return (
    <header className="bg-slate-900/90 backdrop-blur border-b border-slate-800 px-6 py-3 sticky top-0 z-50">
      <div className="flex flex-wrap items-center justify-between gap-4">
        {/* Ministry / System Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold text-lg shadow-sm">
            <ShieldAlert className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
                NE-RAKSHAK AI
                <span className="text-[10px] uppercase font-semibold tracking-wider bg-blue-900/60 text-blue-300 border border-blue-700/50 px-2 py-0.5 rounded">
                  MDoNER • SIH26002
                </span>
              </h1>
            </div>
            <p className="text-xs text-slate-400">
              AI Smart Logistics & Accessibility Intelligence Platform — North Eastern Region
            </p>
          </div>
        </div>

        {/* Operational Status Badges */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-md bg-slate-950/80 border border-slate-800 text-xs">
            <Radio className={`w-3.5 h-3.5 ${isSimulating ? 'text-amber-400 animate-pulse' : 'text-emerald-400'}`} />
            <span className="text-slate-400">Status:</span>
            <span className={`font-semibold ${isSimulating ? 'text-amber-400' : 'text-emerald-400'}`}>
              {isSimulating ? 'WHAT-IF TWIN ACTIVE' : 'LIVE TELEMETRY'}
            </span>
          </div>

          {blockedCount > 0 && (
            <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-rose-950/60 border border-rose-800/80 text-xs text-rose-300">
              <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
              <span>{blockedCount} Corridor{blockedCount > 1 ? 's' : ''} Blocked</span>
            </div>
          )}

          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-slate-950/80 border border-slate-800 text-xs text-slate-300">
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping"></span>
            <span>Alerts: <strong className="text-blue-300">{activeAlertCount}</strong></span>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-2">
          <button
            onClick={onOpenIncidentModal}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/40 text-xs font-medium transition cursor-pointer"
            title="Field Officer Geo-Report"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>Report Incident</span>
          </button>

          <button
            onClick={onRefreshWeather}
            disabled={isLoading}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium transition cursor-pointer"
            title="Sync Live Weather"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-blue-400' : ''}`} />
            <span>Sync Live Feed</span>
          </button>

          {isSimulating && (
            <button
              onClick={onResetSimulation}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 border border-amber-500/40 text-xs font-medium transition cursor-pointer"
              title="Reset What-If Simulation"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset State</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
