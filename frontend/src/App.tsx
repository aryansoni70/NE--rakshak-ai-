import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { KPICards } from './components/KPICards';
import { MapView } from './components/MapView';
import { DigitalTwinPanel } from './components/DigitalTwinPanel';
import { RouteOptimizerPanel } from './components/RouteOptimizerPanel';
import { FleetTelemetryPanel } from './components/FleetTelemetryPanel';
import { WeatherPanel } from './components/WeatherPanel';
import { FieldIncidentModal } from './components/FieldIncidentModal';
import { AlertTicker } from './components/AlertTicker';
import { api } from './services/api';
import {
  RoadSegment,
  VehicleTelemetry,
  WeatherSnapshot,
  CriticalFacility,
  AlertItem,
  SimulationImpact,
  RouteAlternative,
  RouteOptimizationResponse
} from './types';
import { Cpu, Navigation, Truck, CloudRain } from 'lucide-react';

export function App() {
  const [roads, setRoads] = useState<RoadSegment[]>([]);
  const [vehicles, setVehicles] = useState<VehicleTelemetry[]>([]);
  const [weather, setWeather] = useState<WeatherSnapshot[]>([]);
  const [facilities, setFacilities] = useState<CriticalFacility[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [simulationImpact, setSimulationImpact] = useState<SimulationImpact | null>(null);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'TWIN' | 'ROUTES' | 'FLEET' | 'WEATHER'>('TWIN');
  const [isIncidentModalOpen, setIsIncidentModalOpen] = useState<boolean>(false);
  const [selectedRouteOverlays, setSelectedRouteOverlays] = useState<RouteAlternative[]>([]);
  const [highlightedRoadId, setHighlightedRoadId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Initial Load
  const fetchAllData = async () => {
    setIsLoading(true);
    try {
      const [roadsData, weatherData, vehiclesData, alertsData, facilitiesData] = await Promise.all([
        api.getRoadsRisk(),
        api.getWeather(),
        api.getVehicles(),
        api.getAlerts(),
        api.getFacilities()
      ]);

      setRoads(roadsData.roads);
      setWeather(weatherData);
      setVehicles(vehiclesData);
      setAlerts(alertsData);
      setFacilities(facilitiesData);
    } catch (err) {
      console.error('Error loading mission data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();

    // WebSocket live telemetry feed
    let ws: WebSocket | null = null;
    try {
      ws = new WebSocket('ws://localhost:8000/ws/live');
      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'TELEMETRY_PULSE') {
            if (msg.vehicles) setVehicles(msg.vehicles);
            if (msg.active_alerts) setAlerts(msg.active_alerts);
          }
        } catch (e) {
          console.error(e);
        }
      };
    } catch (e) {
      console.warn('WebSocket connection not ready:', e);
    }

    return () => {
      if (ws) ws.close();
    };
  }, []);

  // Handlers
  const handleRefreshWeather = async () => {
    await api.refreshRoadsRisk();
    await fetchAllData();
  };

  const handleSimulateRainfall = async (region: string, mm: number) => {
    setIsLoading(true);
    try {
      const impact = await api.simulateRainfall(region, mm);
      setSimulationImpact(impact);
      setIsSimulating(true);
      await fetchAllData();
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSimulateBlockage = async (roadId: string, reason: string) => {
    setIsLoading(true);
    try {
      const impact = await api.simulateRoadBlock(roadId, reason);
      setSimulationImpact(impact);
      setIsSimulating(true);
      setHighlightedRoadId(roadId);
      await fetchAllData();
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetSimulation = async () => {
    setIsLoading(true);
    try {
      await api.resetSimulation();
      setSimulationImpact(null);
      setIsSimulating(false);
      setHighlightedRoadId(null);
      setSelectedRouteOverlays([]);
      await fetchAllData();
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCalculateRoute = async (
    origin: string,
    dest: string,
    cargo: string,
    urgency: string
  ): Promise<RouteOptimizationResponse> => {
    return api.calculateRoute(origin, dest, cargo, urgency);
  };

  const handleSubmitIncident = async (data: any) => {
    await api.submitIncident(data);
    await fetchAllData();
  };

  const blockedCount = roads.filter((r) => r.is_blocked).length;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Header */}
      <Header
        onRefreshWeather={handleRefreshWeather}
        onResetSimulation={handleResetSimulation}
        onOpenIncidentModal={() => setIsIncidentModalOpen(true)}
        isSimulating={isSimulating}
        activeAlertCount={alerts.length}
        blockedCount={blockedCount}
        isLoading={isLoading}
      />

      {/* KPI Stats Banner */}
      <KPICards
        roads={roads}
        vehicles={vehicles}
        weather={weather}
        facilities={facilities}
      />

      {/* Main Workspace Layout */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-4 p-4 md:p-6 overflow-hidden">
        {/* Left / Center GIS Map (7 cols) */}
        <div className="lg:col-span-7 flex flex-col min-h-[550px]">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                North Eastern Tactical GIS Corridor Visualizer
              </h2>
            </div>
            <span className="text-[11px] text-slate-400">
              Interactive Nodes & Highway LineStrings
            </span>
          </div>

          <div className="flex-1">
            <MapView
              roads={roads}
              vehicles={vehicles}
              facilities={facilities}
              selectedRoutes={selectedRouteOverlays}
              highlightedRoadId={highlightedRoadId}
              onSelectRoad={(r) => setHighlightedRoadId(r.id)}
            />
          </div>
        </div>

        {/* Right Tactical Mission Console (5 cols) */}
        <div className="lg:col-span-5 flex flex-col space-y-3">
          {/* Tactical Tab Navigation */}
          <div className="grid grid-cols-4 gap-1 bg-slate-900/90 p-1 rounded-lg border border-slate-800">
            <button
              onClick={() => setActiveTab('TWIN')}
              className={`flex items-center justify-center space-x-1 py-1.5 rounded text-xs font-semibold transition cursor-pointer ${
                activeTab === 'TWIN'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Cpu className="w-3.5 h-3.5" />
              <span>Digital Twin</span>
            </button>

            <button
              onClick={() => setActiveTab('ROUTES')}
              className={`flex items-center justify-center space-x-1 py-1.5 rounded text-xs font-semibold transition cursor-pointer ${
                activeTab === 'ROUTES'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Navigation className="w-3.5 h-3.5" />
              <span>Routing</span>
            </button>

            <button
              onClick={() => setActiveTab('FLEET')}
              className={`flex items-center justify-center space-x-1 py-1.5 rounded text-xs font-semibold transition cursor-pointer ${
                activeTab === 'FLEET'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Truck className="w-3.5 h-3.5" />
              <span>Fleet</span>
            </button>

            <button
              onClick={() => setActiveTab('WEATHER')}
              className={`flex items-center justify-center space-x-1 py-1.5 rounded text-xs font-semibold transition cursor-pointer ${
                activeTab === 'WEATHER'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <CloudRain className="w-3.5 h-3.5" />
              <span>Weather</span>
            </button>
          </div>

          {/* Active Tab Panel Body */}
          <div className="flex-1 overflow-y-auto max-h-[620px] pr-1">
            {activeTab === 'TWIN' && (
              <DigitalTwinPanel
                onSimulateRainfall={handleSimulateRainfall}
                onSimulateBlockage={handleSimulateBlockage}
                onReset={handleResetSimulation}
                isSimulating={isSimulating}
                impact={simulationImpact}
                roads={roads}
                isLoading={isLoading}
              />
            )}

            {activeTab === 'ROUTES' && (
              <RouteOptimizerPanel
                onCalculateRoute={handleCalculateRoute}
                onSelectRouteOverlay={(routes) => setSelectedRouteOverlays(routes)}
                isLoading={isLoading}
              />
            )}

            {activeTab === 'FLEET' && (
              <FleetTelemetryPanel vehicles={vehicles} />
            )}

            {activeTab === 'WEATHER' && (
              <WeatherPanel weather={weather} />
            )}
          </div>
        </div>
      </main>

      {/* Field Officer Incident Submission Modal */}
      <FieldIncidentModal
        isOpen={isIncidentModalOpen}
        onClose={() => setIsIncidentModalOpen(false)}
        roads={roads}
        onSubmitIncident={handleSubmitIncident}
      />

      {/* Bottom Live Alert Ticker */}
      <AlertTicker alerts={alerts} />
    </div>
  );
}

export default App;
