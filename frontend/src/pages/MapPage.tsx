import React, { useState, useEffect } from 'react';
import DeckGLMap from '../components/DeckGLMap';
import GenZOverlay from '../components/GenZOverlay';
import { getLatestScoutReport, getOffers } from '../services/api';

export default function MapPage() {
  const [mapData, setMapData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const combinedData: any[] = [];
        
        // 1. Load active offers
        try {
          const offers = await getOffers();
          const offerPoints = offers.map((o: any) => ({
            coordinates: [o.lon, o.lat],
            name: o.title,
            discount: o.discount_value > 0 ? `${o.discount_value}%` : null,
            bounty: o.bounty_value > 0 ? `${o.bounty_value} TND` : null,
            type: 'offer',
            id: o.id
          }));
          combinedData.push(...offerPoints);
        } catch (err) {
          console.error("Failed to load offers:", err);
        }

        // 2. Load latest scout report influencers
        try {
          const report = await getLatestScoutReport();
          if (report && report.map_data) {
             combinedData.push(...report.map_data);
          }
        } catch (err) {
          console.error("Failed to load scout report:", err);
        }

        setMapData(combinedData);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  return (
    <div className="relative w-screen h-screen bg-[var(--war-black)]">
      {loading ? (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-[var(--war-black)] text-[var(--war-cyan)] font-mono">
          <div className="animate-pulse">Loading Map Data...</div>
        </div>
      ) : null}
      
      <DeckGLMap data={mapData} />
      <GenZOverlay />
      
      {/* 
        Optional: To show PaperclipSidebar if you want it overlayed on the map,
        you could add a toggle state to render it here floating over the map.
        The UI uses GenZOverlay for standard nav right now.
      */}
    </div>
  );
}
