import React from 'react';
import DeckGL from '@deck.gl/react';
import { ScatterplotLayer, TextLayer } from '@deck.gl/layers';
import Map from 'react-map-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

const INITIAL_VIEW_STATE = {
  longitude: 10.1815, // Tunis
  latitude: 36.8065,
  zoom: 12,
  pitch: 45,
  bearing: 0
};

export default function DeckGLMap({ data }: { data: any[] }) {
  const layers = [
    new ScatterplotLayer({
      id: 'influencer-bubbles',
      data,
      getPosition: d => d.coordinates,
      getFillColor: d => d.type === 'influencer' ? [255, 42, 95, 200] : [0, 240, 255, 200],
      getRadius: d => d.type === 'influencer' ? Math.max(50, (d.followers || 1000) / 100) : 150,
      pickable: true,
      onClick: (info) => console.log(info.object)
    }),
    new TextLayer({
      id: 'text-layer',
      data,
      getPosition: d => d.coordinates,
      getText: d => d.name,
      getSize: 16,
      getColor: [255, 255, 255],
      getPixelOffset: [0, -20]
    })
  ];

  return (
    <DeckGL
      initialViewState={INITIAL_VIEW_STATE}
      controller={true}
      layers={layers}
    >
      <Map
        mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
      />
    </DeckGL>
  );
}
