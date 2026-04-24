import { useState } from 'react';
import { DeckGLMap, type MapDataPoint } from './DeckGLMap';
import { MapProfileCard } from './UI';

export function GlobalMap({ data }: { data: MapDataPoint[] }) {
  const [selectedObj, setSelectedObj] = useState<MapDataPoint | null>(null);

  return (
    <div style={{ position: 'relative', height: '100%' }}>
      <DeckGLMap 
        data={data} 
        onMarkerClick={(obj) => setSelectedObj(obj as MapDataPoint)} 
      />
      
      {selectedObj && (
        <MapProfileCard 
          data={selectedObj} 
          onClose={() => setSelectedObj(null)} 
        />
      )}
    </div>
  );
}
