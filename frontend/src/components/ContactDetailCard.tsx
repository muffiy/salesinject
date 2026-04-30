import { useState } from 'react';

export interface ContactProfileData {
  handle?: string;
  display_name?: string;
  bio?: string;
  avatar_url?: string;
  niche?: string;
  followers?: number;
  engagement_pct?: number;
  platforms?: { name: string; pct: number }[];
  contact_email?: string;
  manager_name?: string;
  rate_card_range?: string;
  recent_content_thumbnails?: string[];
}

interface ContactDetailCardProps {
  data: ContactProfileData;
  onPitch?: (data: ContactProfileData) => void;
  onSave?: (data: ContactProfileData) => void;
  onDismiss?: (data: ContactProfileData) => void;
}

function formatNum(n: number | undefined): string {
  if (n == null) return '0';
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

export function ContactDetailCard({ data, onPitch, onSave, onDismiss }: ContactDetailCardProps) {
  const [expanded, setExpanded] = useState(false);

  const handle = data.handle || 'unknown';
  const initials = handle.charAt(0).toUpperCase();

  return (
    <div
      onClick={() => setExpanded(!expanded)}
      className="bg-brand-card rounded-2xl border border-[#2A2A2A] overflow-hidden cursor-pointer transition-all duration-300"
    >
      {/* Collapsed Row */}
      <div className="flex items-center gap-3 p-4">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-brand-pink to-brand-yellow flex items-center justify-center text-brand-white font-bold text-sm shrink-0">
          {data.avatar_url ? (
            <img src={data.avatar_url} alt={handle} className="w-full h-full rounded-full object-cover" />
          ) : (
            initials
          )}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-brand-white font-bold text-sm truncate">@{handle}</span>
            {data.niche && (
              <span className="flex items-center gap-1 text-xs text-white/50 font-mono">
                <span className="w-1.5 h-1.5 rounded-full bg-brand-yellow inline-block" />
                {data.niche}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-4 text-right shrink-0">
          <div>
            <div className="text-brand-green font-numbers font-bold text-sm">{formatNum(data.followers)}</div>
            <div className="text-[10px] text-white/40 font-mono uppercase">Followers</div>
          </div>
          <div>
            <div className="text-brand-yellow font-numbers font-bold text-sm">{data.engagement_pct ?? '0'}%</div>
            <div className="text-[10px] text-white/40 font-mono uppercase">Eng</div>
          </div>
          <svg
            className={`w-5 h-5 text-white/40 transition-transform duration-300 ${expanded ? 'rotate-180' : ''}`}
            fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {/* Expanded Detail */}
      <div
        className={`transition-all duration-300 ease-out overflow-hidden ${
          expanded ? 'max-h-[800px] opacity-100' : 'max-h-0 opacity-0'
        }`}
      >
        <div className="px-4 pb-4 border-t border-[#2A2A2A] pt-4 flex flex-col gap-4">
          {/* Profile Hero */}
          <div className="flex gap-4 items-start">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-pink to-brand-yellow flex items-center justify-center text-brand-white font-display font-bold text-2xl shrink-0">
              {data.avatar_url ? (
                <img src={data.avatar_url} alt={handle} className="w-full h-full rounded-2xl object-cover" />
              ) : (
                initials
              )}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-brand-white font-display font-bold text-lg leading-tight">
                {data.display_name || `@${handle}`}
              </div>
              <div className="text-white/40 font-mono text-xs">@{handle}</div>
              {data.bio && (
                <p className="text-white/60 text-xs mt-1.5 line-clamp-3 leading-snug">{data.bio}</p>
              )}
            </div>
          </div>

          {/* Big Stats */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-[#1A1A1A] rounded-xl p-3">
              <div className="text-brand-green font-numbers font-bold text-2xl">{formatNum(data.followers)}</div>
              <div className="text-white/40 font-mono text-[10px] uppercase mt-0.5">Followers</div>
            </div>
            <div className="bg-[#1A1A1A] rounded-xl p-3">
              <div className="text-brand-yellow font-numbers font-bold text-2xl">{data.engagement_pct ?? '0'}%</div>
              <div className="text-white/40 font-mono text-[10px] uppercase mt-0.5">Engagement</div>
            </div>
          </div>

          {/* Content Strip */}
          {data.recent_content_thumbnails && data.recent_content_thumbnails.length > 0 && (
            <div>
              <div className="text-white/40 font-mono text-[10px] uppercase tracking-wider mb-2">Recent Content</div>
              <div className="flex gap-2 overflow-x-auto pb-1">
                {data.recent_content_thumbnails.map((src, i) => (
                  <div key={i} className="w-[72px] h-[96px] rounded-lg bg-[#1A1A1A] shrink-0 overflow-hidden">
                    <img src={src} alt="" className="w-full h-full object-cover" />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Platform Breakdown */}
          {data.platforms && data.platforms.length > 0 && (
            <div className="flex flex-col gap-2">
              <div className="text-white/40 font-mono text-[10px] uppercase tracking-wider">Platforms</div>
              {data.platforms.map((p) => (
                <div key={p.name} className="flex items-center gap-2">
                  <span className="text-white/60 font-mono text-xs w-16 shrink-0">{p.name}</span>
                  <div className="flex-1 h-1.5 bg-[#1A1A1A] rounded-full overflow-hidden">
                    <div
                      className="h-full bg-brand-yellow rounded-full transition-all duration-500"
                      style={{ width: `${p.pct}%` }}
                    />
                  </div>
                  <span className="text-white/40 font-mono text-[10px] w-8 text-right">{p.pct}%</span>
                </div>
              ))}
            </div>
          )}

          {/* Contact Info */}
          <div className="flex flex-col gap-1.5">
            <div className="text-white/40 font-mono text-[10px] uppercase tracking-wider mb-0.5">Contact</div>
            {data.contact_email && (
              <div className="flex justify-between text-xs">
                <span className="text-white/40 font-mono uppercase">Email</span>
                <span className="text-brand-white font-mono">{data.contact_email}</span>
              </div>
            )}
            {data.manager_name && (
              <div className="flex justify-between text-xs">
                <span className="text-white/40 font-mono uppercase">Manager</span>
                <span className="text-brand-white font-mono">{data.manager_name}</span>
              </div>
            )}
            {data.rate_card_range && (
              <div className="flex justify-between text-xs">
                <span className="text-white/40 font-mono uppercase">Rate</span>
                <span className="text-brand-green font-mono font-bold">{data.rate_card_range}</span>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col gap-2 pt-1">
            <button
              onClick={(e) => { e.stopPropagation(); onPitch?.(data); console.log('PITCH', data); }}
              className="w-full py-2.5 bg-brand-pink text-brand-black font-display font-bold text-sm uppercase tracking-wider rounded-full hover:brightness-110 transition-all"
            >
              Pitch
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); onSave?.(data); console.log('SAVE', data); }}
              className="w-full py-2.5 bg-brand-yellow text-brand-black font-display font-bold text-sm uppercase tracking-wider rounded-full hover:brightness-110 transition-all"
            >
              Save
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); onDismiss?.(data); console.log('DISMISS', data); }}
              className="w-full py-2 bg-transparent border border-[#2A2A2A] text-white/40 font-mono text-xs uppercase tracking-wider rounded-full hover:border-white/30 hover:text-white/60 transition-all"
            >
              Dismiss
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}