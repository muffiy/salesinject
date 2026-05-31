import { useEffect, useMemo, useState } from 'react';

const FALLBACK = [
  'Yassine just earned +12 TND',
  '3 people competing for this mission',
  'New HOT drop nearby (+25%)',
];

export default function LiveTicker() {
  const [messages, setMessages] = useState<string[]>(FALLBACK);
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const ws = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/api/v1/ws/live-ticker`);
    ws.onmessage = (evt) => {
      try {
        const payload = JSON.parse(evt.data);
        if (payload?.message) setMessages((prev) => [payload.message, ...prev].slice(0, 20));
      } catch {}
    };
    return () => ws.close();
  }, []);

  useEffect(() => {
    const timer = window.setInterval(() => setIndex((v) => (v + 1) % Math.max(messages.length, 1)), 3000);
    return () => clearInterval(timer);
  }, [messages.length]);

  const text = useMemo(() => messages[index] ?? FALLBACK[0], [messages, index]);

  return (
    <div className="live-ticker" style={{
      position: 'fixed',
      bottom: '60px',
      left: 0,
      right: 0,
      height: '20px',
      background: 'rgba(16, 185, 129, 0.1)',
      borderTop: '1px solid rgba(16, 185, 129, 0.2)',
      display: 'flex',
      alignItems: 'center',
      padding: '0 16px',
      fontSize: '0.85rem',
      color: 'var(--green)',
      overflow: 'hidden',
      transition: 'var(--transition-medium)'
    }}>
      <div className="ticker-content" style={{
        display: 'flex',
        gap: '16px',
        animation: 'tickerMove 20s linear infinite'
      }}>
        {/* Ticker items - split the text into parts for individual animation */}
        {text.split(' ').map((word, wordIndex) => (
          <span
            key={`${index}-${wordIndex}`}
            className="ticker-item"
            style={{
              transition: 'var(--transition-fast)',
              padding: '4px 8px',
              borderRadius: '4px'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(16, 185, 129, 0.2)';
              e.currentTarget.style.transform = 'scale(1.05)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.transform = 'scale(1)';
            }}
          >
            {word}{wordIndex < text.split(' ').length - 1 ? ' ' : ''}
          </span>
        ))}
      </div>

      {/* Animated icon */}
      <span className="ticker-icon" style={{
        marginLeft: '8px',
        animation: 'float 3s ease-in-out infinite',
        display: 'inline-block'
      }}>
        ⚡
      </span>
    </div>
  );
}
