import { useEffect } from 'react';

interface SplashScreenProps {
  onFinish: () => void;
}

/**
 * Full screen splash screen with progress bar
 */
export default function SplashScreen({ onFinish }: SplashScreenProps) {
  useEffect(() => {
    const timer = setTimeout(onFinish, 2000);
    return () => clearTimeout(timer);
  }, [onFinish]);

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--war-black)',
    }}>
      <h1 style={{
        fontSize: '48px',
        fontWeight: '900',
        background: 'var(--gradient-cyber)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        textTransform: 'uppercase',
        fontFamily: 'var(--font-display)',
        marginBottom: '32px',
      }}>
        SALESINJECT
      </h1>
      <div style={{
        width: '256px',
        height: '4px',
        background: 'var(--war-gray-800)',
        borderRadius: '999px',
        overflow: 'hidden',
      }}>
        <div style={{
          height: '100%',
          width: '100%',
          background: 'var(--war-cyan)',
          animation: 'progress 2s linear forwards',
        }} />
      </div>
      <p style={{
        marginTop: '16px',
        color: 'var(--si-muted)',
        fontFamily: 'var(--font-mono)',
        fontSize: '14px',
      }}>
        SYSTEM BOOTING...
      </p>

      <style>
        {`
          @keyframes progress {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(0); }
          }
        `}
      </style>
    </div>
  );
}