import React, { useState, useEffect } from 'react';

interface EmotionalFeedbackOverlayProps {
  /** Current mission state */
  state?: 'dominating' | 'struggling' | 'neutral' | 'critical';
  /** Custom message to display */
  message?: string;
  /** Duration to show the message (ms) */
  duration?: number;
  /** Position on screen */
  position?: 'top' | 'center' | 'bottom';
  /** Callback when message hides */
  onHide?: () => void;
}

/**
 * Floating messages ("You are dominating", "High risk")
 * Used in WarRoom
 */
export function EmotionalFeedbackOverlay({
  state = 'neutral',
  message,
  duration = 3000,
  position = 'top',
  onHide,
}: EmotionalFeedbackOverlayProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [currentMessage, setCurrentMessage] = useState(message);
  const [currentState, setCurrentState] = useState(state);

  // Update when props change
  useEffect(() => {
    if (message !== undefined) {
      setCurrentMessage(message);
      setCurrentState(state);
      setIsVisible(true);
    } else {
      // Use default messages based on state
      const defaultMessages = {
        dominating: 'YOU ARE DOMINATING',
        struggling: 'RESISTANCE DETECTED',
        neutral: 'MISSION IN PROGRESS',
        critical: 'CRITICAL SITUATION',
      };
      setCurrentMessage(defaultMessages[state]);
      setCurrentState(state);
      setIsVisible(true);
    }
  }, [message, state]);

  // Hide after duration
  useEffect(() => {
    if (isVisible) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        onHide?.();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [isVisible, duration, onHide]);

  if (!isVisible) return null;

  const getStyleForState = (s: string) => {
    switch (s) {
      case 'dominating':
        return {
          color: 'var(--war-green)',
          borderColor: 'var(--war-green)',
          glowColor: 'rgba(0, 255, 136, 0.4)',
          icon: '🔥',
        };
      case 'struggling':
        return {
          color: 'var(--war-yellow)',
          borderColor: 'var(--war-yellow)',
          glowColor: 'rgba(255, 214, 10, 0.4)',
          icon: '⚡',
        };
      case 'critical':
        return {
          color: 'var(--war-red)',
          borderColor: 'var(--war-red)',
          glowColor: 'rgba(255, 51, 102, 0.5)',
          icon: '⚠️',
        };
      default:
        return {
          color: 'var(--war-cyan)',
          borderColor: 'var(--war-cyan)',
          glowColor: 'rgba(0, 245, 255, 0.4)',
          icon: '📡',
        };
    }
  };

  const style = getStyleForState(currentState);

  const positionStyles = {
    top: {
      top: '80px',
      left: '50%',
      transform: 'translateX(-50%)',
    },
    center: {
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
    },
    bottom: {
      bottom: '100px',
      left: '50%',
      transform: 'translateX(-50%)',
    },
  }[position];

  return (
    <div
      style={{
        position: 'fixed',
        ...positionStyles,
        padding: '16px 32px',
        background: 'rgba(10, 10, 10, 0.85)',
        backdropFilter: 'blur(20px)',
        border: `3px solid ${style.borderColor}`,
        borderRadius: '12px',
        fontFamily: 'var(--font-display)',
        fontSize: '18px',
        fontWeight: '900',
        color: style.color,
        textTransform: 'uppercase',
        letterSpacing: '0.1em',
        zIndex: 9996,
        boxShadow: `0 0 40px ${style.glowColor}`,
        animation: 'emotional-fade-in 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards',
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
        pointerEvents: 'none',
      }}
    >
      {/* Icon */}
      <div
        style={{
          fontSize: '24px',
          animation: 'emotional-icon-pulse 2s ease-in-out infinite',
        }}
      >
        {style.icon}
      </div>

      {/* Message */}
      <div>{currentMessage}</div>

      {/* Decorative elements */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `linear-gradient(45deg, transparent, ${style.color}10, transparent)`,
          backgroundSize: '200% 200%',
          animation: 'emotional-shine 3s linear infinite',
          pointerEvents: 'none',
          borderRadius: '8px',
        }}
      />

      <style>
        {`
          @keyframes emotional-fade-in {
            0% {
              opacity: 0;
              transform: ${position === 'center' ? 'translate(-50%, -60%)' : 'translateX(-50%) translateY(-20px)'};
            }
            100% {
              opacity: 1;
              transform: ${position === 'center' ? 'translate(-50%, -50%)' : 'translateX(-50%) translateY(0)'};
            }
          }

          @keyframes emotional-icon-pulse {
            0%, 100% {
              transform: scale(1);
            }
            50% {
              transform: scale(1.2);
            }
          }

          @keyframes emotional-shine {
            0% {
              background-position: -200% -200%;
            }
            100% {
              background-position: 200% 200%;
            }
          }
        `}
      </style>
    </div>
  );
}