
// The TikTok/IG shareable component designed in Gen-Z design system
interface StoryCardProps {
  username: string;
  rank: string;
  positionsGained: number;
  defeatedTarget: string;
}

export function StoryCard({ username, rank, positionsGained, defeatedTarget }: StoryCardProps) {
  return (
    <div style={{
      position: 'relative', width: '375px', height: '667px',
      background: 'var(--war-black)', overflow: 'hidden'
    }}>
      {/* Background */}
      <div style={{ position: 'absolute', inset: 0, opacity: 0.5, zIndex: 0 }}>
        <div style={{
          width: '100%', height: '100%',
          background: 'linear-gradient(135deg, var(--war-purple), var(--war-cyan))',
          filter: 'blur(40px)', opacity: 0.6
        }}></div>
      </div>
      
      {/* Content */}
      <div style={{
        position: 'relative', height: '100%', display: 'flex', flexDirection: 'column',
        justifyContent: 'space-between', padding: '40px 24px', zIndex: 10
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '32px', height: '32px', background: 'white', borderRadius: '50%',
            display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px'
          }}>⚡</div>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '14px', fontWeight: '700', color: 'white' }}>
            @{username}
          </span>
        </div>
        
        <div style={{ textAlign: 'center' }}>
          <h2 style={{
            fontFamily: 'var(--font-display)', fontSize: '48px', fontWeight: '900',
            background: 'var(--gradient-rage)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            marginBottom: '32px', textTransform: 'uppercase'
          }}>JUST DESTROYED</h2>
          
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '24px', marginBottom: '48px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <span className="stat-number" style={{ fontSize: '64px' }}>#{rank}</span>
              <span className="label">NEW RANK</span>
            </div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '32px', color: 'var(--war-pink)' }}>↑</div>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <span className="stat-number" style={{ fontSize: '64px', color: 'var(--war-pink)' }}>+{positionsGained}</span>
              <span className="label">POSITIONS</span>
            </div>
          </div>
          
          <div style={{ background: 'rgba(255, 51, 102, 0.2)', border: '2px solid var(--war-red)', padding: '12px 24px', display: 'inline-block' }}>
            <span className="label" style={{ color: 'var(--war-gray-700)', marginRight: '8px' }}>DEFEATED:</span>
            <span style={{ fontFamily: 'var(--font-display)', fontSize: '24px', fontWeight: '900', color: 'white', textTransform: 'uppercase' }}>{defeatedTarget}</span>
          </div>
        </div>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '2px solid var(--war-purple)', paddingTop: '16px' }}>
          <span style={{ fontFamily: 'var(--font-display)', fontSize: '16px', fontWeight: '800', textTransform: 'uppercase', color: 'white' }}>Join the war →</span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', fontWeight: '700', color: 'var(--war-cyan)' }}>genesis.market</span>
        </div>
      </div>
    </div>
  );
}
