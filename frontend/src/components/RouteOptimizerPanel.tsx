import React, { useState, useEffect } from 'react';
import { Navigation, ShieldCheck, Clock, Fuel, AlertTriangle, ArrowRight, Check } from 'lucide-react';
import { RouteOptimizationResponse, RouteAlternative } from '../types';

interface RouteOptimizerPanelProps {
  onCalculateRoute: (origin: string, dest: string, cargo: string, urgency: string) => Promise<RouteOptimizationResponse>;
  onSelectRouteOverlay?: (routes: RouteAlternative[]) => void;
  isLoading: boolean;
}

export const RouteOptimizerPanel: React.FC<RouteOptimizerPanelProps> = ({
  onCalculateRoute,
  onSelectRouteOverlay,
  isLoading
}) => {
  const [origin, setOrigin] = useState<string>('Guwahati');
  const [destination, setDestination] = useState<string>('Tawang');
  const [cargoType, setCargoType] = useState<string>('Medical/Oxygen');
  const [urgency, setUrgency] = useState<string>('CRITICAL');
  const [routeResult, setRouteResult] = useState<RouteOptimizationResponse | null>(null);

  const handleCompute = async () => {
    const res = await onCalculateRoute(origin, destination, cargoType, urgency);
    setRouteResult(res);
    if (onSelectRouteOverlay && res?.evaluated_alternatives) {
      onSelectRouteOverlay(res.evaluated_alternatives);
    }
  };

  useEffect(() => {
    handleCompute();
  }, []);

  return (
    <div className="space-y-4">
      {/* Route Form */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-4">
        <div className="flex items-center space-x-2 mb-3">
          <Navigation className="w-4 h-4 text-blue-400" />
          <h2 className="text-sm font-bold uppercase tracking-wider text-white">
            AI Multi-Criteria Route Optimizer
          </h2>
        </div>

        <div className="grid grid-cols-2 gap-3 mb-3">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Origin Node</label>
            <select
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
            >
              <option value="Guwahati">Guwahati Central Logistics Depot</option>
              <option value="Tezpur">Tezpur Forward Transit Base</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Destination Target</label>
            <select
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
            >
              <option value="Tawang">Tawang District Hospital (Border Base)</option>
              <option value="Silchar">Silchar SMCH (Barak Valley Hub)</option>
              <option value="Shillong">Shillong NEIGRIHMS Trauma Center</option>
              <option value="Itanagar">Itanagar State Medical Hub</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 mb-4">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Cargo Classification</label>
            <select
              value={cargoType}
              onChange={(e) => setCargoType(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
            >
              <option value="Medical/Oxygen">Life-Saving Medical Oxygen / Blood</option>
              <option value="Refrigerated Vaccines">Refrigerated Pharma & Vaccines</option>
              <option value="Emergency Food">Disaster Dry Food Rations</option>
              <option value="General Freight">Standard Non-Perishable Cargo</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Mission Urgency</label>
            <select
              value={urgency}
              onChange={(e) => setUrgency(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
            >
              <option value="CRITICAL">CRITICAL (Zero Risk Tolerance)</option>
              <option value="HIGH">HIGH (Time-Sensitive)</option>
              <option value="NORMAL">NORMAL (Cost Balanced)</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleCompute}
          disabled={isLoading}
          className="w-full py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded text-xs font-semibold tracking-wide transition cursor-pointer shadow-sm flex items-center justify-center gap-1.5"
        >
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>{isLoading ? 'Evaluating Multi-Hazard Network...' : 'Compute AI Optimal Dispatch'}</span>
        </button>
      </div>

      {/* Route Alternatives Comparison Table */}
      {routeResult && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-lg p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-white">
              Corridor Alternatives Comparison
            </h3>
            <span className="text-[10px] text-blue-400 font-semibold bg-blue-950/80 px-2 py-0.5 rounded border border-blue-800/60">
              Priority Score: {routeResult.priority_score} / 10
            </span>
          </div>

          <div className="space-y-3">
            {routeResult.evaluated_alternatives.map((alt) => {
              const isRec = alt.is_recommended;
              const isBlocked = alt.safety_rating === 'IMPASSABLE';

              return (
                <div
                  key={alt.route_id}
                  className={`p-3 rounded-lg border transition ${
                    isBlocked
                      ? 'bg-rose-950/20 border-rose-900/60 opacity-80'
                      : isRec
                      ? 'bg-blue-950/30 border-blue-500/80 shadow-md ring-1 ring-blue-500/30'
                      : 'bg-slate-950 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-white">{alt.route_name}</span>
                        {isRec && (
                          <span className="text-[10px] font-bold bg-blue-600 text-white px-2 py-0.5 rounded flex items-center gap-1">
                            <Check className="w-3 h-3" /> AI RECOMMENDED
                          </span>
                        )}
                        {isBlocked && (
                          <span className="text-[10px] font-bold bg-rose-600 text-white px-2 py-0.5 rounded">
                            BLOCKED
                          </span>
                        )}
                      </div>
                      <div className="flex gap-1 mt-1">
                        {alt.highway_corridors.map((tag, idx) => (
                          <span key={idx} className="text-[9px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>

                    <span
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                        alt.safety_rating === 'SAFE'
                          ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                          : alt.safety_rating === 'MODERATE_CAUTION'
                          ? 'bg-amber-950 text-amber-300 border border-amber-800'
                          : 'bg-rose-950 text-rose-300 border border-rose-800'
                      }`}
                    >
                      {alt.safety_rating}
                    </span>
                  </div>

                  {/* Metrics Bar */}
                  <div className="grid grid-cols-4 gap-2 text-center text-xs py-2 bg-slate-900/80 rounded border border-slate-800/80 my-2">
                    <div>
                      <span className="text-[9px] text-slate-400 block uppercase">Distance</span>
                      <strong className="text-slate-200">{alt.distance_km} km</strong>
                    </div>
                    <div>
                      <span className="text-[9px] text-slate-400 block uppercase">AI ETA</span>
                      <strong className={isRec ? 'text-blue-300' : 'text-slate-200'}>
                        {isBlocked ? 'Impassable' : `${Math.floor(alt.ai_predicted_time_mins / 60)}h ${Math.round(alt.ai_predicted_time_mins % 60)}m`}
                      </strong>
                    </div>
                    <div>
                      <span className="text-[9px] text-slate-400 block uppercase">Risk Index</span>
                      <strong className={alt.composite_risk_score > 0.6 ? 'text-rose-400' : 'text-emerald-400'}>
                        {Math.round(alt.composite_risk_score * 100)}%
                      </strong>
                    </div>
                    <div>
                      <span className="text-[9px] text-slate-400 block uppercase">Est. Fuel</span>
                      <strong className="text-slate-200">₹{alt.estimated_fuel_cost_inr.toLocaleString()}</strong>
                    </div>
                  </div>

                  <p className="text-[11px] text-slate-300 leading-snug">
                    <span className="text-slate-400 font-medium">Tactical Assessment: </span>
                    {alt.ai_recommendation_reason}
                  </p>
                </div>
              );
            })}
          </div>

          {/* Rationale Quote */}
          <div className="bg-slate-950 p-3 rounded-md border border-slate-800 text-xs">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
              Optimization Synthesis:
            </span>
            <p className="text-slate-200 text-xs italic leading-relaxed">
              "{routeResult.tactical_rationale}"
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
