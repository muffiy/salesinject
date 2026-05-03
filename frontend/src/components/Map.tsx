import { DeckGLMap } from './DeckGLMap';
import type { MapDataPoint } from './DeckGLMap';

interface GlobalMapProps {
  data: MapDataPoint[];
  selectedId?: string | null;
  onMarkerClick?: (info: MapDataPoint) => void;
  showGlobe?: boolean;
}

export function GlobalMap({ data, selectedId, onMarkerClick, showGlobe }: GlobalMapProps) {
  return (
    <DeckGLMap
      data={data}
      selectedId={selectedId}
      onMarkerClick={onMarkerClick}
      showGlobe={showGlobe}
    />
  );
}
