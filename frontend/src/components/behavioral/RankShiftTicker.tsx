import React, { useState, useEffect } from 'react';

interface RankShiftTickerProps {
  /** Rank change value (positive or negative) */
  change: number;
  /** Current rank (optional) */
  currentRank?: number;
  /** Size of the ticker */
  size?: 'small' | 'medium' | 'large';
  /** Animation duration */
  duration?: number;
  /** Callback when animation completes */
  onComplete?: () => void;
}

/**
 * Small animation showing rank change (+2, -1, etc.)
 * Used in WarRoom and IntelHub
 */
export function RankShiftTicker({
  change,
  currentRank,
  size = 'medium',
  duration = 1000,
  onComplete,
}: RankShiftTickerProps) {
  const [isVisible, setIsVisible] = useState(true);
  const [animationKey, setAnimationKey] = useState(0);

  // Reset animation when change prop updates
  useEffect(() => {
    setIsVisible(true);
    setAnimationKey(prev => prev + 1);
  }, [change]);

  // Hide after animation
  useEffect(() => {
    if (isVisible) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        onComplete?.();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [isVisible, duration, onComplete]);

  if (!isVisible) return null;

  const isPositive = change > 0;
  const color = isPositive ? 'var(--war-green)' : 'var(--war-red)';
  const symbol = isPositive ? '↑' : '↓';

  const sizeStyles = {
    small: {
      fontSize: '14px',
      padding: '4px 8px',
      gap: '4px',
    },
    medium: {
      fontSize: '18px',
      padding: '6px 12px',
      gap: '6px',
    },
    large: {
      fontSize: '24px',
      padding: '8px 16px',
      gap: '8px',
    },
  }[size];

  return (
    <div
      key={animationKey}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: sizeStyles.padding,
        background: 'rgba(26, 26, 26, 0.8)',
        backdropFilter: 'blur(8px)',
        border: `2px solid ${color}`,
        borderRadius: '8px',
        fontFamily: 'var(--font-numbers)',
        fontWeight: '900',
        color: color,
        boxShadow: `0 0 20px ${color}40`,
        animation: `rank-ticker-${size} ${duration}ms cubic-bezier(0.4, 0, 0.2, 1) forwards`,
        gap: sizeStyles.gap,
        opacity: 0,
      }}
    >
      {/* Current rank (if provided) */}
      {currentRank !== undefined && (
        <span style={{ fontSize: sizeStyles.fontSize, opacity: 0.7 }}>
          #{currentRank}
        </span>
      )}

      {/* Change indicator */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '2px' }}>
        <span style={{ fontSize: sizeStyles.fontSize }}>{symbol}</span>
        <span style={{ fontSize: sizeStyles.fontSize }}>{Math.abs(change)}</span>
      </div>

      {/* New rank (if current rank provided) */}
      {currentRank !== undefined && (
        <span style={{ fontSize: sizeStyles.fontSize, opacity: 0.7 }}>
          → #{currentRank + change}
        </span>
      )}

      <style>
        {`
          @keyframes rank-ticker-small {
            0% {
              transform: translateY(-10px) scale(0.9);
              opacity: 0;
            }
            20% {
              transform: translateY(0) scale(1.1);
              opacity: 1;
            }
            80% {
              transform: translateY(0) scale(1);
              opacity: 1;
            }
            100% {
              transform: translateY(10px) scale(0.9);
              opacity: 0;
            }
          }

          @keyframes rank-ticker-medium {
            0% {
              transform: translateY(-15px) scale(0.9);
              opacity: 0;
            }
            20% {
              transform: translateY(0) scale(1.1);
              opacity: 1;
            }
            80% {
              transform: translateY(0) scale(1);
              opacity: 1;
            }
            100% {
              transform: translateY(15px) scale(0.9);
              opacity: 0;
            }
          }

          @keyframes rank-ticker-large {
            0% {
              transform: translateY(-20px) scale(0.9);
              opacity: 0;
            }
            20% {
              transform: translateY(0) scale(1.2);
              opacity: 1;
            }
            80% {
              transform: translateY(0) scale(1);
              opacity: 1;
            }
            100% {
              transform: translateY(20px) scale(0.9);
              opacity: 0;
            }
          }
        `}
      </style>
    </div>
  );
}