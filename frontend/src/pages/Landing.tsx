import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ArrowRight, Map, Bot, Zap, ShieldCheck, Users, Search, Play, Instagram } from 'lucide-react';
import React from 'react';

const AVATARS = [
  { top: '15%', left: '10%', size: 48, score: 8.4, color: 'bg-orange-500' },
  { top: '25%', left: '75%', size: 56, score: 9.2, color: 'bg-pink-500' },
  { top: '65%', left: '15%', size: 40, score: 7.1, color: 'bg-green-500' },
  { top: '70%', left: '80%', size: 64, score: 9.8, color: 'bg-blue-500' },
  { top: '40%', left: '40%', size: 50, score: 8.8, color: 'bg-purple-500' },
  { top: '10%', left: '45%', size: 36, score: 6.5, color: 'bg-yellow-500' },
  { top: '85%', left: '50%', size: 44, score: 7.9, color: 'bg-red-500' },
];

const TRENDING_LISTS = [
  {
    title: 'Tunisian Tech Innovators',
    rating: 4.8,
    count: 13,
    image: 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=500&h=300&fit=crop',
    icon: <Play className="w-5 h-5" />
  },
  {
    title: 'MENA Lifestyle & Fashion',
    rating: 4.9,
    count: 245,
    image: 'https://images.unsplash.com/photo-1483985988355-763728e1935b?w=500&h=300&fit=crop',
    icon: <Instagram className="w-5 h-5" />
  },
  {
    title: 'Maghreb Food Critics',
    rating: 4.7,
    count: 89,
    image: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500&h=300&fit=crop',
    icon: <Instagram className="w-5 h-5" />
  },
  {
    title: 'North African Gamers',
    rating: 4.6,
    count: 156,
    image: 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=500&h=300&fit=crop',
    icon: <Play className="w-5 h-5" />
  }
];

export default function Landing() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  return (
    <div className="w-full min-h-screen bg-[#0A0A0E] text-white selection:bg-[#FF2A5F] selection:text-white pb-20">
      
      {/* ── NAVBAR ── */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass-panel border-b border-white/5 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#FF2A5F] to-[#00F0FF] flex items-center justify-center">
            <Zap className="w-4 h-4 text-white" />
          </div>
          <span className="text-xl font-bold font-mono tracking-wider">SALESINJECT</span>
        </div>
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-400">
          <a href="#map" className="hover:text-white transition-colors">The War Map</a>
          <a href="#agents" className="hover:text-white transition-colors">AI Agents</a>
          <a href="#creators" className="hover:text-white transition-colors">For Creators</a>
        </div>
        <div>
          {isAuthenticated ? (
            <button onClick={() => navigate('/app/map')} className="px-5 py-2 rounded-full bg-white text-black font-bold text-sm hover:bg-gray-200 transition-colors">
              Enter App
            </button>
          ) : (
            <button className="px-5 py-2 rounded-full bg-[#FF2A5F] text-white font-bold text-sm hover:brightness-110 transition-all shadow-[0_0_15px_rgba(255,42,95,0.4)]">
              Book Demo
            </button>
          )}
        </div>
      </nav>

      {/* ── HERO SECTION ── */}
      <section className="relative pt-40 pb-32 px-6 overflow-hidden">
        {/* Dynamic Gradient Background */}
        <div className="absolute inset-0 z-0">
          <div className="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] rounded-full bg-[#B026FF] mix-blend-screen filter blur-[120px] opacity-40 animate-pulse"></div>
          <div className="absolute bottom-[-20%] right-[-10%] w-[60%] h-[60%] rounded-full bg-[#FF2A5F] mix-blend-screen filter blur-[120px] opacity-40"></div>
          <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10 mix-blend-overlay"></div>
        </div>

        <div className="relative z-10 max-w-5xl mx-auto text-center flex flex-col items-center">
          <div className="px-4 py-1.5 rounded-full border border-[#00F0FF]/30 bg-[#00F0FF]/10 text-[#00F0FF] text-xs font-bold uppercase tracking-widest mb-8 inline-flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#00F0FF] animate-ping"></span>
            MENA's #1 Creator Network
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 leading-tight">
            Grow fast with 25K+ MENA creators.<br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00F0FF] via-[#FF2A5F] to-[#B026FF]">
              Trusted by Top Brands.
            </span>
          </h1>
          
          <p className="text-lg md:text-xl text-gray-400 max-w-3xl mb-10 leading-relaxed">
            Stop wasting time on unvetted influencers. Start scaling with performance-driven creators directly on a live 3D map. SalesInject turns everyday content into targeted, viral campaigns.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
            <button onClick={() => navigate('/app/map')} className="px-8 py-4 rounded-full bg-white text-black font-bold text-lg hover:scale-105 transition-transform flex items-center justify-center gap-2">
              Start your campaign today <ArrowRight className="w-5 h-5" />
            </button>
            <button className="px-8 py-4 rounded-full glass-panel text-white font-bold text-lg hover:bg-white/10 transition-colors flex items-center justify-center gap-2">
              <Bot className="w-5 h-5" /> Explore AI Agents
            </button>
          </div>
        </div>
      </section>

      {/* ── CONSTELLATION MAP VISUAL ── */}
      <section className="py-20 relative border-y border-white/5 bg-[#15151C]/50 overflow-hidden" id="map">
        <div className="max-w-6xl mx-auto px-6 relative z-10 text-center">
          <h2 className="text-3xl md:text-5xl font-bold mb-4">Scale end-to-end creator collaborations</h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto mb-16">Visualize market dominance in real-time. Drop bounties, recruit mercenaries, and watch your brand spread across the map.</p>
        </div>

        {/* Floating Avatars Background */}
        <div className="relative h-[400px] max-w-5xl mx-auto">
          {/* Constellation Lines (SVG) */}
          <svg className="absolute inset-0 w-full h-full opacity-20" preserveAspectRatio="none">
            <line x1="10%" y1="15%" x2="40%" y2="40%" stroke="white" strokeWidth="1" strokeDasharray="4 4" />
            <line x1="40%" y1="40%" x2="75%" y2="25%" stroke="white" strokeWidth="1" strokeDasharray="4 4" />
            <line x1="40%" y1="40%" x2="45%" y2="10%" stroke="white" strokeWidth="1" strokeDasharray="4 4" />
            <line x1="40%" y1="40%" x2="50%" y2="85%" stroke="white" strokeWidth="1" strokeDasharray="4 4" />
            <line x1="50%" y1="85%" x2="80%" y2="70%" stroke="white" strokeWidth="1" strokeDasharray="4 4" />
            <line x1="15%" y1="65%" x2="40%" y2="40%" stroke="white" strokeWidth="1" strokeDasharray="4 4" />
          </svg>

          {AVATARS.map((avatar, i) => (
            <div 
              key={i} 
              className="absolute transform -translate-x-1/2 -translate-y-1/2 animate-bounce"
              style={{ top: avatar.top, left: avatar.left, animationDelay: `${i * 0.2}s`, animationDuration: '3s' }}
            >
              <div className="relative">
                <div className={`w-14 h-14 rounded-full border-2 border-[#15151C] overflow-hidden ${avatar.color}`}>
                  <img src={`https://i.pravatar.cc/150?u=${i}`} alt="Avatar" className="w-full h-full object-cover mix-blend-overlay opacity-80" />
                </div>
                <div className="absolute -bottom-2 -right-2 bg-black text-white text-[10px] font-bold px-2 py-0.5 rounded-full border border-white/20 shadow-xl">
                  iScore {avatar.score}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── TRENDING LISTS (CARDS) ── */}
      <section className="py-24 max-w-7xl mx-auto px-6" id="creators">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-4">
          <div>
            <h2 className="text-3xl font-bold mb-2">Trending influencer lists</h2>
            <p className="text-gray-400">Ride the wave with the creators everyone in MENA is talking about.</p>
          </div>
          <button className="px-6 py-2 rounded-full border border-white/20 hover:bg-white/5 font-medium text-sm transition-colors">
            View directory
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {TRENDING_LISTS.map((list, i) => (
            <div key={i} className="bg-[#15151C] border border-white/10 rounded-2xl overflow-hidden hover:border-[#00F0FF]/50 transition-colors group cursor-pointer">
              <div className="h-40 overflow-hidden relative">
                <img src={list.image} alt={list.title} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
                <div className="absolute top-3 right-3 w-8 h-8 rounded-full bg-black/50 backdrop-blur-md flex items-center justify-center">
                  {list.icon}
                </div>
                
                {/* Stacked avatars mimic */}
                <div className="absolute bottom-3 left-3 flex -space-x-2">
                  {[1,2,3,4].map(num => (
                    <img key={num} className="w-8 h-8 rounded-full border-2 border-[#15151C]" src={`https://i.pravatar.cc/100?img=${i*4+num}`} alt="User" />
                  ))}
                  <div className="w-8 h-8 rounded-full border-2 border-[#15151C] bg-[#FF2A5F] flex items-center justify-center text-[10px] font-bold">
                    +{list.count}
                  </div>
                </div>
              </div>
              
              <div className="p-5">
                <h3 className="font-bold text-lg mb-2 line-clamp-2">{list.title} – Connect & Scale</h3>
                <div className="flex items-center gap-2 mb-4">
                  <div className="flex text-yellow-500 text-sm">★★★★★</div>
                  <span className="text-xs text-gray-400">({list.rating})</span>
                </div>
                <div className="flex justify-between items-center text-sm text-gray-400 border-t border-white/10 pt-4">
                  <span className="flex items-center gap-1"><Users className="w-4 h-4"/> {list.count} Creators</span>
                  <span className="flex items-center gap-1"><Search className="w-4 h-4"/> Deep Scan</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── FEATURES SPLIT ── */}
      <section className="py-20 bg-gradient-to-b from-[#15151C] to-[#0A0A0E]" id="agents">
        <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-2 gap-16 items-center">
          <div>
            <div className="w-12 h-12 rounded-xl bg-[#B026FF]/20 flex items-center justify-center mb-6">
              <Bot className="w-6 h-6 text-[#B026FF]" />
            </div>
            <h2 className="text-3xl md:text-4xl font-bold mb-6 leading-tight">
              AI Agents that hunt,<br/>negotiate, and generate.
            </h2>
            <p className="text-gray-400 text-lg mb-8">
              Why manually search for influencers? Deploy an AI Scout to crawl social platforms, rank creators by engagement in specific regions (like Tunis, Dubai, Cairo), and auto-generate tailored ad copy.
            </p>
            <ul className="space-y-4 mb-8">
              <li className="flex items-center gap-3"><ShieldCheck className="w-5 h-5 text-green-500" /> Fraud & Fake Follower Detection</li>
              <li className="flex items-center gap-3"><ShieldCheck className="w-5 h-5 text-green-500" /> Automated Outreach & Deal Flow</li>
              <li className="flex items-center gap-3"><ShieldCheck className="w-5 h-5 text-green-500" /> Telegram Native Mini App</li>
            </ul>
            <button className="px-6 py-3 rounded-full bg-[#B026FF] text-white font-bold hover:brightness-110 transition-all">
              Deploy an Agent
            </button>
          </div>
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-[#B026FF] to-[#FF2A5F] rounded-3xl blur-2xl opacity-30 transform rotate-3"></div>
            <div className="glass-panel border border-white/10 rounded-3xl p-2 relative">
              <img src="https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=800&h=600&fit=crop" alt="Dashboard" className="rounded-2xl opacity-80" />
              {/* Overlay card */}
              <div className="absolute -bottom-6 -left-6 glass-panel rounded-xl p-4 border border-white/20 shadow-2xl flex items-center gap-4 animate-bounce" style={{ animationDuration: '4s' }}>
                <div className="w-12 h-12 rounded-full bg-[#00F0FF] flex items-center justify-center">
                  <Map className="w-6 h-6 text-black" />
                </div>
                <div>
                  <div className="text-xs text-gray-400 font-mono">NEW MISSION</div>
                  <div className="font-bold">Scout: Tunisia Tech</div>
                  <div className="text-xs text-green-400">Found 42 targets</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer className="border-t border-white/10 mt-20 py-12 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-[#FF2A5F] to-[#00F0FF] flex items-center justify-center">
              <Zap className="w-3 h-3 text-white" />
            </div>
            <span className="font-bold font-mono tracking-wider">SALESINJECT</span>
          </div>
          <div className="text-sm text-gray-500">
            © 2026 SalesInject. The Visibility War Game. Building in MENA.
          </div>
          <div className="flex gap-4 text-sm text-gray-400">
            <a href="#" className="hover:text-white transition-colors">Privacy</a>
            <a href="#" className="hover:text-white transition-colors">Terms</a>
            <a href="#" className="hover:text-white transition-colors">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
