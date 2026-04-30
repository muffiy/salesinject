import React from 'react';
import GenZOverlay from '../components/GenZOverlay';

export default function Dashboard() {
  return (
    <div className="h-screen w-screen bg-[var(--war-black)] text-white overflow-y-auto pb-24">
      <div className="p-6">
        <h1 className="text-3xl font-bold font-mono text-gradient mb-8">DASHBOARD</h1>
        
        <div className="grid grid-cols-2 gap-4 mb-8">
          <div className="glass-panel p-5 rounded-2xl border-l-4 border-[var(--war-cyan)]">
            <p className="text-gray-400 text-sm">TOTAL EARNINGS</p>
            <p className="text-2xl font-bold">1,450 TND</p>
          </div>
          <div className="glass-panel p-5 rounded-2xl border-l-4 border-[var(--war-pink)]">
            <p className="text-gray-400 text-sm">ACTIVE MISSIONS</p>
            <p className="text-2xl font-bold">3</p>
          </div>
        </div>
        
        <h2 className="text-xl font-bold mb-4 border-b border-gray-800 pb-2">Recent Intel</h2>
        <div className="space-y-4">
          <div className="glass-panel p-4 rounded-xl flex items-center justify-between">
            <div>
              <p className="font-bold">KFC Lac 2 - Promo</p>
              <p className="text-sm text-gray-400">Claimed 2 hours ago</p>
            </div>
            <div className="text-[var(--war-cyan)] font-bold">+ 150 TND</div>
          </div>
        </div>
      </div>
      <GenZOverlay />
    </div>
  );
}
