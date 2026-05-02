import React, { useState, useEffect } from 'react';

interface ActionStreakCounterProps {
  /** Number of consecutive missions completed */
  streakCount: number;
  /** Maximum streak achieved */
  maxStreak?: number;
  /** Size of the counter */
  size?: 'small' | 'medium' | 'large';
  /** Show flame animation */
  animated?: boolean;
  /** Callback when streak milestone is reached */
  onMilestone?: (milestone: number) => void;
}

/**
 * Number of consecutive missions completed
 * Used in CommandDeck and Dashboard
 */
export function ActionStreakCounter({
  streakCount,
  maxStreak,
  size = 'medium',
  animated = true,
  onMilestone,
}: ActionStreakCounterProps) {
  const [displayStreak, setDisplayStreak] = useState(streakCount);
  const [isPulsing, setIsPulsing] = useState(false);

  // Animate streak changes
  useEffect(() => {
    if (streakCount !== displayStreak) {
      setIsPulsing(true);

      // Check for milestones
      if (streakCount > displayStreak && streakCount % 5 === 0) {
        onMilestone?.(streakCount);
      }

      const timer = setTimeout(() => {
        setDisplayStreak(streakCount);
        setIsPulsing(false);
      }, 300);

      return () => clearTimeout(timer);
    }
  }, [streakCount, displayStreak, onMilestone]);

  const sizeStyles = {
    small: {
      fontSize: '16px',
      flameSize: '20px',
      gap: '8px',
    },
    medium: {
      fontSize: '24px',
      flameSize: '28px',
      gap: '12px',
    },
    large: {
      fontSize: '32px',
      flameSize: '36px',
      gap: '16px',
    },
  }[size];

  const getFlameColor = (streak: number) => {
    if (streak >= 20) return 'var(--war-red)';
    if (streak >= 10) return 'var(--war-yellow)';
    if (streak >= 5) return 'var(--war-orange)';
    return 'var(--war-cyan)';
  };

  const flameColor = getFlameColor(streakCount);

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: sizeStyles.gap,
        padding: '12px 20px',
        background: 'rgba(26, 26, 26, 0.8)',
        backdropFilter: 'blur(10px)',
        border: `2px solid ${flameColor}`,
        borderRadius: '16px',
        fontFamily: 'var(--font-display)',
        fontWeight: '900',
        color: 'white',
        animation: isPulsing ? 'streak-pulse 0.3s ease-in-out' : 'none',
      }}
    >
      {/* Flame icon */}
      <div
        style={{
          position: 'relative',
          width: sizeStyles.flameSize,
          height: sizeStyles.flameSize,
          fontSize: sizeStyles.flameSize,
          animation: animated ? 'flame-flicker 1s ease-in-out infinite' : 'none',
          filter: `drop-shadow(0 0 10px ${flameColor})`,
        }}
      >
        🔥
        {/* Additional flame effects for high streaks */}
        {streakCount >= 10 && (
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              fontSize: `${parseInt(sizeStyles.flameSize) * 1.5}px`,
              opacity: 0.4,
              animation: 'flame-aura 2s ease-in-out infinite',
              zIndex: -1,
            }}
          >
            🔥
          </div>
        )}
      </div>

      {/* Streak count */}
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
        <span style={{ fontSize: sizeStyles.fontSize, color: flameColor }}>
          {displayStreak}
        </span>
        <span style={{ fontSize: `${parseInt(sizeStyles.fontSize) * 0.6}px`, opacity: 0.7 }}>
          STREAK
        </span>
      </div>

      {/* Max streak indicator */}
      {maxStreak !== undefined && maxStreak > streakCount && (
        <div
          style={{
            marginLeft: '8px',
            padding: '4px 8px',
            background: 'rgba(0, 0, 0, 0.5)',
            border: '1px solid var(--war-gray-700)',
            borderRadius: '8px',
            fontFamily: 'var(--font-mono)',
            fontSize: `${parseInt(sizeStyles.fontSize) * 0.5}px`,
            color: 'var(--si-muted)',
          }}
        >
          MAX {maxStreak}
        </div>
      )}

      {/* Streak level indicator */}
      <div
        style={{
          marginLeft: '8px',
          padding: '4px 8px',
          background: 'rgba(0, 0, 0, 0.5)',
          border: `1px solid ${flameColor}`,
          borderRadius: '8px',
          fontFamily: 'var(--font-mono)',
          fontSize: `${parseInt(sizeStyles.fontSize) * 0.5}px`,
          fontWeight: '700',
          color: flameColor,
          textTransform: 'uppercase',
        }}
      >
        {streakCount >= 20 ? 'LEGENDARY' :
         streakCount >= 10 ? 'EPIC' :
         streakCount >= 5 ? 'HOT' : 'WARMING'}
      </div>

      <style>
        {`
          @keyframes flame-flicker {
            0%, 100% {
              transform: scale(1) rotate(0deg);
              opacity: 1;
            }
            25% {
              transform: scale(1.1) rotate(-2deg);
              opacity: 0.9;
            }
            50% {
              transform: scale(0.95) rotate(2deg);
              opacity: 1;
            }
            75% {
              transform: scale(1.05) rotate(-1deg);
              opacity: 0.95;
            }
          }

          @keyframes flame-aura {
            0%, 100% {
              transform: translate(-50%, -50%) scale(1);
              opacity: 0.4;
            }
            50% {
              transform: translate(-50%, -50%) scale(1.2);
              opacity: 0.2;
            }
          }

          @keyframes streak-pulse {
            0% {
              transform: scale(1);
            }
            50% {
              transform: scale(1.1);
              box-shadow: 0 0 30px ${flameColor};
            }
            100% {
              transform: scale(1);
            }
          }
        `}
      </style>
    </div>
  );
}