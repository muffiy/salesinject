import React, { useState, useEffect } from 'react';

interface BudgetAlertProps {
  /** Current budget remaining */
  budgetRemaining: number;
  /** Total budget */
  totalBudget: number;
  /** Warning threshold (percentage) */
  warningThreshold?: number;
  /** Critical threshold (percentage) */
  criticalThreshold?: number;
  /** Position of the alert */
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
  /** Whether the alert is dismissible */
  dismissible?: boolean;
  /** Callback when alert is dismissed */
  onDismiss?: () => void;
  /** Callback when budget reaches critical level */
  onCritical?: () => void;
}

/**
 * Shows warning when budget is low (<20%)
 * Used in IntelHub and Dashboard
 */
export function BudgetAlert({
  budgetRemaining,
  totalBudget,
  warningThreshold = 20,
  criticalThreshold = 10,
  position = 'top-right',
  dismissible = true,
  onDismiss,
  onCritical,
}: BudgetAlertProps) {
  const [isVisible, setIsVisible] = useState(true);
  const [wasCritical, setWasCritical] = useState(false);

  const percentage = (budgetRemaining / totalBudget) * 100;
  const isWarning = percentage <= warningThreshold;
  const isCritical = percentage <= criticalThreshold;

  // Notify when budget reaches critical level
  useEffect(() => {
    if (isCritical && !wasCritical) {
      setWasCritical(true);
      onCritical?.();
    } else if (!isCritical) {
      setWasCritical(false);
    }
  }, [isCritical, wasCritical, onCritical]);

  const handleDismiss = () => {
    setIsVisible(false);
    onDismiss?.();
  };

  if (!isVisible || !isWarning) return null;

  const color = isCritical ? 'var(--war-red)' : 'var(--war-yellow)';
  const icon = isCritical ? '⚠️' : '💰';
  const message = isCritical
    ? 'CRITICAL: BUDGET NEARLY DEPLETED'
    : 'WARNING: BUDGET RUNNING LOW';

  const positionStyles = {
    'top-right': { top: '20px', right: '20px' },
    'top-left': { top: '20px', left: '20px' },
    'bottom-right': { bottom: '20px', right: '20px' },
    'bottom-left': { bottom: '20px', left: '20px' },
  }[position];

  return (
    <div
      style={{
        position: 'fixed',
        ...positionStyles,
        padding: '16px 20px',
        background: 'rgba(26, 26, 26, 0.95)',
        backdropFilter: 'blur(20px)',
        border: `3px solid ${color}`,
        borderRadius: '12px',
        fontFamily: 'var(--font-mono)',
        fontSize: '13px',
        fontWeight: '800',
        color: color,
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
        zIndex: 9995,
        boxShadow: `0 0 40px ${color}40`,
        animation: 'budget-alert-pulse 2s ease-in-out infinite',
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
        maxWidth: '400px',
      }}
    >
      {/* Icon */}
      <div style={{ fontSize: '24px' }}>{icon}</div>

      {/* Message and details */}
      <div style={{ flex: 1 }}>
        <div style={{ marginBottom: '8px' }}>{message}</div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          fontSize: '11px',
          opacity: 0.9,
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}>
            <span>REMAINING:</span>
            <span style={{
              fontFamily: 'var(--font-numbers)',
              fontWeight: '900',
              color: 'white',
            }}>
              ${budgetRemaining.toFixed(2)}
            </span>
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}>
            <span>PERCENT:</span>
            <span style={{
              fontFamily: 'var(--font-numbers)',
              fontWeight: '900',
              color: color,
            }}>
              {percentage.toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      {/* Progress bar */}
      <div style={{
        width: '100px',
        height: '6px',
        background: 'var(--war-gray-700)',
        borderRadius: '999px',
        overflow: 'hidden',
      }}>
        <div
          style={{
            width: `${percentage}%`,
            height: '100%',
            background: color,
            borderRadius: '999px',
            transition: 'width 0.3s ease',
          }}
        />
      </div>

      {/* Dismiss button */}
      {dismissible && (
        <button
          onClick={handleDismiss}
          style={{
            marginLeft: '12px',
            background: 'transparent',
            border: 'none',
            color: 'var(--si-muted)',
            fontSize: '18px',
            cursor: 'pointer',
            padding: '4px',
            borderRadius: '4px',
            lineHeight: 1,
          }}
          title="Dismiss alert"
        >
          ×
        </button>
      )}

      <style>
        {`
          @keyframes budget-alert-pulse {
            0%, 100% {
              box-shadow: 0 0 40px ${color}40;
            }
            50% {
              box-shadow: 0 0 60px ${color}60;
            }
          }
        `}
      </style>
    </div>
  );
}