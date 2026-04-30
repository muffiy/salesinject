import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Map, LayoutDashboard, Target, Users, UserCircle } from 'lucide-react';

export default function GenZOverlay() {
  const navigate = useNavigate();

  return (
    <div className="absolute inset-0 pointer-events-none flex flex-col justify-between p-4 z-10">
      <div className="flex justify-between items-start pointer-events-auto">
        <div className="glass-panel rounded-2xl p-4 flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-[var(--war-pink)] to-[var(--war-purple)] flex items-center justify-center font-bold text-white shadow-neon-primary">
            @
          </div>
          <div>
            <h2 className="font-bold text-lg text-white">Tunis War Room</h2>
            <p className="text-xs text-[var(--war-cyan)]">20 active missions</p>
          </div>
        </div>
      </div>

      <div className="flex justify-center mb-6 pointer-events-auto">
        <div className="glass-panel rounded-full px-6 py-3 flex space-x-8 shadow-glass">
          <button onClick={() => navigate('/app/map')} className="text-white hover:text-[var(--war-pink)] transition-colors"><Map /></button>
          <button onClick={() => navigate('/app/dashboard')} className="text-gray-400 hover:text-[var(--war-pink)] transition-colors"><LayoutDashboard /></button>
          <button onClick={() => navigate('/app/tasks')} className="text-gray-400 hover:text-[var(--war-cyan)] transition-colors"><Target /></button>
          <button onClick={() => navigate('/app/agents')} className="text-gray-400 hover:text-[var(--war-purple)] transition-colors"><Users /></button>
          <button onClick={() => navigate('/app/profile')} className="text-gray-400 hover:text-[var(--war-pink)] transition-colors"><UserCircle /></button>
        </div>
      </div>
    </div>
  );
}
