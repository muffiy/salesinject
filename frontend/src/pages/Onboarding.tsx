import { useState } from 'react';
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
  const [inputHovered, setInputHovered] = useState(false);
  const [inputFocused, setInputFocused] = useState(false);

  const handleNext = () => {
    if (step === 1 && !name) return;
    if (step < 3) {
      setStep(step + 1);
    } else {
      // Complete flow and move to app
      navigate('/app');
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
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

        {/* Progress Indicator */}
        <div className="onboarding-progress" style={{
          height: '4px',
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '2px',
          overflow: 'hidden',
          margin: '24px 0'
        }}>
          <div className="progress-fill" style={{
            width: `${step / 3 * 100}%`,
            height: '100%',
            background: 'linear-gradient(90deg, var(--accent), var(--accent2))',
            transition: 'width 0.5s ease-out'
          }}></div>
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
                className="onboarding-input" 
                placeholder="_e.g. NeoBrand" 
                value={name} 
                onChange={e => setName(e.target.value)} 
                onFocus={() => setInputFocused(true)}
                onBlur={() => setInputFocused(false)}
                onMouseEnter={() => setInputHovered(true)}
                onMouseLeave={() => setInputHovered(false)}
                style={{ 
                  textAlign: 'center', 
                  fontSize: '18px', 
                  padding: '16px',
                  transition: 'var(--transition-medium)',
                  border: inputFocused ? `1px solid var(--accent)` : inputHovered ? '1px solid rgba(99, 102, 241, 0.5)' : '1px solid var(--border)',
                  borderRadius: '8px',
                  background: inputFocused ? 'rgba(255, 255, 255, 0.05)' : 'rgba(255, 255, 255, 0.03)',
                  boxShadow: inputFocused ? '0 0 0 2px rgba(99, 102, 241, 0.2)' : 'none'
                }}
              />
            </div>
          )}

          {step === 2 && (
            <div className="input-wrapper" style={{ animation: 'scanline 0.5s ease-out' }}>
              <label className="input-label">SELECT TARGET DIRECTIVE</label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '300px', overflowY: 'auto', paddingRight: '8px' }}>
                {NICHES.map(niche => (
                  <div 
                    key={niche.id}
                    onClick={() => setSelectedNiche(niche)}
                    className="onboarding-option"
                    style={{
                      transition: 'var(--transition-medium)',
                      border: selectedNiche.id === niche.id ? `1px solid ${niche.color}` : '1px solid var(--border)',
                      borderRadius: '12px',
                      padding: '20px',
                      background: selectedNiche.id === niche.id ? 'rgba(99, 102, 241, 0.1)' : 'transparent',
                      cursor: 'pointer'
                    }}
                  >
                    {selectedNiche.id === niche.id ? '▶ ' : '  '} {niche.label}
                  </div>
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

          <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', marginTop: '24px' }}>
            <button className="btn-secondary" onClick={handleBack} disabled={step === 1} style={{
              width: '100%',
              padding: '16px',
              fontSize: '1rem',
              transition: 'var(--transition-medium)'
            }}>
              Go Back
            </button>
            <button className="btn-primary" onClick={handleNext} style={{
              width: '100%',
              padding: '16px',
              fontSize: '1rem',
              fontWeight: '700',
              transition: 'var(--transition-medium)',
              position: 'relative',
              overflow: 'hidden'
            }}>
              {step === 3 ? 'START DEPLOYMENT' : 'NEXT'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
