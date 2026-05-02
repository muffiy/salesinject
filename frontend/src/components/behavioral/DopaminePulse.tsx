import React, { useState, useEffect } from 'react';

interface DopaminePulseProps {
  /** Trigger the pulse animation */
  trigger?: boolean;
  /** Size of the pulse ring (pixels) */
  size?: number;
  /** Color of the pulse */
  color?: string;
  /** Duration of the animation in milliseconds */
  duration?: number;
  /** Optional sound effect URL */
  soundUrl?: string;
  /** Callback when animation completes */
  onComplete?: () => void;
}

/**
 * Animated ring + sound effect for success events
 * Used in WarRoom to celebrate node completions
 */
export function DopaminePulse({
  trigger = false,
  size = 120,
  color = 'var(--war-cyan)',
  duration = 800,
  soundUrl,
  onComplete,
}: DopaminePulseProps) {
  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    if (trigger && !isActive) {
      setIsActive(true);

      // Play sound if provided
      if (soundUrl) {
        const audio = new Audio(soundUrl);
        audio.volume = 0.3;
        audio.play().catch(() => {
          // Silent fail on autoplay restrictions
        });
      }

      // Reset after animation
      const timer = setTimeout(() => {
        setIsActive(false);
        onComplete?.();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [trigger, isActive, soundUrl, duration, onComplete]);

  if (!isActive) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: size,
        height: size,
        pointerEvents: 'none',
        zIndex: 9999,
      }}
    >
      {/* Outer ring */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          borderRadius: '50%',
          border: `3px solid ${color}`,
          animation: `dopamine-pulse ${duration}ms cubic-bezier(0.4, 0, 0.2, 1) forwards`,
          boxShadow: `0 0 40px ${color}`,
        }}
      />

      {/* Inner ring */}
      <div
        style={{
          position: 'absolute',
          inset: '15%',
          borderRadius: '50%',
          border: `2px solid ${color}`,
          animation: `dopamine-pulse-inner ${duration}ms cubic-bezier(0.4, 0, 0.2, 1) forwards`,
          opacity: 0.7,
        }}
      />

      {/* Center burst */}
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          width: '20%',
          height: '20%',
          transform: 'translate(-50%, -50%)',
          background: color,
          borderRadius: '50%',
          animation: `dopamine-burst ${duration}ms cubic-bezier(0.4, 0, 0.2, 1) forwards`,
          boxShadow: `0 0 30px ${color}`,
        }}
      />

      <style>
        {`
          @keyframes dopamine-pulse {
            0% {
              transform: scale(0.1);
              opacity: 1;
            }
            70% {
              opacity: 0.7;
            }
            100% {
              transform: scale(2);
              opacity: 0;
            }
          }

          @keyframes dopamine-pulse-inner {
            0% {
              transform: scale(0.1);
              opacity: 0.8;
            }
            100% {
              transform: scale(1.5);
              opacity: 0;
            }
          }

          @keyframes dopamine-burst {
            0% {
              transform: translate(-50%, -50%) scale(0);
              opacity: 1;
            }
            50% {
              transform: translate(-50%, -50%) scale(1.2);
              opacity: 0.8;
            }
            100% {
              transform: translate(-50%, -50%) scale(1.8);
              opacity: 0;
            }
          }
        `}
      </style>
    </div>
  );
}