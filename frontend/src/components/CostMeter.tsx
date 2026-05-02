import React, { useState, useEffect } from 'react';

interface CostMeterProps {
  /** Current cost value */
  cost: number;
  /** Maximum cost value */
  maxCost?: number;
  /** Warning threshold (percentage) */
  warningThreshold?: number;
  /** Critical threshold (percentage) */
  criticalThreshold?: number;
  /** Size of the meter */
  size?: 'small' | 'medium' | 'large';
  /** Show value label */
  showLabel?: boolean;
  /** Show percentage */
  showPercentage?: boolean;
  /** Animation duration for cost changes */
  animationDuration?: number;
  /** Callback when cost crosses threshold */
  onThreshold?: (threshold: 'low' | 'warning' | 'critical') => void;
}

/**
 * Visual cost meter with threshold warnings
 * Used throughout the UI to display mission costs
 */
export function CostMeter({
  cost,
  maxCost = 1.0,
  warningThreshold = 70,
  criticalThreshold = 90,
  size = 'medium',
  showLabel = true,
  showPercentage = true,
  animationDuration = 500,
  onThreshold,
}: CostMeterProps) {
  const [displayCost, setDisplayCost] = useState(cost);
  const [lastThreshold, setLastThreshold] = useState<'low' | 'warning' | 'critical'>('low');

  // Animate cost changes
  useEffect(() => {
    const timer = setTimeout(() => {
      setDisplayCost(cost);
    }, 50);

    return () => clearTimeout(timer);
  }, [cost]);

  // Detect threshold changes
  useEffect(() => {
    const percentage = (cost / maxCost) * 100;
    let newThreshold: 'low' | 'warning' | 'critical';
    if (percentage >= criticalThreshold) {
      newThreshold = 'critical';
    } else if (percentage >= warningThreshold) {
      newThreshold = 'warning';
    } else {
      newThreshold = 'low';
    }

    if (newThreshold !== lastThreshold) {
      setLastThreshold(newThreshold);
      onThreshold?.(newThreshold);
    }
  }, [cost, maxCost, warningThreshold, criticalThreshold, lastThreshold, onThreshold]);

  const percentage = (displayCost / maxCost) * 100;
  const clampedPercentage = Math.max(0, Math.min(100, percentage));

  const getColor = (perc: number) => {
    if (perc >= criticalThreshold) return 'var(--war-red)';
    if (perc >= warningThreshold) return 'var(--war-yellow)';
    return 'var(--war-green)';
  };

  const sizeStyles = {
    small: {
      height: '20px',
      fontSize: '11px',
      labelSize: '10px',
    },
    medium: {
      height: '30px',
      fontSize: '14px',
      labelSize: '12px',
    },
    large: {
      height: '40px',
      fontSize: '16px',
      labelSize: '14px',
    },
  }[size];

  const color = getColor(percentage);
  const isCritical = percentage >= criticalThreshold;

  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        height: sizeStyles.height,
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
          width: `${clampedPercentage}%`,
          background: color,
          borderRadius: '999px',
          transition: `width ${animationDuration}ms cubic-bezier(0.4, 0, 0.2, 1), background ${animationDuration}ms ease`,
          boxShadow: `0 0 20px ${color}40`,
        }}
      />

      {/* Warning and critical markers */}
      {maxCost > 0 && (
        <>
          <div
            style={{
              position: 'absolute',
              top: 0,
              bottom: 0,
              left: `${warningThreshold}%`,
              width: '1px',
              background: 'rgba(255, 255, 255, 0.3)',
            }}
          />
          <div
            style={{
              position: 'absolute',
              top: 0,
              bottom: 0,
              left: `${criticalThreshold}%`,
              width: '1px',
              background: 'rgba(255, 255, 255, 0.5)',
            }}
          />
        </>
      )}

      {/* Critical warning effect */}
      {isCritical && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: `linear-gradient(90deg, transparent, rgba(255, 51, 102, 0.3), transparent)`,
            backgroundSize: '200% 100%',
            animation: 'critical-pulse 1s ease-in-out infinite',
            pointerEvents: 'none',
          }}
        />
      )}

      {/* Value label */}
      {showLabel && (
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            fontSize: sizeStyles.fontSize,
            fontWeight: '700',
            color: 'white',
            textShadow: '0 1px 2px rgba(0, 0, 0, 0.8)',
            letterSpacing: '0.05em',
            zIndex: 1,
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <span style={{ fontFamily: 'var(--font-numbers)' }}>
            ${displayCost.toFixed(2)}
          </span>
          {showPercentage && maxCost > 0 && (
            <>
              <span style={{ opacity: 0.5 }}>/</span>
              <span style={{ opacity: 0.7, fontSize: sizeStyles.labelSize }}>
                ${maxCost.toFixed(2)}
              </span>
              <span style={{ opacity: 0.7, fontSize: sizeStyles.labelSize }}>
                ({percentage.toFixed(1)}%)
              </span>
            </>
          )}
        </div>
      )}

      <style>
        {`
          @keyframes critical-pulse {
            0%, 100% {
              opacity: 0.5;
            }
            50% {
              opacity: 0.8;
            }
          }
        `}
      </style>
    </div>
  );
}