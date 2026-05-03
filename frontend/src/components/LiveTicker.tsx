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

  return <div className="fixed top-0 left-0 right-0 z-[1100] h-6 bg-[#111] text-[10px] font-mono text-cyan-300 px-3 flex items-center whitespace-nowrap overflow-hidden">⚡ LIVE: {text}</div>;
}
