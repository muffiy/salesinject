import React, { useState, useEffect } from 'react';

interface GhostAgent {
  id: string;
  name: string;
  type: 'scout' | 'ammo' | 'bounty';
  lon: number;
  lat: number;
  status: 'active' | 'idle' | 'completed';
  rank: number;
  opacity: number;
}

interface GhostAgentsLayerProps {
  /** Map data points for ghost agents */
  agents: GhostAgent[];
  /** Map container reference */
  mapRef?: React.RefObject<any>;
  /** Whether the layer is visible */
  visible?: boolean;
  /** Opacity of ghost agents */
  baseOpacity?: number;
  /** Callback when an agent is clicked */
  onAgentClick?: (agent: GhostAgent) => void;
}

/**
 * Translucent bubbles of other users' agents (social pressure)
 * Used in WarRoom (on map)
 */
export function GhostAgentsLayer({
  agents,
  mapRef,
  visible = true,
  baseOpacity = 0.3,
  onAgentClick,
}: GhostAgentsLayerProps) {
  const [hoveredAgent, setHoveredAgent] = useState<string | null>(null);

  if (!visible || agents.length === 0) return null;

  const getColorForType = (type: string) => {
    switch (type) {
      case 'scout': return 'var(--war-cyan)';
      case 'ammo': return 'var(--war-green)';
      case 'bounty': return 'var(--war-red)';
      default: return 'var(--war-purple)';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return '▶️';
      case 'idle': return '⏸️';
      case 'completed': return '✅';
      default: return '❓';
    }
  };

  // This component would typically integrate with DeckGL or MapLibre
  // For now, we'll render a simplified version
  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        pointerEvents: 'none',
        zIndex: 100,
      }}
    >
      {/* Ghost agent indicators */}
      {agents.map((agent) => {
        const isHovered = hoveredAgent === agent.id;
        const color = getColorForType(agent.type);
        const opacity = isHovered ? baseOpacity * 2 : agent.opacity * baseOpacity;

        // In a real implementation, these would be positioned based on map coordinates
        // For demo purposes, we'll use fixed positions
        const left = `${(agent.lon + 180) / 360 * 100}%`;
        const top = `${(90 - agent.lat) / 180 * 100}%`;

        return (
          <div
            key={agent.id}
            style={{
              position: 'absolute',
              left: left,
              top: top,
              transform: 'translate(-50%, -50%)',
              pointerEvents: 'auto',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
            }}
            onMouseEnter={() => setHoveredAgent(agent.id)}
            onMouseLeave={() => setHoveredAgent(null)}
            onClick={() => onAgentClick?.(agent)}
          >
            {/* Outer pulse ring */}
            <div
              style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                width: '60px',
                height: '60px',
                borderRadius: '50%',
                border: `2px solid ${color}`,
                opacity: opacity * 0.5,
                animation: 'ghost-pulse 3s ease-in-out infinite',
              }}
            />

            {/* Agent bubble */}
            <div
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                background: `radial-gradient(circle, ${color}40, ${color}20)`,
                border: `2px solid ${color}`,
                backdropFilter: 'blur(4px)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                color: 'white',
                textShadow: '0 1px 3px rgba(0, 0, 0, 0.8)',
                transform: isHovered ? 'scale(1.2)' : 'scale(1)',
                transition: 'transform 0.2s ease',
                boxShadow: `0 0 20px ${color}${Math.floor(opacity * 255).toString(16).padStart(2, '0')}`,
              }}
            >
              {getStatusIcon(agent.status)}
            </div>

            {/* Rank badge */}
            <div
              style={{
                position: 'absolute',
                top: '-8px',
                right: '-8px',
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                background: 'rgba(26, 26, 26, 0.9)',
                border: `1px solid ${color}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '10px',
                fontWeight: '900',
                fontFamily: 'var(--font-numbers)',
                color: color,
              }}
            >
              {agent.rank}
            </div>

            {/* Tooltip on hover */}
            {isHovered && (
              <div
                style={{
                  position: 'absolute',
                  bottom: '100%',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  marginBottom: '10px',
                  padding: '8px 12px',
                  background: 'rgba(10, 10, 10, 0.9)',
                  backdropFilter: 'blur(10px)',
                  border: `1px solid ${color}`,
                  borderRadius: '8px',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '11px',
                  fontWeight: '700',
                  color: 'white',
                  textAlign: 'center',
                  whiteSpace: 'nowrap',
                  zIndex: 101,
                  pointerEvents: 'none',
                  boxShadow: `0 0 20px ${color}40`,
                }}
              >
                <div style={{ color, marginBottom: '4px' }}>{agent.name}</div>
                <div style={{ fontSize: '10px', opacity: 0.8 }}>
                  {agent.type.toUpperCase()} • {agent.status.toUpperCase()}
                </div>
              </div>
            )}
          </div>
        );
      })}

      <style>
        {`
          @keyframes ghost-pulse {
            0%, 100% {
              transform: translate(-50%, -50%) scale(1);
              opacity: 0.2;
            }
            50% {
              transform: translate(-50%, -50%) scale(1.5);
              opacity: 0;
            }
          }
        `}
      </style>
    </div>
  );
}

// Default mock data for demonstration
export const mockGhostAgents: GhostAgent[] = [
  {
    id: 'ghost1',
    name: 'ALPHA TEAM',
    type: 'scout',
    lon: -74.006,
    lat: 40.7128,
    status: 'active',
    rank: 1,
    opacity: 0.7,
  },
  {
    id: 'ghost2',
    name: 'BETA SQUAD',
    type: 'ammo',
    lon: -0.1276,
    lat: 51.5072,
    status: 'idle',
    rank: 3,
    opacity: 0.5,
  },
  {
    id: 'ghost3',
    name: 'GAMMA FORCE',
    type: 'bounty',
    lon: 139.6917,
    lat: 35.6895,
    status: 'completed',
    rank: 2,
    opacity: 0.3,
  },
  {
    id: 'ghost4',
    name: 'DELTA UNIT',
    type: 'scout',
    lon: -118.2437,
    lat: 34.0522,
    status: 'active',
    rank: 5,
    opacity: 0.6,
  },
  {
    id: 'ghost5',
    name: 'EPSILON CELL',
    type: 'ammo',
    lon: 2.3522,
    lat: 48.8566,
    status: 'active',
    rank: 4,
    opacity: 0.8,
  },
];