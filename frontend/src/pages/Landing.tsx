import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Landing() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  return (
    <div className="h-screen w-screen flex flex-col items-center justify-center bg-[var(--war-black)] text-white overflow-hidden relative">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-[rgba(255,42,95,0.15)] via-[var(--war-black)] to-[var(--war-black)] z-0"></div>
      
      <div className="z-10 flex flex-col items-center max-w-md text-center px-6">
        <h1 className="text-5xl font-bold mb-4 text-gradient font-mono">SALESINJECT</h1>
        <p className="text-gray-400 mb-8 text-lg">
          Turn everyday content into viral campaigns. Claim bounties, conquer the map.
        </p>
        
        {isAuthenticated ? (
          <button 
            onClick={() => navigate('/app/map')}
            className="w-full py-4 rounded-xl bg-[var(--war-pink)] text-white font-bold text-lg shadow-neon-primary transition-transform hover:scale-105 active:scale-95"
          >
            ENTER WAR MAP
          </button>
        ) : (
          <button 
            onClick={() => alert("Please open inside Telegram")}
            className="w-full py-4 rounded-xl bg-gray-800 text-gray-300 font-bold text-lg"
          >
            OPEN IN TELEGRAM
          </button>
        )}
      </div>
    </div>
  );
}
