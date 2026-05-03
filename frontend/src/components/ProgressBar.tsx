import { useEffect, useState } from 'react';
import api from '../services/api';

type Progress = { level: number; xp_current: number; xp_next: number; next_unlock: string };

export default function ProgressBar() {
  const [progress, setProgress] = useState<Progress | null>(null);
  useEffect(() => {
    api.get('/users/progress').then((r) => setProgress(r.data)).catch(() => {});
  }, []);
  if (!progress) return null;
  const pct = Math.max(0, Math.min(100, (progress.xp_current / progress.xp_next) * 100));
  return <div className="sticky top-6 z-40 mt-2">
    <div className="text-[10px] text-cyan-200 font-mono mb-1">LVL {progress.level} · {progress.xp_current}/{progress.xp_next} XP · {progress.next_unlock}</div>
    <div className="h-[6px] bg-[#333] rounded-full overflow-hidden"><div className="h-full bg-[#00F5FF]" style={{ width: `${pct}%` }} /></div>
  </div>;
}
