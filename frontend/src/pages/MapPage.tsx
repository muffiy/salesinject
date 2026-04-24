import { useState, useEffect } from 'react';
import { GlobalMap } from '../components/Map';
import type { MapDataPoint } from '../components/DeckGLMap';

export function MapPage() {
  const [data, setData] = useState<MapDataPoint[]>([]);

  useEffect(() => {
    // Simulated live targets
    setData([
      { id: '1', name: 'TARGET ALPHA', address: 'New York', lon: -74.006, lat: 40.7128, type: 'bounty', status: 'active', extraData: { bounty: 500, risk: 'HIGH' } },
      { id: '2', name: 'MERC OUTPOST', address: 'London', lon: -0.1276, lat: 51.5072, type: 'agent', status: 'idle', extraData: { agents: 12, status: 'STANDBY' } },
      { id: '3', name: 'TARGET BETA', address: 'Tokyo', lon: 139.6917, lat: 35.6895, type: 'bounty', status: 'active', extraData: { bounty: 1200, risk: 'EXTREME' } }
    ]);
  }, []);

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', zIndex: 0, background: 'var(--war-black)' }}>
      <GlobalMap data={data} />
      <div style={{ position: 'absolute', top: '24px', left: '24px', zIndex: 10, pointerEvents: 'none' }}>
        <h1 className="section-title" style={{ fontSize: '32px', color: 'var(--war-cyan)', textShadow: '0 0 20px rgba(0,245,255,0.5)' }}>GLOBAL WAR ROOM</h1>
        <div className="label" style={{ color: 'white', background: 'var(--war-red)', display: 'inline-block', padding: '4px 8px' }}>LIVE TARGET TRACKING</div>
      </div>
    </div>
  );
}
