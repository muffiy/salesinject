import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const NICHES = [
  { id: 'saas', label: 'SaaS/Tech', color: 'var(--war-cyan)' },
  { id: 'food', label: 'Food & Restaurants', color: 'var(--war-pink)' },
  { id: 'fashion', label: 'Fashion & Apparel', color: '#ff79c6' },
  { id: 'real_estate', label: 'Real Estate', color: '#bd93f9' },
  { id: 'fitness', label: 'Health & Fitness', color: 'var(--war-green)' },
  { id: 'ecommerce', label: 'E-commerce', color: '#f1fa8c' },
  { id: 'education', label: 'Education', color: '#ffb86c' },
  { id: 'beauty', label: 'Beauty & Cosmetics', color: '#ff5555' }
];

export function Onboarding() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [name, setName] = useState('');
  const [selectedNiche, setSelectedNiche] = useState(NICHES[0]);

  const handleNext = () => {
    if (step === 1 && !name) return;
    if (step < 3) {
      setStep(step + 1);
    } else {
      // Complete flow and move to app
      navigate('/app');
    }
  };

  const getSigil = (str: string) => str ? str.substring(0, 2).toUpperCase() : '??';

  return (
    <div style={{ background: 'var(--war-black)', color: 'white', minHeight: '100dvh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '24px' }}>
      <div className="card-glass" style={{ width: '100%', maxWidth: '420px', padding: '32px', position: 'relative', overflow: 'hidden' }}>
        
        {/* Dynamic Niche Glow Background Effect */}
        <div style={{
          position: 'absolute', top: '-50%', left: '-50%', width: '200%', height: '200%',
          background: `radial-gradient(circle at 50% 0%, ${selectedNiche.color}22 0%, transparent 60%)`,
          pointerEvents: 'none', zIndex: 0, transition: 'background 0.5s ease'
        }} />

        <div style={{ marginBottom: '32px', textAlign: 'center', position: 'relative', zIndex: 1 }}>
          <h2 className="section-title" style={{ fontSize: '24px', color: 'var(--war-cyan)', textShadow: '0 0 10px rgba(0, 255, 255, 0.3)' }}>COMMAND INIT</h2>
          <div className="label">PHASE {step} // 3</div>
        </div>

        <div style={{ position: 'relative', zIndex: 1 }}>
          {step === 1 && (
            <div className="input-wrapper" style={{ animation: 'scanline 0.5s ease-out' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '24px' }}>
                <div style={{ 
                  width: '80px', height: '80px', borderRadius: '50%', border: '2px solid var(--war-cyan)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontFamily: 'var(--font-display)', fontSize: '32px', color: 'var(--war-cyan)',
                  boxShadow: '0 0 20px rgba(0, 255, 255, 0.2)', textShadow: '0 0 5px var(--war-cyan)'
                }}>
                  {getSigil(name)}
                </div>
              </div>
              <label className="input-label" style={{ textAlign: 'center', display: 'block' }}>ENTER COMMANDER ALIAS</label>
              <input 
                autoFocus
                className="input-terminal" 
                placeholder="_e.g. NeoBrand" 
                value={name} 
                onChange={e => setName(e.target.value)} 
                style={{ textAlign: 'center', fontSize: '18px', padding: '16px' }}
              />
            </div>
          )}

          {step === 2 && (
            <div className="input-wrapper" style={{ animation: 'scanline 0.5s ease-out' }}>
              <label className="input-label">SELECT TARGET DIRECTIVE</label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '300px', overflowY: 'auto', paddingRight: '8px' }}>
                {NICHES.map(niche => (
                  <button 
                    key={niche.id}
                    onClick={() => setSelectedNiche(niche)}
                    style={{
                      background: selectedNiche.id === niche.id ? `${niche.color}22` : 'transparent',
                      border: `1px solid ${selectedNiche.id === niche.id ? niche.color : 'var(--si-border)'}`,
                      color: selectedNiche.id === niche.id ? niche.color : 'var(--si-text)',
                      padding: '16px',
                      borderRadius: '4px',
                      textAlign: 'left',
                      cursor: 'pointer',
                      fontFamily: 'var(--font-mono)',
                      fontSize: '14px',
                      transition: 'all 0.2s',
                      boxShadow: selectedNiche.id === niche.id ? `inset 0 0 10px ${niche.color}22` : 'none'
                    }}
                  >
                    {selectedNiche.id === niche.id ? '▶ ' : '  '} {niche.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {step === 3 && (
            <div style={{ textAlign: 'center', marginBottom: '24px', animation: 'scanline 0.5s ease-out' }}>
               <div style={{ 
                  width: '60px', height: '60px', borderRadius: '50%', border: `2px solid ${selectedNiche.color}`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px',
                  fontFamily: 'var(--font-display)', fontSize: '24px', color: selectedNiche.color,
                  boxShadow: `0 0 20px ${selectedNiche.color}44`, textShadow: `0 0 5px ${selectedNiche.color}`
                }}>
                  {getSigil(name)}
                </div>
              <h3 style={{ fontFamily: 'var(--font-display)', color: 'white', fontSize: '20px', marginBottom: '8px' }}>IDENTITY VERIFIED</h3>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: '14px', color: 'var(--si-muted)', marginBottom: '24px' }}>
                Directive locked to <strong style={{ color: selectedNiche.color }}>{selectedNiche.label}</strong>.
              </p>
              
              <div style={{ borderTop: '1px solid var(--si-border)', borderBottom: '1px solid var(--si-border)', padding: '16px 0', marginBottom: '16px' }}>
                <p style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--si-muted)', textTransform: 'uppercase' }}>Acquiring Initial Scout operative</p>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '16px', marginTop: '12px' }}>
                  <span style={{ textDecoration: 'line-through', color: '#ff5555', fontSize: '16px', fontFamily: 'var(--font-mono)' }}>50 CREDITS</span>
                  <span style={{ color: 'var(--si-muted)' }}>→</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '4px 12px', background: 'rgba(0, 255, 0, 0.1)', border: '1px solid var(--war-green)', borderRadius: '4px' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--war-green)', boxShadow: '0 0 8px var(--war-green)' }} />
                    <span style={{ fontSize: '18px', fontWeight: 'bold', color: 'var(--war-green)', fontFamily: 'var(--font-display)', letterSpacing: '2px' }}>FREE</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <button className="btn-primary" style={{ width: '100%', marginTop: '16px' }} onClick={handleNext}>
            {step === 3 ? 'START DEPLOYMENT' : 'NEXT'}
          </button>
        </div>
      </div>
    </div>
  );
}
