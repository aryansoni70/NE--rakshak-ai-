import React, { useState } from 'react';
import { AlertTriangle, X, Send, MapPin } from 'lucide-react';
import { RoadSegment } from '../types';

interface FieldIncidentModalProps {
  isOpen: boolean;
  onClose: () => void;
  roads: RoadSegment[];
  onSubmitIncident: (data: {
    incident_type: string;
    road_id: string;
    location_desc: string;
    lat: number;
    lng: number;
    severity: string;
    blockage_extent_pct: number;
    reporter_badge: string;
    notes?: string;
  }) => Promise<void>;
}

export const FieldIncidentModal: React.FC<FieldIncidentModalProps> = ({
  isOpen,
  onClose,
  roads,
  onSubmitIncident
}) => {
  if (!isOpen) return null;

  const [incidentType, setIncidentType] = useState<string>('LANDSLIDE');
  const [roadId, setRoadId] = useState<string>(roads[0]?.id || 'RD-TEZ-BHK-02');
  const [locationDesc, setLocationDesc] = useState<string>('Km 38.5 Mountain Cutting near Bhalukpong Gate');
  const [lat, setLat] = useState<number>(27.0125);
  const [lng, setLng] = useState<number>(92.6468);
  const [severity, setSeverity] = useState<string>('CRITICAL');
  const [blockagePct, setBlockagePct] = useState<number>(100);
  const [reporterBadge, setReporterBadge] = useState<string>('NER-FLD-DISPATCH-09');
  const [notes, setNotes] = useState<string>('Massive boulders across both lanes. Mud slurry flowing from upper slope.');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmitIncident({
        incident_type: incidentType,
        road_id: roadId,
        location_desc: locationDesc,
        lat,
        lng,
        severity,
        blockage_extent_pct: blockagePct,
        reporter_badge: reporterBadge,
        notes
      });
      onClose();
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[1000] bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-lg w-full p-6 shadow-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-white">
              Field Officer Geo-Tagged Incident Report
            </h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded transition cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3 text-xs">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-300 font-medium mb-1">Incident Classification</label>
              <select
                value={incidentType}
                onChange={(e) => setIncidentType(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-white focus:outline-none focus:border-blue-500"
              >
                <option value="LANDSLIDE">Major Landslide / Rockfall</option>
                <option value="FLASH_FLOOD">Flash Flood / Road Submersion</option>
                <option value="BRIDGE_DAMAGE">Culvert / Bridge Shear Damage</option>
                <option value="ROAD_EROSION">Slope Subsidence & Sinking Zone</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-1">Corridor Segment</label>
              <select
                value={roadId}
                onChange={(e) => {
                  setRoadId(e.target.value);
                  const selectedRoad = roads.find((r) => r.id === e.target.value);
                  if (selectedRoad && selectedRoad.coordinates.length > 0) {
                    setLat(selectedRoad.coordinates[0][0]);
                    setLng(selectedRoad.coordinates[0][1]);
                  }
                }}
                className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-white focus:outline-none focus:border-blue-500"
              >
                {roads.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-slate-300 font-medium mb-1">Specific Landmark / Location Marker</label>
            <input
              type="text"
              value={locationDesc}
              onChange={(e) => setLocationDesc(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-white focus:outline-none focus:border-blue-500"
              required
            />
          </div>

          <div className="grid grid-cols-3 gap-2">
            <div>
              <label className="block text-slate-300 font-medium mb-1">Latitude</label>
              <input
                type="number"
                step="0.0001"
                value={lat}
                onChange={(e) => setLat(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-white focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-medium mb-1">Longitude</label>
              <input
                type="number"
                step="0.0001"
                value={lng}
                onChange={(e) => setLng(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-white focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-medium mb-1">Blockage %</label>
              <input
                type="number"
                min="10"
                max="100"
                step="10"
                value={blockagePct}
                onChange={(e) => setBlockagePct(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-white focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-300 font-medium mb-1">Severity Level</label>
              <select
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-white focus:outline-none focus:border-blue-500"
              >
                <option value="CRITICAL">CRITICAL (Total Impasse)</option>
                <option value="HIGH">HIGH (Single Lane Passage)</option>
                <option value="MODERATE">MODERATE (Slow Transit)</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-1">Officer Badge ID</label>
              <input
                type="text"
                value={reporterBadge}
                onChange={(e) => setReporterBadge(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-white focus:outline-none focus:border-blue-500"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-slate-300 font-medium mb-1">Ground Notes & Clearance Time Estimate</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={2}
              className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-white focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="flex justify-end space-x-2 pt-3 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded font-medium transition cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex items-center space-x-1.5 px-4 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded font-medium transition cursor-pointer shadow-sm"
            >
              <Send className="w-3.5 h-3.5" />
              <span>{isSubmitting ? 'Submitting & Broadcasting...' : 'Broadcast Incident Alert'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
