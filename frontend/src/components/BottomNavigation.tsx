import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

interface BottomNavigationProps {
  hasActiveMission?: boolean;
}

/**
 * Fixed bottom navigation with Home and Intel tabs
 * Shows active mission indicator when mission is claimed
 */
export default function BottomNavigation({ hasActiveMission = false }: BottomNavigationProps) {
  const location = useLocation();
  const navigate = useNavigate();

  const tabs = [
    { id: 'home', label: 'Home', icon: '🎯', path: '/' },
    { id: 'map', label: 'Map', icon: '🌍', path: '/map' },
    { id: 'intel', label: 'Intel', icon: '📊', path: '/intel' },
  ];

  return (
    <nav style={{
      position: 'fixed',
      bottom: 0,
      left: 0,
      right: 0,
      display: 'flex',
      background: 'rgba(10, 10, 10, 0.95)',
      backdropFilter: 'blur(20px)',
      borderTop: '1px solid var(--war-gray-700)',
      padding: '12px 16px',
      paddingBottom: 'calc(12px + env(safe-area-inset-bottom, 0px))',
      zIndex: 1000,
    }}>
      {tabs.map((tab) => {
        const isActive = location.pathname === tab.path;

        return (
          <button
            key={tab.id}
            onClick={() => navigate(tab.path)}
            style={{
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '6px',
              background: 'transparent',
              border: 'none',
              color: isActive ? 'var(--war-cyan)' : 'var(--si-muted)',
              fontFamily: 'var(--font-mono)',
              fontSize: '11px',
              fontWeight: '700',
              textTransform: 'uppercase',
              cursor: 'pointer',
              position: 'relative',
              padding: '8px 4px',
              transition: 'var(--transition-medium)',
              position: 'relative',
              overflow: 'hidden'
            }}
            onMouseEnter={(e) => {
              const btn = e.currentTarget;
              btn.style.transform = 'translateY(-2px)';
              btn.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
            }}
            onMouseLeave={(e) => {
              const btn = e.currentTarget;
              btn.style.transform = 'translateY(0)';
              btn.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
            }}
            onMouseDown={(e) => {
              const btn = e.currentTarget;
              btn.style.transform = 'translateY(0)';
            }}
            onMouseUp={(e) => {
              const btn = e.currentTarget;
              btn.style.transform = 'translateY(-2px)';
            }}
          >
            <div style={{
              fontSize: '20px',
              position: 'relative',
              transition: 'var(--transition-fast)'
            }}>
              {tab.icon}

              {/* Active mission indicator for Home tab */}
              {tab.id === 'home' && hasActiveMission && (
                <div style={{
                  position: 'absolute',
                  top: '-4px',
                  right: '-4px',
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: 'var(--war-red)',
                  animation: 'pulse 2s infinite',
                }} />
              )}
            </div>

            <span>{tab.label}</span>

            {/* Active indicator */}
            {isActive && (
              <div style={{
                position: 'absolute',
                bottom: '-12px',
                width: '24px',
                height: '3px',
                background: 'var(--war-cyan)',
                borderRadius: '999px',
                transition: 'var(--transition-medium)'
              }} />
            )}
          </button>
        );
      })}

      {/* Active mission floating indicator (if mission active) */}
      {hasActiveMission && (
        <div style={{
          position: 'absolute',
          top: '-32px',
          left: '50%',
          transform: 'translateX(-50%)',
          padding: '8px 16px',
          background: 'var(--gradient-rage)',
          borderRadius: '999px',
          fontFamily: 'var(--font-mono)',
          fontSize: '11px',
          fontWeight: '700',
          color: 'white',
          textTransform: 'uppercase',
          whiteSpace: 'nowrap',
          boxShadow: '0 0 20px var(--war-red)',
          animation: 'float 3s ease-in-out infinite',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
        }}>
          <span>⚡</span>
          <span>MISSION ACTIVE</span>
        </div>
      )}

      <style>
        {`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }

          @keyframes float {
            0%, 100% { transform: translateX(-50%) translateY(0); }
            50% { transform: translateX(-50%) translateY(-5px); }
          }
        `}
      </style>
    </nav>
  );
}