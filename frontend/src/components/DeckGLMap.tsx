import { useState } from 'react';
import DeckGL from '@deck.gl/react';
import { ScatterplotLayer, TextLayer } from '@deck.gl/layers';
import { Map, MapProvider, Marker } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
import { GenZMarkerBadge } from './GenZOverlay';

export interface MapDataPoint {
  id: string;
  name: string;
  lat: number;
  lon: number;
  type: 'agent' | 'ad' | 'business' | 'bounty' | 'influencer' | 'brand' | 'event' | 'hotspot';
  status?: string;
  address?: string;
  category?: string;
  image?: string;
  value?: number;
  extraData?: Record<string, any>;
}

interface DeckGLMapProps {
  data: MapDataPoint[];
  selectedId?: string | null;
  onMarkerClick?: (info: MapDataPoint) => void;
  showGlobe?: boolean;
}

const DARK_MAP_STYLE = {
  version: 8,
  sources: {
    carto: {
      type: 'raster',
      tiles: ['https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'],
      tileSize: 256,
      attribution: '&copy; CARTO',
    },
  },
  layers: [{ id: 'carto', type: 'raster', source: 'carto', minzoom: 0, maxzoom: 19 }],
};

const TYPE_COLORS: Record<string, [number, number, number]> = {
  agent: [139, 92, 246],       // purple
  influencer: [236, 72, 153],  // pink
  brand: [0, 245, 255],        // cyan
  business: [0, 255, 136],     // green
  bounty: [255, 51, 102],      // red
  event: [255, 214, 10],       // yellow
  ad: [255, 0, 110],           // magenta
  hotspot: [255, 136, 0],      // orange
};

const TYPE_ICONS: Record<string, string> = {
  agent: '🤖',
  influencer: '⭐',
  brand: '🏢',
  business: '💼',
  bounty: '🎯',
  event: '📅',
  ad: '📢',
  hotspot: '🔥',
};

const INITIAL_VIEW_STATE = {
  longitude: 0,
  latitude: 20,
  zoom: 1.5,
  pitch: 0,
  bearing: 0,
};

export function DeckGLMap({ data, selectedId, onMarkerClick, showGlobe }: DeckGLMapProps) {
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);

  // Marker layer — colored circles
  const scatterLayer = new ScatterplotLayer({
    id: 'scatter-layer',
    data,
    pickable: true,
    opacity: 0.85,
    stroked: true,
    filled: true,
    radiusScale: 6,
    radiusMinPixels: 5,
    radiusMaxPixels: 18,
    lineWidthMinPixels: 1.5,
    getPosition: (d: MapDataPoint) => [d.lon, d.lat],
    getFillColor: (d: MapDataPoint) => TYPE_COLORS[d.type] ?? [108, 99, 255],
    getLineColor: [255, 255, 255],
    getRadius: (d: MapDataPoint) => (selectedId === d.id ? 250000 : 100000),
    onClick: (info: any) => {
      if (info.object && onMarkerClick) onMarkerClick(info.object);
    },
  });

  // Label layer — show names for selected or high-value points
  const textLayer = new TextLayer({
    id: 'text-layer',
    data: data.filter((d) => selectedId === d.id || (d.value && d.value > 500)),
    pickable: false,
    getPosition: (d: MapDataPoint) => [d.lon, d.lat],
    getText: (d: MapDataPoint) => d.name,
    getSize: 12,
    getAngle: 0,
    getTextAnchor: 'middle',
    getAlignmentBaseline: 'bottom',
    getPixelOffset: [0, -18],
    getColor: [255, 255, 255],
    fontFamily: 'JetBrains Mono, monospace',
    fontWeight: 'bold',
  });

  const layers = [scatterLayer, textLayer];

  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        height: '100%',
        background: 'var(--si-surface)',
        borderRadius: '0px',
        border: '1px solid var(--si-border)',
        overflow: 'hidden',
      }}
    >
      {/* Header bar */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          padding: '14px 20px',
          background: 'rgba(10, 10, 10, 0.85)',
          backdropFilter: 'blur(16px)',
          borderBottom: '1px solid var(--si-border)',
          zIndex: 10,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <h3
          style={{
            margin: 0,
            fontSize: '14px',
            fontWeight: '800',
            fontFamily: 'var(--font-display)',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            color: 'var(--war-cyan)',
          }}
        >
          🌍 {showGlobe ? '3D Globe View' : 'Global Live Monitor'}
        </h3>
        <span
          style={{
            fontSize: '11px',
            fontFamily: 'var(--font-mono)',
            color: 'var(--si-muted)',
            fontWeight: 600,
          }}
        >
          {data.length} SIGNALS ACTIVE
        </span>
      </div>

      {/* DeckGL Map */}
      <DeckGL
        viewState={viewState}
        onViewStateChange={({ viewState: vs }: any) => setViewState(vs)}
        controller={{ touchRotate: true, keyboard: true }}
        layers={layers}
        getTooltip={(info: any) => {
          if (!info.object) return null;
          const obj = info.object as MapDataPoint;
          return {
            html: `<div style="font-family:var(--font-mono);font-size:11px;padding:4px 8px;">
              <b>${obj.name}</b><br/>
              <span style="color:var(--war-cyan)">${obj.type.toUpperCase()}</span>
              ${obj.value ? ` · $${obj.value}` : ''}
            </div>`,
          };
        }}
      >
        <MapProvider>
          <Map reuseMaps mapStyle={DARK_MAP_STYLE as any} />
        </MapProvider>
      </DeckGL>

      {/* Gen-Z HTML markers rendered on top (react-map-gl Marker components) */}
      {data.slice(0, 20).map((d) => (
        <Marker
          key={d.id}
          longitude={d.lon}
          latitude={d.lat}
          anchor="center"
          onClick={(e) => {
            e.originalEvent.stopPropagation();
            if (onMarkerClick) onMarkerClick(d);
          }}
          style={{ cursor: 'pointer', zIndex: selectedId === d.id ? 100 : 1 }}
        >
          <GenZMarkerBadge
            label={d.name}
            selected={selectedId === d.id}
            icon={TYPE_ICONS[d.type]}
            color={`rgb(${TYPE_COLORS[d.type]?.join(',')})`}
          />
        </Marker>
      ))}
    </div>
  );
}