import React, { useState, useEffect } from 'react';

interface ThreatSignalProps {
  /** Threat level (0 to 1) */
  threatLevel: number;
  /** Show warning when threat exceeds this threshold */
  warningThreshold?: number;
  /** Show critical when threat exceeds this threshold */
  criticalThreshold?: number;
  /** Custom warning message */
  warningMessage?: string;
  /** Position of the signal */
  position?: 'top' | 'bottom' | 'left' | 'right';
  /** Callback when threat level changes category */
  onThreatChange?: (level: 'low' | 'warning' | 'critical') => void;
}

/**
 * Red glow + warning text when risk > 60%
 * Used in WarRoom
 */
export function ThreatSignal({
  threatLevel,
  warningThreshold = 0.6,
  criticalThreshold = 0.8,
  warningMessage,
  position = 'top',
  onThreatChange,
}: ThreatSignalProps) {
  const [lastCategory, setLastCategory] = useState<'low' | 'warning' | 'critical'>('low');

  // Determine threat category
  let category: 'low' | 'warning' | 'critical' = 'low';
  if (threatLevel >= criticalThreshold) {
    category = 'critical';
  } else if (threatLevel >= warningThreshold) {
    category = 'warning';
  }

  // Notify when category changes
  useEffect(() => {
    if (category !== lastCategory) {
      setLastCategory(category);
      onThreatChange?.(category);
    }
  }, [category, lastCategory, onThreatChange]);

  // Don't show anything for low threat
  if (category === 'low') return null;

  const isCritical = category === 'critical';
  const color = isCritical ? 'var(--war-red)' : 'var(--war-yellow)';
  const glowColor = isCritical ? 'rgba(255, 51, 102, 0.5)' : 'rgba(255, 214, 10, 0.5)';

  const defaultMessage = isCritical
    ? 'CRITICAL THREAT DETECTED'
    : 'ELEVATED RISK LEVEL';

  const message = warningMessage || defaultMessage;

  // Position styles
  const positionStyles = {
    top: {
      top: '20px',
      left: '50%',
      transform: 'translateX(-50%)',
    },
    bottom: {
      bottom: '20px',
      left: '50%',
      transform: 'translateX(-50%)',
    },
    left: {
      top: '50%',
      left: '20px',
      transform: 'translateY(-50%)',
    },
    right: {
      top: '50%',
      right: '20px',
      transform: 'translateY(-50%)',
    },
  }[position];

  return (
    <div
      style={{
        position: 'fixed',
        ...positionStyles,
        padding: '12px 24px',
        background: 'rgba(26, 26, 26, 0.85)',
        backdropFilter: 'blur(10px)',
        border: `2px solid ${color}`,
        borderRadius: '8px',
        fontFamily: 'var(--font-mono)',
        fontSize: '12px',
        fontWeight: '800',
        color: color,
        textTransform: 'uppercase',
        letterSpacing: '0.1em',
        zIndex: 9997,
        boxShadow: `0 0 30px ${glowColor}`,
        animation: 'threat-pulse 2s ease-in-out infinite',
        pointerEvents: 'none',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
      }}
    >
      {/* Warning icon */}
      <div
        style={{
          fontSize: '16px',
          animation: 'threat-icon-shake 0.5s ease-in-out infinite',
        }}
      >
        {isCritical ? '⚠️' : '⚠️'}
      </div>

      {/* Message */}
      <div>{message}</div>

      {/* Threat level indicator */}
      <div
        style={{
          marginLeft: '8px',
          padding: '4px 8px',
          background: 'rgba(0, 0, 0, 0.5)',
          border: `1px solid ${color}`,
          borderRadius: '4px',
          fontSize: '11px',
          fontWeight: '900',
          fontFamily: 'var(--font-numbers)',
        }}
      >
        {(threatLevel * 100).toFixed(0)}%
      </div>

      <style>
        {`
          @keyframes threat-pulse {
            0%, 100% {
              box-shadow: 0 0 30px ${glowColor};
            }
            50% {
              box-shadow: 0 0 50px ${glowColor};
            }
          }

          @keyframes threat-icon-shake {
            0%, 100% {
              transform: rotate(0deg);
            }
            25% {
              transform: rotate(-5deg);
            }
            75% {
              transform: rotate(5deg);
            }
          }
        `}
      </style>
    </div>
  );
}