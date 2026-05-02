import React, { useState } from 'react';

interface ShareButtonProps {
  /** Mission trace ID to share */
  traceId: string;
  /** Button size */
  size?: 'small' | 'medium' | 'large';
  /** Button variant */
  variant?: 'primary' | 'ghost' | 'icon';
  /** Custom share URL template (use {trace_id} placeholder) */
  urlTemplate?: string;
  /** Custom share message */
  message?: string;
  /** Callback when share is successful */
  onShare?: (url: string) => void;
  /** Callback when share fails */
  onError?: (error: Error) => void;
}

/**
 * Generates Telegram share link with trace_id
 * Used in LoopEngine
 */
export function ShareButton({
  traceId,
  size = 'medium',
  variant = 'primary',
  urlTemplate,
  message,
  onShare,
  onError,
}: ShareButtonProps) {
  const [isSharing, setIsSharing] = useState(false);
  const [copied, setCopied] = useState(false);

  const getShareUrl = () => {
    const baseUrl = window.location.origin;
    const defaultTemplate = `${baseUrl}/replay/{trace_id}`;
    const template = urlTemplate || defaultTemplate;
    return template.replace('{trace_id}', traceId);
  };

  const getShareMessage = () => {
    return message || `Check out my mission replay: ${getShareUrl()}`;
  };

  const handleShare = async () => {
    setIsSharing(true);
    setCopied(false);

    try {
      const shareUrl = getShareUrl();
      const shareMessage = getShareMessage();

      // Check if Telegram WebApp is available
      if (window.Telegram?.WebApp) {
        // Use Telegram WebApp to share
        window.Telegram.WebApp.openTelegramLink(
          `https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(shareMessage)}`
        );
      } else if (navigator.share) {
        // Use Web Share API
        await navigator.share({
          title: 'Mission Replay',
          text: shareMessage,
          url: shareUrl,
        });
      } else if (navigator.clipboard) {
        // Fallback to clipboard
        await navigator.clipboard.writeText(shareUrl);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } else {
        // Last resort: open share dialog
        window.open(
          `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareMessage)}`,
          '_blank'
        );
      }

      onShare?.(shareUrl);
    } catch (error) {
      console.error('Share failed:', error);
      onError?.(error as Error);
    } finally {
      setIsSharing(false);
    }
  };

  const sizeStyles = {
    small: {
      padding: '8px 16px',
      fontSize: '12px',
      iconSize: '14px',
    },
    medium: {
      padding: '12px 24px',
      fontSize: '14px',
      iconSize: '18px',
    },
    large: {
      padding: '16px 32px',
      fontSize: '16px',
      iconSize: '22px',
    },
  }[size];

  const variantStyles = {
    primary: {
      background: 'var(--gradient-cyber)',
      border: '3px solid var(--war-black)',
      color: 'white',
      boxShadow: '0 0 0 2px var(--war-purple), 0 8px 0 0 var(--war-black), 0 8px 0 2px var(--war-purple)',
    },
    ghost: {
      background: 'transparent',
      border: '2px solid var(--war-cyan)',
      color: 'var(--war-cyan)',
      boxShadow: 'inset 0 0 20px rgba(0, 245, 255, 0.1), 0 0 20px rgba(0, 245, 255, 0.2)',
    },
    icon: {
      background: 'rgba(26, 26, 26, 0.8)',
      border: '2px solid var(--war-purple)',
      color: 'white',
      boxShadow: '0 0 20px rgba(139, 92, 246, 0.3)',
      padding: '12px',
      borderRadius: '50%',
      width: '48px',
      height: '48px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    },
  }[variant];

  const buttonContent = variant === 'icon' ? (
    <div style={{ fontSize: sizeStyles.iconSize }}>
      {isSharing ? '📤' : copied ? '✅' : '📤'}
    </div>
  ) : (
    <>
      <div style={{ fontSize: sizeStyles.iconSize, marginRight: '8px' }}>
        {isSharing ? '📤' : copied ? '✅' : '📤'}
      </div>
      <span style={{ fontSize: sizeStyles.fontSize, fontWeight: '700' }}>
        {copied ? 'COPIED!' : isSharing ? 'SHARING...' : 'SHARE MISSION'}
      </span>
    </>
  );

  return (
    <button
      onClick={handleShare}
      disabled={isSharing}
      style={{
        ...variantStyles,
        ...(variant !== 'icon' && { padding: sizeStyles.padding }),
        borderRadius: variant === 'icon' ? '50%' : '12px',
        fontFamily: 'var(--font-display)',
        fontWeight: '800',
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
        cursor: isSharing ? 'wait' : 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1)',
        opacity: isSharing ? 0.8 : 1,
        ...(variant !== 'icon' && {
          ':hover': {
            transform: 'translateY(-2px)',
            boxShadow: variant === 'primary'
              ? '0 0 0 2px var(--war-purple), 0 12px 0 0 var(--war-black), 0 12px 0 2px var(--war-purple), 0 0 40px var(--war-purple)'
              : 'inset 0 0 40px rgba(0, 245, 255, 0.3), 0 0 40px rgba(0, 245, 255, 0.5)',
          },
          ':active': {
            transform: 'translateY(4px)',
            boxShadow: variant === 'primary'
              ? '0 0 0 2px var(--war-purple), 0 4px 0 0 var(--war-black), 0 4px 0 2px var(--war-purple)'
              : 'inset 0 0 20px rgba(0, 245, 255, 0.2), 0 0 10px rgba(0, 245, 255, 0.3)',
          },
        }),
        ...(variant === 'icon' && {
          ':hover': {
            transform: 'scale(1.1)',
            boxShadow: '0 0 30px rgba(139, 92, 246, 0.5)',
          },
          ':active': {
            transform: 'scale(0.95)',
          },
        }),
      }}
    >
      {buttonContent}
    </button>
  );
}