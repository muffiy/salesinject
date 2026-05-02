import React, { useState, useEffect } from 'react';

interface UncertaintyBarProps {
  /** Current probability (0 to 1) */
  probability: number;
  /** Height of the bar */
  height?: number;
  /** Width of the bar */
  width?: number;
  /** Show percentage label */
  showLabel?: boolean;
  /** Animation duration for probability changes */
  animationDuration?: number;
  /** Callback when probability changes significantly */
  onThreshold?: (threshold: 'low' | 'medium' | 'high') => void;
}

/**
 * Shows probability of success changing live
 * Used in CommandDeck and WarRoom
 */
export function UncertaintyBar({
  probability,
  height = 24,
  width = 300,
  showLabel = true,
  animationDuration = 500,
  onThreshold,
}: UncertaintyBarProps) {
  const [displayProb, setDisplayProb] = useState(probability);
  const [lastThreshold, setLastThreshold] = useState<'low' | 'medium' | 'high'>('medium');

  // Animate probability changes
  useEffect(() => {
    const timer = setTimeout(() => {
      setDisplayProb(probability);
    }, 50);

    return () => clearTimeout(timer);
  }, [probability]);

  // Detect threshold changes
  useEffect(() => {
    let newThreshold: 'low' | 'medium' | 'high';
    if (probability < 0.3) {
      newThreshold = 'low';
    } else if (probability < 0.7) {
      newThreshold = 'medium';
    } else {
      newThreshold = 'high';
    }

    if (newThreshold !== lastThreshold) {
      setLastThreshold(newThreshold);
      onThreshold?.(newThreshold);
    }
  }, [probability, lastThreshold, onThreshold]);

  const getColor = (prob: number) => {
    if (prob < 0.3) return 'var(--war-red)';
    if (prob < 0.7) return 'var(--war-yellow)';
    return 'var(--war-green)';
  };

  const getGlowColor = (prob: number) => {
    if (prob < 0.3) return 'rgba(255, 51, 102, 0.4)';
    if (prob < 0.7) return 'rgba(255, 214, 10, 0.4)';
    return 'rgba(0, 255, 136, 0.4)';
  };

  const barWidth = Math.max(0, Math.min(100, displayProb * 100));

  return (
    <div
      style={{
        position: 'relative',
        width: width,
        height: height,
        background: 'rgba(255, 255, 255, 0.05)',
        border: '2px solid var(--war-gray-700)',
        borderRadius: '999px',
        overflow: 'hidden',
        fontFamily: 'var(--font-mono)',
      }}
    >
      {/* Background fill */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          bottom: 0,
          width: `${barWidth}%`,
          background: getColor(displayProb),
          borderRadius: '999px',
          transition: `width ${animationDuration}ms cubic-bezier(0.4, 0, 0.2, 1), background ${animationDuration}ms ease`,
          boxShadow: `0 0 20px ${getGlowColor(displayProb)}`,
        }}
      />

      {/* Scan line effect */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent)`,
          backgroundSize: '200% 100%',
          animation: 'uncertainty-scan 3s linear infinite',
          opacity: 0.3,
          pointerEvents: 'none',
        }}
      />

      {/* Percentage label */}
      {showLabel && (
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            fontSize: '11px',
            fontWeight: '700',
            color: 'white',
            textShadow: '0 1px 2px rgba(0, 0, 0, 0.8)',
            letterSpacing: '0.05em',
            zIndex: 1,
          }}
        >
          {(displayProb * 100).toFixed(1)}%
        </div>
      )}

      {/* Threshold markers */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          bottom: 0,
          left: '30%',
          width: '1px',
          background: 'rgba(255, 255, 255, 0.2)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          top: 0,
          bottom: 0,
          left: '70%',
          width: '1px',
          background: 'rgba(255, 255, 255, 0.2)',
        }}
      />

      <style>
        {`
          @keyframes uncertainty-scan {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
          }
        `}
      </style>
    </div>
  );
}