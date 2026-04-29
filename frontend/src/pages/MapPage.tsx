import { useState, useCallback } from 'react';
import { GlobalMap } from '../components/Map';
import type { MapDataPoint } from '../components/DeckGLMap';
import {
  GenZFilterBar,
  GenZFloatingControls,
  GenZBottomBar,
  GenZBottomSheet,
} from '../components/GenZOverlay';

// ─── Demo data: influencers, brands, hotspots ──────────────────────

const DEMO_DATA: MapDataPoint[] = [
  { id: '1', name: 'ALPHA MERC', lon: -74.006, lat: 40.7128, type: 'agent', value: 1200, status: 'active', image: 'https://i.pravatar.cc/80?img=1', extraData: { rating: 'ELITE', missions: 47 } },
  { id: '2', name: 'NOVA OUTPOST', lon: -0.1276, lat: 51.5072, type: 'agent', value: 800, status: 'standby', image: 'https://i.pravatar.cc/80?img=2', extraData: { rating: 'VETERAN', missions: 23 } },
  { id: '3', name: 'TOKYO DRIFT', lon: 139.6917, lat: 35.6895, type: 'bounty', value: 2500, status: 'hot', image: 'https://i.pravatar.cc/80?img=3', extraData: { risk: 'EXTREME', bounty: 2500 } },
  { id: '4', name: 'CRYPTO KING', lon: -118.2437, lat: 34.0522, type: 'influencer', value: 5000, status: 'trending', image: 'https://i.pravatar.cc/80?img=4', extraData: { followers: '2.4M', niche: 'DeFi' } },
  { id: '5', name: 'FASHION ICON', lon: 2.3522, lat: 48.8566, type: 'influencer', value: 3500, status: 'active', image: 'https://i.pravatar.cc/80?img=5', extraData: { followers: '5.1M', niche: 'Luxury' } },
  { id: '6', name: 'NIKE HQ', lon: -122.6784, lat: 45.5152, type: 'brand', value: 8000, status: 'partner', image: 'https://i.pravatar.cc/80?img=6', extraData: { budget: '2M', category: 'Sportswear' } },
  { id: '7', name: 'SAMSUNG LAB', lon: 127.0018, lat: 37.5642, type: 'brand', value: 6500, status: 'active', image: 'https://i.pravatar.cc/80?img=7', extraData: { budget: '1.5M', category: 'Electronics' } },
  { id: '8', name: 'DUBAI EXPO', lon: 55.2708, lat: 25.2048, type: 'event', value: 4200, status: 'upcoming', image: 'https://i.pravatar.cc/80?img=8', extraData: { attendees: '50K', date: '2026-05-15' } },
  { id: '9', name: 'BERLIN TECH', lon: 13.405, lat: 52.52, type: 'event', value: 3800, status: 'live', image: 'https://i.pravatar.cc/80?img=9', extraData: { attendees: '12K', date: '2026-04-30' } },
  { id: '10', name: 'SAO PAULO', lon: -46.6333, lat: -23.5505, type: 'hotspot', value: 900, status: 'rising', image: 'https://i.pravatar.cc/80?img=10', extraData: { trend: '+340%', category: 'Emerging' } },
  { id: '11', name: 'MUMBAI HUB', lon: 72.8777, lat: 19.076, type: 'hotspot', value: 1100, status: 'rising', image: 'https://i.pravatar.cc/80?img=11', extraData: { trend: '+210%', category: 'Growth' } },
  { id: '12', name: 'SYDNEY CREW', lon: 151.2093, lat: -33.8688, type: 'agent', value: 600, status: 'idle', image: 'https://i.pravatar.cc/80?img=12', extraData: { rating: 'ROOKIE', missions: 5 } },
];

// Filter options
const FILTER_OPTIONS = [
  { id: 'all', icon: '🌐', label: 'All' },
  { id: 'influencer', icon: '⭐', label: 'Influencers', count: 2 },
  { id: 'brand', icon: '🏢', label: 'Brands', count: 2 },
  { id: 'agent', icon: '🤖', label: 'Agents', count: 3 },
  { id: 'bounty', icon: '🎯', label: 'Bounties', count: 1 },
  { id: 'hotspot', icon: '🔥', label: 'Hotspots', count: 2 },
];

const CATEGORY_OPTIONS = [
  { id: 'all', icon: '🌐', label: 'All' },
  { id: 'live', icon: '🟢', label: 'Live' },
  { id: 'trending', icon: '📈', label: 'Trending' },
  { id: 'high-value', icon: '💎', label: 'High Value' },
];


const SHEET_ACTIONS = [
  { id: 'connect', icon: '🤝', label: 'Connect' },
  { id: 'track', icon: '📡', label: 'Track' },
  { id: 'analyze', icon: '📊', label: 'Analyze' },
];

export function MapPage() {
  const [data] = useState<MapDataPoint[]>(DEMO_DATA);
  const [selectedId, _setSelectedId] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState('all');
  const [activeCategory, setActiveCategory] = useState('all');
  const [viewMode, setViewMode] = useState<'flat' | 'globe'>('flat');
  const [sheetCollapsed, setSheetCollapsed] = useState(false);
  const [sheetAction, setSheetAction] = useState('connect');

  const selected = data.find((d) => d.id === selectedId) ?? null;

  // Filter data
  const filteredData =
    activeFilter === 'all' ? data : data.filter((d) => d.type === activeFilter);

  
  const handleGlobeToggle = useCallback(() => {
    setViewMode((prev) => (prev === 'globe' ? 'flat' : 'globe'));
  }, []);

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', zIndex: 0, background: 'var(--war-black)' }}>
      {/* 3D Globe View (simulated with perspective hint) or Flat Map */}
      <div
        style={{
          width: '100%',
          height: '100%',
          perspective: viewMode === 'globe' ? '1200px' : 'none',
          transition: 'perspective 0.5s ease',
        }}
      >
        <div
          style={{
            width: '100%',
            height: '100%',
            transform: viewMode === 'globe' ? 'rotateX(5deg) scale(1.02)' : 'none',
            transformOrigin: 'center center',
            transition: 'transform 0.5s ease',
          }}
        >
          <GlobalMap data={filteredData} />
        </div>
      </div>

      {/* Gen-Z Top Filter Bar */}
      <GenZFilterBar options={FILTER_OPTIONS} active={activeFilter} onChange={setActiveFilter} />

      {/* Gen-Z Floating Controls */}
      <GenZFloatingControls
        actions={[
          { id: 'search', icon: '🔍', label: 'Search', onClick: () => {} },
          { id: 'globe', icon: viewMode === 'globe' ? '🗺️' : '🌐', label: viewMode === 'globe' ? 'Flat View' : '3D Globe', onClick: handleGlobeToggle, active: viewMode === 'globe' },
          { id: 'layers', icon: '📊', label: 'Data Layers', onClick: () => {} },
        ]}
      />

      {/* Gen-Z Bottom Action Bar */}
      <GenZBottomBar options={CATEGORY_OPTIONS} active={activeCategory} onChange={setActiveCategory} />

      {/* View mode indicator */}
      <div className="genz-view-indicator">
        {viewMode === 'globe' ? '🌐 3D GLOBE ACTIVE' : '🗺️ FLAT MAP ACTIVE'}
      </div>

      {/* Gen-Z Bottom Sheet */}
      <GenZBottomSheet
        title={selected ? selected.name : 'Explore the Network'}
        actions={SHEET_ACTIONS}
        activeAction={sheetAction}
        onActionChange={setSheetAction}
        triggerLabel={selected ? `ENGAGE ${selected.name}` : 'SELECT A SIGNAL'}
        onTrigger={() => {
          if (selected) {
            alert(`Engaging: ${selected.name} (${selected.type}) · Value: $${selected.value}`);
          }
        }}
        collapsed={sheetCollapsed}
        onToggle={() => setSheetCollapsed(!sheetCollapsed)}
      />
    </div>
  );
}