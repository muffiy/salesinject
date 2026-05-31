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
      transition: 'var(--transition-medium)'
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
        transition: 'var(--transition-medium)'
      }}>
        SALESINJECT
      </h1>
      <div style={{
        width: '256px',
        height: '4px',
        background: 'var(--war-gray-800)',
        borderRadius: '999px',
        overflow: 'hidden',
        transition: 'var(--transition-medium)'
      }}>
        <div style={{
          height: '100%',
          width: '100%',
          background: 'var(--war-cyan)',
          animation: 'progress 2s linear forwards',
          transition: 'var(--transition-medium)'
        }} />
      </div>
      <p style={{
        marginTop: '16px',
        color: 'var(--si-muted)',
        fontFamily: 'var(--font-mono)',
        fontSize: '14px',
        transition: 'var(--transition-medium)'
      }}>
        SYSTEM BOOTING...
      </p>

      <style>
        {`
          @keyframes progress {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(0); }
          }

          /* Add subtle pulse to the h1 on load */
          @keyframes titlePulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
          }

          h1 {
            animation: titlePulse 3s ease-in-out infinite;
          }
        `}
      </style>
    </div>
  );
}