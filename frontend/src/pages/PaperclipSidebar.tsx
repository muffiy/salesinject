import { useEffect, useState } from 'react';
import { getPaperclips } from '../services/api';
import { ContactDetailCard } from '../components/ContactDetailCard';
import type { ContactProfileData } from '../components/ContactDetailCard';

export interface PaperclipItemData {
  id: string;
  task_id: string | null;
  item_type: 'mission_log' | 'pinned_profile' | 'ad_copy' | string;
  content: any;
  created_at: string;
}

export function PaperclipSidebar() {
  const [items, setItems] = useState<PaperclipItemData[]>([]);
  const [loading, setLoading] = useState(true);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  useEffect(() => {
    localStorage.setItem('salesinject_last_viewed_paperclips', new Date().toISOString());
    window.dispatchEvent(new Event('paperclipsViewed'));

    getPaperclips()
      .then((data) => {
        setItems(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load paperclips', err);
        setLoading(false);
      });
  }, []);

  const formatDate = (ds: string) => {
    const d = new Date(ds);
    return `${d.toLocaleDateString()} ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
  };

  const handleCopy = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      console.log('Copy to clipboard requires a secure context (or use fallback).');
    }
  };

  const chipColor = (idx: number) => {
    const colors = ['text-brand-yellow border-brand-yellow', 'text-brand-pink border-brand-pink', 'text-brand-green border-brand-green'];
    return colors[idx % colors.length];
  };

  if (loading) {
    return (
      <div className="p-5 flex flex-col gap-4">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="animate-pulse bg-white/[0.03] border border-[#2A2A2A] rounded-xl"
            style={{ height: i === 1 ? 80 : i === 2 ? 60 : 120 }}
          />
        ))}
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center flex-1 min-h-[400px] text-center px-6 opacity-60">
        <div className="text-4xl mb-4">📭</div>
        <div className="font-mono text-[13px] font-bold text-brand-yellow tracking-wide uppercase">
          No Intel Yet — Run a Scout Mission
        </div>
      </div>
    );
  }

  return (
    <div className="p-5 flex-1 bg-brand-bg min-h-full">
      <h2 className="font-display text-2xl font-extrabold text-brand-yellow mb-6 uppercase tracking-tight">
        Intelligence Feed
      </h2>

      <div className="flex flex-col gap-4">
        {items.map((item) => {
          switch (item.item_type) {
            case 'mission_log':
              return (
                <div
                  key={item.id}
                  className="p-4 bg-brand-card border border-[#2A2A2A] rounded-2xl border-l-4 border-l-brand-yellow"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-base">📡</span>
                    <span className="font-mono text-[11px] text-brand-yellow font-bold uppercase tracking-wider">
                      Mission Log
                    </span>
                    <span className="ml-auto font-mono text-[10px] text-white/40">
                      {formatDate(item.created_at)}
                    </span>
                  </div>
                  <p className="text-[13px] text-brand-white leading-relaxed">
                    {item.content.report || JSON.stringify(item.content)}
                  </p>
                  {item.content.tags && (
                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {item.content.tags.map((tag: string, i: number) => (
                        <span
                          key={tag}
                          className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${chipColor(i)}`}
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              );

            case 'pinned_profile': {
              const profileData: ContactProfileData = {
                handle: item.content.handle,
                display_name: item.content.display_name,
                bio: item.content.bio,
                avatar_url: item.content.avatar_url,
                niche: item.content.niche,
                followers: item.content.followers,
                engagement_pct: item.content.engagement,
                platforms: item.content.platforms,
                contact_email: item.content.contact_email,
                manager_name: item.content.manager_name,
                rate_card_range: item.content.rate_card_range,
                recent_content_thumbnails: item.content.recent_content_thumbnails,
              };
              return <ContactDetailCard key={item.id} data={profileData} />;
            }

            case 'ad_copy':
              return (
                <div
                  key={item.id}
                  className="p-4 bg-brand-card border border-[#2A2A2A] rounded-2xl border-l-4 border-l-brand-pink"
                >
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-sm">📝</span>
                    <span className="font-mono text-[11px] text-brand-pink font-bold uppercase tracking-wider">
                      Ad Copy Draft
                    </span>
                    <span className="ml-auto font-mono text-[10px] text-white/40">
                      {formatDate(item.created_at)}
                    </span>
                  </div>

                  <div className="bg-[#1A1A1A] border border-[#2A2A2A] rounded-xl p-3 mb-4">
                    <pre className="text-[13px] text-brand-white leading-relaxed whitespace-pre-wrap font-body">
                      {item.content.draft || JSON.stringify(item.content)}
                    </pre>
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => handleCopy(item.content.draft || '', item.id)}
                      className={`flex-1 py-2 rounded-full font-mono text-xs font-bold uppercase tracking-wider border transition-all ${
                        copiedId === item.id
                          ? 'bg-brand-green text-brand-black border-brand-green'
                          : 'bg-transparent text-brand-pink border-brand-pink hover:bg-brand-pink/10'
                      }`}
                    >
                      {copiedId === item.id ? 'Copied' : 'Copy'}
                    </button>
                    <button
                      onClick={() => console.log('DEPLOY', item.content)}
                      className="flex-1 py-2 bg-brand-green text-brand-black font-display font-bold text-xs uppercase tracking-wider rounded-full hover:brightness-110 transition-all"
                    >
                      Deploy Asset
                    </button>
                  </div>
                </div>
              );

            default:
              return (
                <div
                  key={item.id}
                  className="p-3 bg-brand-card border border-[#2A2A2A] rounded-xl"
                >
                  <span className="font-mono text-[10px] text-white/40 uppercase">{item.item_type}</span>
                  <p className="text-[12px] text-white/70 mt-1 font-mono">{JSON.stringify(item.content)}</p>
                </div>
              );
          }
        })}
      </div>
    </div>
  );
}