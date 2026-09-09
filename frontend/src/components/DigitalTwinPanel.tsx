import React, { useState } from 'react';
import { Cpu, AlertTriangle, ShieldCheck, Zap, ArrowRight, CheckCircle2, Copy } from 'lucide-react';
import { SimulationImpact, RoadSegment } from '../types';

interface DigitalTwinPanelProps {
  onSimulateRainfall: (region: string, mm: number) => Promise<void>;
  onSimulateBlockage: (roadId: string, reason: string) => Promise<void>;
  onReset: () => Promise<void>;
  isSimulating: boolean;
  impact: SimulationImpact | null;
  roads: RoadSegment[];
  isLoading: boolean;
}

export const DigitalTwinPanel: React.FC<DigitalTwinPanelProps> = ({
  onSimulateRainfall,
  onSimulateBlockage,
  onReset,
  isSimulating,
  impact,
  roads,
  isLoading
}) => {
  const [selectedScenario, setSelectedScenario] = useState<'RAINFALL' | 'BLOCKAGE'>('RAINFALL');
  const [rainfallMm, setRainfallMm] = useState<number>(120);
  const [selectedRegion, setSelectedRegion] = useState<string>('Tawang / West Kameng Corridor');
  const [selectedRoadId, setSelectedRoadId] = useState<string>('RD-BHK-BMD-03');
  const [blockageReason, setBlockageReason] = useState<string>('Severe Landslide & Rockfall Debris at Bhalukpong Pass');
  const [copied, setCopied] = useState<boolean>(false);

  const handleRunSimulation = async () => {
    if (selectedScenario === 'RAINFALL') {
      await onSimulateRainfall(selectedRegion, rainfallMm);
    } else {
      await onSimulateBlockage(selectedRoadId, blockageReason);
    }
  };

  const handleCopyDirective = () => {
    if (impact?.tactical_dispatch_directive) {
      navigator.clipboard.writeText(impact.tactical_dispatch_directive);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="space-y-4">
      {/* Simulation Controller Card */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-blue-400" />
            <h2 className="text-sm font-bold uppercase tracking-wider text-white">
              Digital Risk Twin — What-If Simulator
            </h2>
          </div>
          {isSimulating && (
            <span className="text-[10px] bg-amber-950/80 text-amber-300 border border-amber-700/60 px-2 py-0.5 rounded font-semibold uppercase animate-pulse">
              Scenario Active
            </span>
          )}
        </div>

        <p className="text-xs text-slate-400 mb-4">
          Stress-test the North Eastern road network under extreme weather shocks and physical obstructions to evaluate cascading logistics bottlenecks.
        </p>

        {/* Scenario Toggle */}
        <div className="grid grid-cols-2 gap-2 mb-4 bg-slate-950 p-1 rounded-md border border-slate-800">
          <button
            onClick={() => setSelectedScenario('RAINFALL')}
            className={`py-1.5 text-xs font-medium rounded transition cursor-pointer ${
              selectedScenario === 'RAINFALL'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Extreme Monsoon Rainfall
          </button>
          <button
            onClick={() => setSelectedScenario('BLOCKAGE')}
            className={`py-1.5 text-xs font-medium rounded transition cursor-pointer ${
              selectedScenario === 'BLOCKAGE'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Physical Corridor Blockage
          </button>
        </div>

        {selectedScenario === 'RAINFALL' ? (
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Target District Corridor</label>
              <select
                value={selectedRegion}
                onChange={(e) => setSelectedRegion(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
              >
                <option value="Tawang / West Kameng Corridor">Tawang / West Kameng Corridor (NH-13)</option>
                <option value="East Khasi / Jaintia Hills (Shillong - Silchar)">East Khasi / Jaintia Hills (NH-06 Silchar Lifeline)</option>
                <option value="Papum Pare / Itanagar Corridor">Papum Pare / Itanagar Trunk (NH-415)</option>
              </select>
            </div>

            <div>
              <div className="flex justify-between text-xs text-slate-300 mb-1">
                <span>Precipitation Inflation (24h):</span>
                <strong className="text-blue-400 font-mono">{rainfallMm} mm</strong>
              </div>
              <input
                type="range"
                min="40"
                max="220"
                step="10"
                value={rainfallMm}
                onChange={(e) => setRainfallMm(Number(e.target.value))}
                className="w-full accent-blue-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg"
              />
              <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                <span>40mm (Moderate)</span>
                <span>120mm (Severe Monsoon)</span>
                <span>220mm (Cloudburst)</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Select Corridor to Obstruct</label>
              <select
                value={selectedRoadId}
                onChange={(e) => setSelectedRoadId(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
              >
                {roads.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.name} ({r.highway_num})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Disaster / Obstruction Reason</label>
              <input
                type="text"
                value={blockageReason}
                onChange={(e) => setBlockageReason(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
                placeholder="e.g. Mudslide debris / Rockfall"
              />
            </div>
          </div>
        )}

        {/* Action Button */}
        <div className="flex items-center gap-2 mt-4">
          <button
            onClick={handleRunSimulation}
            disabled={isLoading}
            className="flex-1 flex items-center justify-center space-x-1.5 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded text-xs font-semibold tracking-wide transition cursor-pointer shadow-sm"
          >
            <Zap className="w-3.5 h-3.5" />
            <span>{isLoading ? 'Simulating Dynamic Cascade...' : 'Execute What-If Twin'}</span>
          </button>

          {isSimulating && (
            <button
              onClick={onReset}
              disabled={isLoading}
              className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded text-xs font-medium transition cursor-pointer"
            >
              Reset
            </button>
          )}
        </div>
      </div>

      {/* Simulation Cascade Impact Results */}
      {impact && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-lg p-4 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-rose-400" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-rose-300">
                Cascade Impact Assessment
              </h3>
            </div>
            <span className="text-[10px] text-slate-400 font-mono">
              {new Date(impact.triggered_at).toLocaleTimeString()}
            </span>
          </div>

          {/* Metrics Delta */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-slate-950 p-2.5 rounded border border-slate-800/80">
              <span className="text-[10px] uppercase text-slate-400 font-medium">Avg Fleet Delay</span>
              <div className="text-lg font-bold text-amber-400 mt-0.5">
                +{Math.round(impact.average_system_delay_minutes)} <span className="text-xs font-normal">mins</span>
              </div>
            </div>
            <div className="bg-slate-950 p-2.5 rounded border border-slate-800/80">
              <span className="text-[10px] uppercase text-slate-400 font-medium">Logistics Escalation</span>
              <div className="text-lg font-bold text-rose-400 mt-0.5">
                +₹{Math.round(impact.total_cost_escalation_inr).toLocaleString()}
              </div>
            </div>
          </div>

          {/* Impacted Infrastructure */}
          <div className="space-y-2 text-xs">
            <div>
              <span className="text-slate-400 font-medium block mb-1">Blocked Corridors:</span>
              <div className="space-y-1">
                {impact.blocked_corridors.length > 0 ? (
                  impact.blocked_corridors.map((c, i) => (
                    <div key={i} className="flex items-center gap-1.5 text-rose-300 bg-rose-950/40 px-2 py-1 rounded border border-rose-900/50">
                      <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
                      <span>{c}</span>
                    </div>
                  ))
                ) : (
                  <span className="text-emerald-400">No total blockages, caution advisories active.</span>
                )}
              </div>
            </div>

            <div>
              <span className="text-slate-400 font-medium block mb-1">Rerouted Supply Convoys:</span>
              <div className="space-y-1">
                {impact.affected_vehicles.map((v, i) => (
                  <div key={i} className="flex items-center gap-1.5 text-amber-300 bg-amber-950/30 px-2 py-1 rounded border border-amber-900/40">
                    <span>🚚 {v}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <span className="text-slate-400 font-medium block mb-1">Healthcare Buffer Warnings:</span>
              <div className="space-y-1">
                {impact.affected_hospitals.map((h, i) => (
                  <div key={i} className="flex items-center gap-1.5 text-cyan-300 bg-cyan-950/30 px-2 py-1 rounded border border-cyan-900/40">
                    <span>🏥 {h}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Tactical Dispatch Directive Card */}
          <div className="bg-slate-950 border border-blue-900/40 rounded-lg p-3 relative">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-bold tracking-wider text-blue-400 uppercase flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5" /> AI Tactical Dispatch Directive
              </span>
              <button
                onClick={handleCopyDirective}
                className="text-[10px] flex items-center gap-1 text-slate-400 hover:text-white bg-slate-800 px-2 py-0.5 rounded cursor-pointer"
              >
                {copied ? <CheckCircle2 className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>
            </div>
            <pre className="text-[11px] text-slate-200 whitespace-pre-wrap font-mono leading-relaxed bg-slate-900/60 p-2 rounded border border-slate-800">
              {impact.tactical_dispatch_directive}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};
