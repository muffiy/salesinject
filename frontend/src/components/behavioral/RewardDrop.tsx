import React, { useState, useEffect } from 'react';

interface RewardDropProps {
  /** Trigger the drop animation */
  trigger?: boolean;
  /** Value to display (e.g., +2, -0.42) */
  value: string | number;
  /** Type of reward: 'rank' for rank increase, 'cost' for cost deduction */
  type: 'rank' | 'cost';
  /** Position from top of screen (percentage) */
  top?: number;
  /** Delay before starting animation (ms) */
  delay?: number;
  /** Callback when animation completes */
  onComplete?: () => void;
}

/**
 * Micro-animation when cost deducted or rank increases
 * Used in WarRoom
 */
export function RewardDrop({
  trigger = false,
  value,
  type,
  top = 30,
  delay = 0,
  onComplete,
}: RewardDropProps) {
  const [isActive, setIsActive] = useState(false);
  const [animationKey, setAnimationKey] = useState(0);

  useEffect(() => {
    if (trigger) {
      const timer = setTimeout(() => {
        setIsActive(true);
        setAnimationKey(prev => prev + 1);
      }, delay);

      return () => clearTimeout(timer);
    }
  }, [trigger, delay]);

  useEffect(() => {
    if (isActive) {
      const timer = setTimeout(() => {
        setIsActive(false);
        onComplete?.();
      }, 1500);

      return () => clearTimeout(timer);
    }
  }, [isActive, onComplete]);

  if (!isActive) return null;

  const isPositive = typeof value === 'string' ? value.includes('+') : value > 0;
  const color = type === 'rank'
    ? (isPositive ? 'var(--war-green)' : 'var(--war-red)')
    : 'var(--war-yellow)';

  const symbol = type === 'rank'
    ? (isPositive ? '↑' : '↓')
    : '$';

  return (
    <div
      key={animationKey}
      style={{
        position: 'fixed',
        top: `${top}%`,
        left: '50%',
        transform: 'translateX(-50%)',
        fontSize: '28px',
        fontWeight: '900',
        fontFamily: 'var(--font-numbers)',
        color: color,
        textShadow: `0 0 20px ${color}`,
        zIndex: 9998,
        pointerEvents: 'none',
        animation: 'reward-drop 1.5s cubic-bezier(0.4, 0, 0.2, 1) forwards',
        opacity: 0,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span>{symbol}</span>
        <span>{value}</span>
      </div>

      {/* Trail effect */}
      <div
        style={{
          position: 'absolute',
          top: '100%',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '2px',
          height: '40px',
          background: `linear-gradient(to bottom, ${color}, transparent)`,
          opacity: 0.6,
          animation: 'reward-trail 1.5s cubic-bezier(0.4, 0, 0.2, 1) forwards',
        }}
      />

      <style>
        {`
          @keyframes reward-drop {
            0% {
              transform: translateX(-50%) translateY(-20px);
              opacity: 0;
            }
            20% {
              opacity: 1;
            }
            40% {
              transform: translateX(-50%) translateY(0);
            }
            60% {
              transform: translateX(-50%) translateY(-10px);
            }
            80% {
              transform: translateX(-50%) translateY(0);
              opacity: 1;
            }
            100% {
              transform: translateX(-50%) translateY(20px);
              opacity: 0;
            }
          }

          @keyframes reward-trail {
            0% {
              height: 0;
              opacity: 0;
            }
            20% {
              height: 40px;
              opacity: 0.6;
            }
            80% {
              height: 60px;
              opacity: 0.3;
            }
            100% {
              height: 80px;
              opacity: 0;
            }
          }
        `}
      </style>
    </div>
  );
}