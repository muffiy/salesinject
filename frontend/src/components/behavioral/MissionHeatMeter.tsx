import React, { useState, useEffect } from 'react';

interface MissionHeatMeterProps {
  /** Heat level (0 to 1) */
  heatLevel: number;
  /** Width of the meter */
  width?: number;
  /** Height of the meter */
  height?: number;
  /** Show temperature labels */
  showLabels?: boolean;
  /** Animation duration for heat changes */
  animationDuration?: number;
  /** Callback when heat crosses threshold */
  onThreshold?: (threshold: 'cold' | 'warm' | 'hot' | 'critical') => void;
}

/**
 * Horizontal meter (cold → hot) based on mission intensity
 * Used in WarRoom
 */
export function MissionHeatMeter({
  heatLevel,
  width = 300,
  height = 40,
  showLabels = true,
  animationDuration = 500,
  onThreshold,
}: MissionHeatMeterProps) {
  const [displayHeat, setDisplayHeat] = useState(heatLevel);
  const [lastThreshold, setLastThreshold] = useState<'cold' | 'warm' | 'hot' | 'critical'>('cold');

  // Animate heat changes
  useEffect(() => {
    const timer = setTimeout(() => {
      setDisplayHeat(heatLevel);
    }, 50);

    return () => clearTimeout(timer);
  }, [heatLevel]);

  // Detect threshold changes
  useEffect(() => {
    let newThreshold: 'cold' | 'warm' | 'hot' | 'critical';
    if (heatLevel < 0.25) {
      newThreshold = 'cold';
    } else if (heatLevel < 0.5) {
      newThreshold = 'warm';
    } else if (heatLevel < 0.75) {
      newThreshold = 'hot';
    } else {
      newThreshold = 'critical';
    }

    if (newThreshold !== lastThreshold) {
      setLastThreshold(newThreshold);
      onThreshold?.(newThreshold);
    }
  }, [heatLevel, lastThreshold, onThreshold]);

  const getGradient = (heat: number) => {
    const percent = Math.max(0, Math.min(100, heat * 100));
    return `linear-gradient(to right,
      #00f5ff 0%,
      #00ff88 ${percent * 0.25}%,
      #ffd60a ${percent * 0.5}%,
      #ffaa00 ${percent * 0.75}%,
      #ff3366 ${percent}%,
      var(--war-gray-700) ${percent}%,
      var(--war-gray-700) 100%
    )`;
  };

  const getGlowColor = (heat: number) => {
    if (heat < 0.25) return 'rgba(0, 245, 255, 0.3)';
    if (heat < 0.5) return 'rgba(0, 255, 136, 0.3)';
    if (heat < 0.75) return 'rgba(255, 214, 10, 0.3)';
    return 'rgba(255, 51, 102, 0.5)';
  };

  const barWidth = Math.max(0, Math.min(100, displayHeat * 100));

  return (
    <div
      style={{
        position: 'relative',
        width: width,
        height: height,
      }}
    >
      {/* Background track */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: getGradient(1),
          borderRadius: '999px',
          overflow: 'hidden',
        }}
      />

      {/* Mask for current heat level */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          bottom: 0,
          width: `${barWidth}%`,
          background: getGradient(displayHeat),
          borderRadius: '999px',
          transition: `width ${animationDuration}ms cubic-bezier(0.4, 0, 0.2, 1)`,
          boxShadow: `0 0 30px ${getGlowColor(displayHeat)}`,
        }}
      />

      {/* Heat waves effect */}
      {displayHeat > 0.5 && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: `linear-gradient(90deg,
              transparent,
              rgba(255, 255, 255, ${displayHeat * 0.2}),
              transparent
            )`,
            backgroundSize: '200% 100%',
            animation: 'heat-wave 3s linear infinite',
            opacity: displayHeat,
            pointerEvents: 'none',
          }}
        />
      )}

      {/* Temperature labels */}
      {showLabels && (
        <>
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '10%',
              transform: 'translate(-50%, -50%)',
              fontFamily: 'var(--font-mono)',
              fontSize: '10px',
              fontWeight: '700',
              color: 'var(--war-cyan)',
              textShadow: '0 1px 2px rgba(0, 0, 0, 0.8)',
              opacity: displayHeat >= 0.25 ? 1 : 0.3,
            }}
          >
            COLD
          </div>
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '35%',
              transform: 'translate(-50%, -50%)',
              fontFamily: 'var(--font-mono)',
              fontSize: '10px',
              fontWeight: '700',
              color: 'var(--war-green)',
              textShadow: '0 1px 2px rgba(0, 0, 0, 0.8)',
              opacity: displayHeat >= 0.5 ? 1 : 0.3,
            }}
          >
            WARM
          </div>
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '60%',
              transform: 'translate(-50%, -50%)',
              fontFamily: 'var(--font-mono)',
              fontSize: '10px',
              fontWeight: '700',
              color: 'var(--war-yellow)',
              textShadow: '0 1px 2px rgba(0, 0, 0, 0.8)',
              opacity: displayHeat >= 0.75 ? 1 : 0.3,
            }}
          >
            HOT
          </div>
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '85%',
              transform: 'translate(-50%, -50%)',
              fontFamily: 'var(--font-mono)',
              fontSize: '10px',
              fontWeight: '700',
              color: 'var(--war-red)',
              textShadow: '0 1px 2px rgba(0, 0, 0, 0.8)',
              opacity: displayHeat >= 0.9 ? 1 : 0.3,
            }}
          >
            CRITICAL
          </div>
        </>
      )}

      {/* Current heat indicator */}
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: `${barWidth}%`,
          transform: 'translate(-50%, -50%)',
          width: '3px',
          height: '120%',
          background: 'white',
          boxShadow: '0 0 10px white',
          zIndex: 1,
        }}
      />

      {/* Heat percentage */}
      <div
        style={{
          position: 'absolute',
          bottom: '-20px',
          left: `${barWidth}%`,
          transform: 'translateX(-50%)',
          fontFamily: 'var(--font-numbers)',
          fontSize: '12px',
          fontWeight: '900',
          color: 'white',
          textShadow: '0 1px 3px rgba(0, 0, 0, 0.8)',
        }}
      >
        {(displayHeat * 100).toFixed(0)}%
      </div>

      <style>
        {`
          @keyframes heat-wave {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
          }
        `}
      </style>
    </div>
  );
}