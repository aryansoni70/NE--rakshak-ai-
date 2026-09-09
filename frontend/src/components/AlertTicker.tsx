import React from 'react';
import { AlertCircle, ShieldAlert, Info } from 'lucide-react';
import { AlertItem } from '../types';

interface AlertTickerProps {
  alerts: AlertItem[];
}

export const AlertTicker: React.FC<AlertTickerProps> = ({ alerts }) => {
  if (alerts.length === 0) return null;

  return (
    <div className="bg-slate-900 border-t border-slate-800 px-6 py-2 flex items-center justify-between text-xs z-40">
      <div className="flex items-center space-x-2 text-rose-400 font-bold uppercase tracking-wider flex-shrink-0">
        <ShieldAlert className="w-4 h-4 animate-pulse" />
        <span>Live Warnings ({alerts.length}):</span>
      </div>

      <div className="overflow-hidden whitespace-nowrap ml-4 flex-1">
        <div className="inline-flex space-x-6">
          {alerts.map((alert) => (
            <div key={alert.id} className="inline-flex items-center space-x-1.5 text-slate-300">
              <span
                className={`w-2 h-2 rounded-full ${
                  alert.severity === 'CRITICAL' ? 'bg-rose-500' : alert.severity === 'WARNING' ? 'bg-amber-500' : 'bg-blue-500'
                }`}
              ></span>
              <strong className="text-white font-medium">{alert.title}</strong>
              <span className="text-slate-400">— {alert.message}</span>
              <span className="text-[10px] text-slate-500 font-mono">[{alert.timestamp}]</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
