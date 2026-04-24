import DeckGL from '@deck.gl/react';
import { ScatterplotLayer } from '@deck.gl/layers';
import { Map, MapProvider } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';

export interface MapDataPoint {
  id: string;
  name: string;
  lat: number;
  lon: number;
  type: 'agent' | 'ad' | 'business' | 'bounty';
  status?: string;
  address?: string;
  extraData?: any;
}

interface DeckGLMapProps {
  data: MapDataPoint[];
  onMarkerClick?: (info: any) => void;
}

const INITIAL_VIEW_STATE = {
  longitude: 0,
  latitude: 20,
  zoom: 1.5,
  pitch: 0,
  bearing: 0
};

// Use OpenStreetMap via MapLibre given no API key is assumed
const MAP_STYLE = {
  version: 8,
  sources: {
    osm: {
      type: 'raster',
      tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
      tileSize: 256,
      attribution: '&copy; OpenStreetMap Contributors'
    }
  },
  layers: [
    {
      id: 'osm',
      type: 'raster',
      source: 'osm',
      minzoom: 0,
      maxzoom: 19
    }
  ]
};

export function DeckGLMap({ data, onMarkerClick }: DeckGLMapProps) {

  const scatterLayer = new ScatterplotLayer({
    id: 'scatter-layer',
    data,
    pickable: true,
    opacity: 0.8,
    stroked: true,
    filled: true,
    radiusScale: 6,
    radiusMinPixels: 4,
    radiusMaxPixels: 15,
    lineWidthMinPixels: 1,
    getPosition: (d: MapDataPoint) => [d.lon, d.lat],
    getPoints: (d: MapDataPoint) => [d.lon, d.lat],
    getFillColor: (d: MapDataPoint) => {
      if (d.type === 'agent') return [108, 99, 255]; // si-accent
      if (d.type === 'business') return [0, 229, 160]; // si-green
      return [255, 101, 132]; // fallback pink
    },
    getLineColor: [255, 255, 255],
    getRadius: 100000,
    onClick: info => {
      if (onMarkerClick) onMarkerClick(info.object);
    }
  });

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', background: 'var(--si-surface)', borderRadius: '20px', border: '1px solid var(--si-border)', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, padding: '16px 20px', background: 'rgba(22, 24, 31, 0.8)', borderBottom: '1px solid var(--si-border)', zIndex: 10, display: 'flex', justifyContent: 'space-between', alignItems: 'center', backdropFilter: 'blur(10px)' }}>
        <h3 style={{ margin: 0, fontSize: '15px', fontWeight: '700' }}>🌍 Global Live Monitor</h3>
        <span style={{ fontSize: '12px', color: 'var(--si-muted)' }}>Agents & Activity</span>
      </div>

      <DeckGL
        initialViewState={INITIAL_VIEW_STATE}
        controller={true}
        layers={[scatterLayer]}
        getTooltip={(info) => {
            if (!info.object) return null;
            const obj = info.object as MapDataPoint;
            return `${obj.name} (${obj.type})`;
        }}
      >
        <MapProvider>
            <Map reuseMaps mapStyle={MAP_STYLE as any} />
        </MapProvider>
      </DeckGL>
    </div>
  );
}
