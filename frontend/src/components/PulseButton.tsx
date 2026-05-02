import React, { useState } from 'react';

interface PulseButtonProps {
  /** Button text */
  children: React.ReactNode;
  /** Button click handler */
  onClick: () => void;
  /** Button variant */
  variant?: 'primary' | 'secondary' | 'danger' | 'success';
  /** Button size */
  size?: 'small' | 'medium' | 'large';
  /** Whether the button is disabled */
  disabled?: boolean;
  /** Whether to show pulse animation */
  pulse?: boolean;
  /** Pulse animation color */
  pulseColor?: string;
  /** Pulse animation interval (ms) */
  pulseInterval?: number;
  /** Additional CSS class */
  className?: string;
}

/**
 * Animated button with pulse effect
 * Used throughout the UI for primary actions
 */
export function PulseButton({
  children,
  onClick,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  pulse = false,
  pulseColor,
  pulseInterval = 2000,
  className,
}: PulseButtonProps) {
  const [isPulsing, setIsPulsing] = useState(false);

  const variantStyles = {
    primary: {
      background: 'var(--gradient-rage)',
      border: '3px solid var(--war-black)',
      color: 'white',
      boxShadow: '0 0 0 2px var(--war-pink), 0 8px 0 0 var(--war-black), 0 8px 0 2px var(--war-pink)',
    },
    secondary: {
      background: 'var(--gradient-cyber)',
      border: '3px solid var(--war-black)',
      color: 'white',
      boxShadow: '0 0 0 2px var(--war-purple), 0 8px 0 0 var(--war-black), 0 8px 0 2px var(--war-purple)',
    },
    danger: {
      background: 'var(--gradient-rage)',
      border: '3px solid var(--war-black)',
      color: 'white',
      boxShadow: '0 0 0 2px var(--war-red), 0 8px 0 0 var(--war-black), 0 8px 0 2px var(--war-red)',
    },
    success: {
      background: 'linear-gradient(135deg, #00FF88 0%, #00F5FF 50%, #3366FF 100%)',
      border: '3px solid var(--war-black)',
      color: 'white',
      boxShadow: '0 0 0 2px var(--war-green), 0 8px 0 0 var(--war-black), 0 8px 0 2px var(--war-green)',
    },
  }[variant];

  const sizeStyles = {
    small: {
      padding: '8px 16px',
      fontSize: '12px',
    },
    medium: {
      padding: '12px 24px',
      fontSize: '14px',
    },
    large: {
      padding: '16px 32px',
      fontSize: '16px',
    },
  }[size];

  const pulseColorValue = pulseColor ||
    (variant === 'primary' ? 'var(--war-pink)' :
     variant === 'secondary' ? 'var(--war-purple)' :
     variant === 'danger' ? 'var(--war-red)' : 'var(--war-green)');

  const handleClick = (e: React.MouseEvent) => {
    if (!disabled) {
      onClick();
      // Trigger a pulse on click
      setIsPulsing(true);
      setTimeout(() => setIsPulsing(false), 300);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled}
      className={className}
      style={{
        ...variantStyles,
        ...sizeStyles,
        borderRadius: '12px',
        fontFamily: 'var(--font-display)',
        fontWeight: '800',
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
        cursor: disabled ? 'not-allowed' : 'pointer',
        position: 'relative',
        overflow: 'hidden',
        transition: 'all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1)',
        opacity: disabled ? 0.6 : 1,
        ...(!disabled && {
          ':hover': {
            transform: 'translateY(-2px)',
            boxShadow: `${variantStyles.boxShadow}, 0 0 40px ${pulseColorValue}`,
          },
          ':active': {
            transform: 'translateY(4px)',
            boxShadow: variantStyles.boxShadow.replace('8px', '4px'),
          },
        }),
      }}
    >
      {/* Pulse animation ring */}
      {(pulse || isPulsing) && (
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: '100%',
            height: '100%',
            borderRadius: '12px',
            border: `2px solid ${pulseColorValue}`,
            animation: `pulse-expand ${pulseInterval}ms ease-out infinite`,
            pointerEvents: 'none',
            opacity: 0.6,
          }}
        />
      )}

      {/* Button content */}
      <span style={{ position: 'relative', zIndex: 1 }}>
        {children}
      </span>

      {/* Glow effect */}
      <div
        style={{
          position: 'absolute',
          top: '-50%',
          left: '-50%',
          width: '200%',
          height: '200%',
          background: `conic-gradient(from 0deg, transparent 0deg 340deg, ${pulseColorValue} 340deg 360deg)`,
          animation: 'btn-rotate 3s linear infinite',
          opacity: 0,
          transition: 'opacity 0.3s',
          pointerEvents: 'none',
        }}
      />

      <style>
        {`
          @keyframes pulse-expand {
            0% {
              transform: translate(-50%, -50%) scale(1);
              opacity: 0.6;
            }
            100% {
              transform: translate(-50%, -50%) scale(1.2);
              opacity: 0;
            }
          }

          @keyframes btn-rotate {
            to { transform: rotate(360deg); }
          }

          button:hover .btn-glow { opacity: 0.5; }
        `}
      </style>
    </button>
  );
}