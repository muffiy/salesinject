
interface SplashScreenProps {
  title?: string;
  subtitle?: string;
  ctaLabel?: string;
  ctaHref?: string;
  ctaOnClick?: () => void;
  showSparkle?: boolean;
}

export function SplashScreen({
  title = "MANAGE YOUR LEADS IN ONE PLACE",
  subtitle = "Weaponize your Ad Campaigns with AI Mercenaries. Deploy agents to scout, match, and conquer your target niches.",
  ctaLabel = "DEPLOY YOUR AGENTS",
  ctaHref = "https://t.me/salesInspectAI_Bot",
  ctaOnClick,
  showSparkle = true,
}: SplashScreenProps) {
  return (
    <div style={{
      background: 'var(--brand-bg)',
      minHeight: '100dvh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '24px',
      textAlign: 'center',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Sparkle Ornament */}
      {showSparkle && (
        <div style={{
          position: 'absolute',
          top: '20%',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '200px',
          height: '200px',
          opacity: 0.6,
          pointerEvents: 'none',
          zIndex: 0,
        }}>
          <div style={{
            position: 'absolute',
            top: '0',
            left: '50%',
            width: '4px',
            height: '80px',
            background: 'var(--brand-yellow)',
            transform: 'translateX(-50%)',
            filter: 'blur(1px)',
          }} />
          <div style={{
            position: 'absolute',
            top: '0',
            left: '50%',
            width: '80px',
            height: '4px',
            background: 'var(--brand-yellow)',
            transform: 'translateX(-50%)',
            filter: 'blur(1px)',
          }} />
          <div style={{
            position: 'absolute',
            top: '40px',
            left: '40px',
            width: '30px',
            height: '30px',
            background: 'var(--brand-pink)',
            borderRadius: '50%',
            filter: 'blur(8px)',
            opacity: 0.5,
          }} />
          <div style={{
            position: 'absolute',
            bottom: '40px',
            right: '40px',
            width: '20px',
            height: '20px',
            background: 'var(--brand-green)',
            borderRadius: '50%',
            filter: 'blur(6px)',
            opacity: 0.5,
          }} />
          <div style={{
            position: 'absolute',
            top: '60px',
            right: '60px',
            width: '15px',
            height: '15px',
            background: 'var(--brand-lime)',
            borderRadius: '50%',
            filter: 'blur(4px)',
            opacity: 0.7,
          }} />
        </div>
      )}

      {/* Background grid */}
      <div style={{
        position: 'absolute',
        inset: 0,
        backgroundImage: `linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)`,
        backgroundSize: '40px 40px',
        zIndex: 0,
      }} />

      <div style={{ position: 'relative', zIndex: 10, maxWidth: '800px' }}>
        {/* Title */}
        <h1 style={{
          fontFamily: 'var(--font-display)',
          fontSize: 'clamp(2.5rem, 8vw, 4.5rem)',
          fontWeight: 900,
          lineHeight: 1,
          letterSpacing: '-0.05em',
          color: 'var(--brand-white)',
          marginBottom: '1.5rem',
          textTransform: 'uppercase',
        }}>
          {title}
        </h1>

        {/* Subtitle */}
        <p style={{
          fontFamily: 'var(--font-body)',
          fontSize: 'clamp(1rem, 4vw, 1.25rem)',
          color: 'rgba(255, 255, 255, 0.7)',
          marginBottom: '3rem',
          lineHeight: 1.6,
          maxWidth: '600px',
          marginLeft: 'auto',
          marginRight: 'auto',
        }}>
          {subtitle}
        </p>

        {/* CTA Button */}
        <a
          href={ctaHref}
          onClick={ctaOnClick}
          style={{
            display: 'inline-block',
            padding: '1.25rem 3rem',
            fontFamily: 'var(--font-display)',
            fontSize: '1.125rem',
            fontWeight: 800,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            background: 'var(--brand-white)',
            color: 'var(--brand-black)',
            border: 'none',
            borderRadius: '9999px',
            cursor: 'pointer',
            textDecoration: 'none',
            transition: 'all 0.3s ease',
            boxShadow: '0 0 0 2px var(--brand-white), 0 0 30px rgba(255, 255, 255, 0.3)',
            position: 'relative',
            overflow: 'hidden',
            zIndex: 1,
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'var(--brand-yellow)';
            e.currentTarget.style.boxShadow = '0 0 0 2px var(--brand-yellow), 0 0 50px rgba(229, 255, 69, 0.5)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'var(--brand-white)';
            e.currentTarget.style.boxShadow = '0 0 0 2px var(--brand-white), 0 0 30px rgba(255, 255, 255, 0.3)';
          }}
        >
          {ctaLabel}
        </a>

        {/* Additional note */}
        <p style={{
          marginTop: '2rem',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.875rem',
          color: 'rgba(255, 255, 255, 0.5)',
        }}>
          Open in Telegram to start your first mission
        </p>
      </div>
    </div>
  );
}