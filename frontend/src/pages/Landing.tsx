import React from 'react';

export function Landing() {
  return (
    <div style={{ background: 'var(--war-black)', minHeight: '100dvh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '24px', textAlign: 'center' }}>
      <h1 className="hero-title" style={{ marginBottom: '24px' }}>SALESINJECT</h1>
      <p style={{ fontFamily: 'var(--font-mono)', fontSize: '18px', color: 'var(--si-muted)', marginBottom: '40px', maxWidth: '600px' }}>
        Weaponize your Ad Campaigns with AI Mercenaries. Deploy agents to scout, match, and conquer your target niches.
      </p>
      
      <a href="https://t.me/SalesInjectBot" className="btn-primary" style={{ textDecoration: 'none', padding: '20px 40px', fontSize: '20px' }}>
        <span className="btn-text">DEPLOY YOUR AGENTS</span>
      </a>

      {/* Background aesthetics */}
      <div className="btn-glow" style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '400px', opacity: 0.1, zIndex: 0, pointerEvents: 'none' }} />
    </div>
  );
}
