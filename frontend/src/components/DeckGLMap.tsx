import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

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

const TYPE_COLORS: Record<string, string> = {
  agent: '#8b5cf6',
  influencer: '#ec4899',
  brand: '#00f5ff',
  business: '#00ff88',
  bounty: '#ff3366',
  event: '#ffd60a',
  ad: '#ff006e',
  hotspot: '#ff8800',
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

function makeIcon(point: MapDataPoint, selected: boolean) {
  const color = TYPE_COLORS[point.type] ?? '#6c63ff';
  const icon = TYPE_ICONS[point.type] ?? '📍';
  const size = selected ? 44 : 34;
  const html = `<div style="
    width:${size}px;height:${size}px;
    background:${color}22;
    border:2px solid ${color};
    border-radius:50%;
    display:flex;align-items:center;justify-content:center;
    font-size:${selected ? 18 : 14}px;
    box-shadow:0 0 ${selected ? 16 : 8}px ${color}88;
    cursor:pointer;">${icon}</div>`;
  return L.divIcon({ html, className: '', iconSize: [size, size], iconAnchor: [size / 2, size / 2] });
}

export function DeckGLMap({ data, selectedId, onMarkerClick }: DeckGLMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const markersRef = useRef<L.Marker[]>([]);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = L.map(containerRef.current, {
      center: [20, 0],
      zoom: 2,
      zoomControl: false,
      attributionControl: false,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      subdomains: ['a', 'b', 'c'],
    }).addTo(map);

    // Dark overlay to match the app theme
    const darkPane = map.createPane('dark-overlay');
    darkPane.style.zIndex = '200';
    darkPane.style.pointerEvents = 'none';
    L.imageOverlay(
      'data:image/gif;base64,R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs=',
      [[-90, -180], [90, 180]],
      { opacity: 0, pane: 'dark-overlay' }
    ).addTo(map);

    L.control.zoom({ position: 'bottomright' }).addTo(map);
    L.control.attribution({ position: 'bottomright', prefix: '© OSM' }).addTo(map);

    mapRef.current = map;

    // Force Leaflet to recalculate size after mount
    const t = setTimeout(() => { map.invalidateSize(); }, 100);

    return () => {
      clearTimeout(t);
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Sync markers when data or selectedId changes
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    data.forEach((point) => {
      const marker = L.marker([point.lat, point.lon], {
        icon: makeIcon(point, selectedId === point.id),
      });

      marker.bindTooltip(
        `<b>${point.name}</b><br/><span style="color:${TYPE_COLORS[point.type] ?? '#fff'}">${point.type.toUpperCase()}</span>${point.value ? ` · $${point.value}` : ''}`,
        { direction: 'top', offset: [0, -8] }
      );

      if (onMarkerClick) {
        marker.on('click', () => onMarkerClick(point));
      }

      marker.addTo(map);
      markersRef.current.push(marker);
    });
  }, [data, selectedId, onMarkerClick]);

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', minHeight: '400px', background: '#1a1a2e' }}>
      {/* Leaflet fills entire area */}
      <div ref={containerRef} style={{ position: 'absolute', inset: 0 }} />

      {/* Signal count badge */}
      <div style={{
        position: 'absolute', top: 8, right: 8, zIndex: 1000,
        background: 'rgba(0,0,0,0.7)',
        backdropFilter: 'blur(8px)',
        border: '1px solid rgba(255,255,255,0.15)',
        borderRadius: '20px',
        padding: '4px 10px',
        fontSize: '11px',
        fontFamily: 'monospace',
        color: '#00f5ff',
        fontWeight: 700,
        letterSpacing: '0.05em',
      }}>
        {data.length} SIGNALS
      </div>

      <style>{`
        .leaflet-container { background: #1a1a2e !important; }
        .leaflet-tile { filter: invert(1) hue-rotate(180deg) brightness(0.85) saturate(0.6); }
        .leaflet-control-attribution { font-size: 9px !important; opacity: 0.4 !important; }
      `}</style>
    </div>
  );
}
