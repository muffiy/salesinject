import React, { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';

export function TelegramGuard() {
  const [hasInitData, setHasInitData] = useState<boolean | null>(null);

  useEffect(() => {
    const telegram = (window as any).Telegram;
    if (telegram?.WebApp?.initData) {
      setHasInitData(true);
    } else if (import.meta.env.DEV) {
      console.log('Dev mode: skipping Telegram initData check');
      setHasInitData(true); // Allow local bypassing
    } else {
      setHasInitData(false);
    }
  }, []);

  if (hasInitData === null) return null; // Or a subtle loading state

  if (!hasInitData) {
    return (
      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', height: '100dvh', background: 'var(--war-black)',
        color: 'white', padding: '24px', textAlign: 'center'
      }}>
        <h2 style={{ fontFamily: 'var(--font-display)', color: 'var(--war-pink)', fontSize: '24px', marginBottom: '16px' }}>RESTRICTED ACCESS</h2>
        <p style={{ fontFamily: 'var(--font-mono)', fontSize: '14px', marginBottom: '24px', color: 'var(--si-muted)' }}>SalesInject Command must be launched via Telegram.</p>
        <a href="https://t.me/SalesInjectBot" className="btn-primary" style={{ textDecoration: 'none' }}>
          <span className="btn-text">OPEN IN TELEGRAM</span>
        </a>
      </div>
    );
  }

  return <Outlet />;
}
