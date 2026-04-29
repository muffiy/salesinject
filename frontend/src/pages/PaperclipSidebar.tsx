import { useEffect, useState } from 'react';
import { getPaperclips } from '../services/api';

export interface PaperclipItemData {
  id: string;
  task_id: string | null;
  item_type: 'mission_log' | 'pinned_profile' | 'ad_copy' | string;
  content: any;
  created_at: string;
}

export function PaperclipSidebar() {
  const [items, setItems] = useState<PaperclipItemData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Mark as viewed in localStorage to clear the red dot badge in App.tsx
    localStorage.setItem('salesinject_last_viewed_paperclips', new Date().toISOString());
    window.dispatchEvent(new Event('paperclipsViewed'));

    getPaperclips()
      .then((data) => {
        setItems(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load paperclips', err);
        setLoading(false);
      });
  }, []);

  const formatDate = (ds: string) => {
    const d = new Date(ds);
    return `${d.toLocaleDateString()} ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
  };

  const renderSkeleton = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', padding: '20px' }}>
      {[1, 2, 3].map(i => (
        <div key={i} style={{ 
          height: i === 1 ? '80px' : i === 2 ? '60px' : '120px', 
          background: 'rgba(255,255,255,0.03)', 
          borderRadius: '8px',
          border: '1px solid var(--war-gray-700)',
          animation: 'pulse 1.5s infinite ease-in-out'
        }} />
      ))}
      <style>
        {`
          @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 0.3; }
            100% { opacity: 0.6; }
          }
        `}
      </style>
    </div>
  );

  const renderEmptyState = () => (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      justifyContent: 'center', 
      flex: 1,
      minHeight: '400px',
      color: 'var(--war-cyan)',
      opacity: 0.6,
      textAlign: 'center',
      padding: '24px'
    }}>
      <div style={{ fontSize: '32px', marginBottom: '16px' }}>📭</div>
      <div style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', fontWeight: '700', letterSpacing: '0.5px' }}>
        No Intel Yet — Run a Scout Mission
      </div>
    </div>
  );

  const renderMissionLog = (item: PaperclipItemData) => (
    <div key={item.id} style={{
      padding: '16px',
      border: '1px solid var(--war-cyan)',
      background: 'rgba(0, 229, 255, 0.05)',
      borderRadius: '8px',
      borderLeft: '4px solid var(--war-cyan)',
      marginBottom: '16px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
        <span style={{ fontSize: '16px' }}>📡</span>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--war-cyan)', fontWeight: '700' }}>MISSION LOG</span>
        <span style={{ marginLeft: 'auto', fontSize: '10px', color: 'var(--si-muted)', fontFamily: 'var(--font-mono)' }}>
          {formatDate(item.created_at)}
        </span>
      </div>
      <div style={{ fontSize: '13px', color: 'var(--si-fg)', lineHeight: 1.5 }}>
        {item.content.report || JSON.stringify(item.content)}
      </div>
    </div>
  );

  const renderPinnedProfile = (item: PaperclipItemData) => {
    const data = item.content || {};
    return (
      <div key={item.id} style={{
        padding: '12px 16px',
        border: '1px solid var(--war-gray-700)',
        background: 'var(--war-black)',
        borderRadius: '8px',
        marginBottom: '16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--war-purple), var(--war-gray-700))', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold', fontSize: '14px' }}>
            {data.handle ? data.handle.charAt(0).toUpperCase() : '?'}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontWeight: '700', fontSize: '14px', color: 'white' }}>@{data.handle || 'unknown'}</span>
            <span style={{ fontSize: '11px', color: 'var(--si-muted)', display: 'flex', alignItems: 'center', gap: '4px', fontFamily: 'var(--font-mono)' }}>
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--war-yellow)', display: 'inline-block' }}></span>
              {data.niche || 'General'}
            </span>
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '2px' }}>
          <span style={{ fontSize: '12px', fontWeight: '700', color: 'var(--war-cyan)' }}>{data.followers || '0'}</span>
          <span style={{ fontSize: '10px', color: 'var(--si-muted)', fontFamily: 'var(--font-mono)' }}>ENG: {data.engagement || '0%'}</span>
        </div>
      </div>
    );
  };

  const renderAdCopy = (item: PaperclipItemData) => (
    <div key={item.id} style={{
      padding: '16px',
      border: '1px solid var(--war-pink)',
      background: 'rgba(255, 0, 128, 0.05)',
      borderRadius: '8px',
      boxShadow: '0 0 15px rgba(255, 0, 128, 0.1) inset',
      marginBottom: '16px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
        <span style={{ fontSize: '14px' }}>📝</span>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--war-pink)', fontWeight: '700' }}>AD COPY DRAFT</span>
        <span style={{ marginLeft: 'auto', fontSize: '10px', color: 'var(--si-muted)', fontFamily: 'var(--font-mono)' }}>
          {formatDate(item.created_at)}
        </span>
      </div>
      <div style={{ 
        background: 'rgba(0,0,0,0.3)', 
        border: '1px solid var(--war-gray-700)', 
        padding: '12px', 
        borderRadius: '6px',
        fontSize: '13px', 
        color: '#e2e8f0', 
        lineHeight: 1.5,
        marginBottom: '16px',
        whiteSpace: 'pre-wrap'
      }}>
        {item.content.draft || JSON.stringify(item.content)}
      </div>
      <button 
        disabled
        style={{
          width: '100%',
          padding: '8px',
          background: 'var(--war-gray-700)',
          color: 'var(--si-muted)',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: '4px',
          fontFamily: 'var(--font-mono)',
          fontWeight: '700',
          fontSize: '12px',
          cursor: 'not-allowed',
          letterSpacing: '1px'
        }}
      >
        DEPLOY ASSET (LOCKED)
      </button>
    </div>
  );

  return (
    <div style={{ padding: '20px', flex: 1, backgroundColor: 'var(--war-black)', minHeight: '100%' }}>
      <div className="section-title" style={{ fontSize: '24px', marginBottom: '24px', color: 'var(--war-cyan)' }}>
        INTELLIGENCE FEED
      </div>

      {loading ? (
        renderSkeleton()
      ) : items.length === 0 ? (
        renderEmptyState()
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          {items.map(item => {
            switch (item.item_type) {
              case 'mission_log': return renderMissionLog(item);
              case 'pinned_profile': return renderPinnedProfile(item);
              case 'ad_copy': return renderAdCopy(item);
              default: 
                return (
                  <div key={item.id} style={{ padding: '12px', border: '1px solid var(--war-gray-700)', marginBottom: '12px', borderRadius: '4px' }}>
                    <span style={{ fontSize: '10px', color: 'var(--si-muted)' }}>{item.item_type}</span>
                  </div>
                );
            }
          })}
        </div>
      )}
    </div>
  );
}
