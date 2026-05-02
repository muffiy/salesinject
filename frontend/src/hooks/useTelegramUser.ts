import { useEffect, useState } from 'react';

declare global {
  interface Window {
    Telegram?: {
      WebApp: any;
    };
  }
}

export interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  photo_url?: string;
}

export function useTelegramUser() {
  const [user, setUser] = useState<TelegramUser | null>(null);
  const [initData, setInitData] = useState<string>('');
  const [colorScheme, setColorScheme] = useState<'light' | 'dark'>('dark');

  useEffect(() => {
    let tg = window.Telegram?.WebApp;
    if (!tg && (import.meta.env.DEV || import.meta.env.VITE_BYPASS_TELEGRAM === 'true')) {
      // Create a minimal mock Telegram WebApp for development
      console.log('Dev mode: mocking Telegram WebApp');
      const mockUser: TelegramUser = {
        id: 123456789,
        first_name: 'Dev',
        last_name: 'User',
        username: 'dev_user',
        language_code: 'en',
        photo_url: '',
      };
      const mockWebApp = {
        ready: () => {},
        expand: () => {},
        initDataUnsafe: { user: mockUser },
        initData: '',
        colorScheme: 'dark' as const,
      };
      // Attach to window for other components
      if (!window.Telegram) {
        window.Telegram = { WebApp: mockWebApp };
      } else {
        window.Telegram.WebApp = mockWebApp;
      }
      tg = mockWebApp;
    }

    if (tg) {
      tg.ready();
      tg.expand();
      setUser(tg.initDataUnsafe?.user || null);
      setInitData(tg.initData || '');
      setColorScheme(tg.colorScheme || 'dark');
    }
  }, []);

  return { user, initData, colorScheme };
}
