import React from 'react';
import { CloudRain, Wind, Droplets, Thermometer, Radio } from 'lucide-react';
import { WeatherSnapshot } from '../types';

interface WeatherPanelProps {
  weather: WeatherSnapshot[];
}

export const WeatherPanel: React.FC<WeatherPanelProps> = ({ weather }) => {
  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2">
          <CloudRain className="w-4 h-4 text-cyan-400" />
          <h2 className="text-sm font-bold uppercase tracking-wider text-white">
            NER Meteorological Stations & Precipitation Index
          </h2>
        </div>
        <span className="text-[10px] text-slate-400 flex items-center gap-1">
          <Radio className="w-3 h-3 text-cyan-400" /> Open-Meteo & Ground Telemetry
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 text-[10px] uppercase">
              <th className="py-2">District / State</th>
              <th className="py-2">24h Rainfall</th>
              <th className="py-2">Forecast</th>
              <th className="py-2">Temp</th>
              <th className="py-2">Humidity</th>
              <th className="py-2">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {weather.map((w, idx) => (
              <tr key={idx} className="hover:bg-slate-800/40 transition">
                <td className="py-2 font-medium text-white">
                  {w.district} <span className="text-[10px] text-slate-400 block font-normal">{w.state}</span>
                </td>
                <td className="py-2">
                  <span className={`font-semibold ${w.rainfall_24h_mm > 50 ? 'text-rose-400' : w.rainfall_24h_mm > 25 ? 'text-amber-400' : 'text-cyan-300'}`}>
                    {w.rainfall_24h_mm} mm
                  </span>
                </td>
                <td className="py-2 text-slate-300">{w.rainfall_forecast_mm} mm</td>
                <td className="py-2 text-slate-300">{w.temperature_c}°C</td>
                <td className="py-2 text-slate-300">{w.humidity_pct}%</td>
                <td className="py-2">
                  {w.is_simulated ? (
                    <span className="text-[9px] bg-amber-950 text-amber-300 border border-amber-800 px-1.5 py-0.5 rounded font-medium">
                      SIMULATED
                    </span>
                  ) : (
                    <span className="text-[9px] bg-emerald-950 text-emerald-300 border border-emerald-800 px-1.5 py-0.5 rounded font-medium">
                      LIVE
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
