import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PulseButton } from '../components';
import { fetchMissionHistory, fetchEarnings, getUserProfile } from '../services/osApi';

/**
 * IntelHub - Identity card + three tabs (Missions, Earnings, Replay)
 * Wireframe: Top identity card with rank, streak, earnings, percentile
 */
export default function IntelHub() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'missions' | 'earnings' | 'replay'>('missions');
  const [missions, setMissions] = useState<any[]>([]);
  const [earnings, setEarnings] = useState<any>({ total: 0, pending: 0, today: 0, week: 0 });
  const [profile, setProfile] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [missionHistory, earningsData, profileData] = await Promise.all([
        fetchMissionHistory(),
        fetchEarnings(),
        getUserProfile(),
      ]);
      setMissions(missionHistory);
      setEarnings(earningsData);
      setProfile(profileData);
    } catch (error) {
      console.error('Failed to load intel data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const formatCurrency = (amount: number) => {
    return `${amount.toFixed(2)} TND`;
  };

  if (isLoading) {
    return (
      <div style={{
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--war-black)',
        color: 'white',
      }}>
        <div style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '14px',
          color: 'var(--war-cyan)',
        }}>
          Loading intel...
        </div>
      </div>
    );
  }

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: 'var(--war-black)',
      color: 'white',
    }}>
      {/* Identity card */}
      <div style={{
        padding: '24px',
        background: 'linear-gradient(135deg, var(--war-purple)20, transparent)',
        borderBottom: '1px solid var(--war-gray-700)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            width: '60px',
            height: '60px',
            borderRadius: '50%',
            background: 'var(--gradient-cyber)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '24px',
            fontWeight: '900',
            color: 'white',
            border: '3px solid var(--war-black)',
            boxShadow: '0 0 20px var(--war-purple)',
          }}>
            {profile?.rank ? profile.rank.charAt(0) : 'E'}
          </div>

          <div style={{ flex: 1 }}>
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '12px',
              color: 'var(--si-muted)',
              marginBottom: '4px',
            }}>
              {profile?.tier || 'Local Explorer'} (Tier 2)
            </div>
            <div style={{
              fontFamily: 'var(--font-display)',
              fontSize: '28px',
              fontWeight: '900',
              marginBottom: '4px',
            }}>
              🔥 {formatCurrency(earnings.total)} earned
            </div>
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '12px',
              color: 'var(--war-cyan)',
            }}>
              Top {profile?.city_percentile || 12}% in Tunis
            </div>
          </div>
        </div>

        {/* Stats row */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '16px',
          marginTop: '20px',
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{
              fontFamily: 'var(--font-numbers)',
              fontSize: '20px',
              fontWeight: '900',
              color: 'var(--war-cyan)',
            }}>
              {profile?.streak || 5}
            </div>
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '11px',
              color: 'var(--si-muted)',
              textTransform: 'uppercase',
            }}>
              Streak
            </div>
          </div>

          <div style={{ textAlign: 'center' }}>
            <div style={{
              fontFamily: 'var(--font-numbers)',
              fontSize: '20px',
              fontWeight: '900',
              color: 'var(--war-green)',
            }}>
              {missions.length}
            </div>
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '11px',
              color: 'var(--si-muted)',
              textTransform: 'uppercase',
            }}>
              Missions
            </div>
          </div>

          <div style={{ textAlign: 'center' }}>
            <div style={{
              fontFamily: 'var(--font-numbers)',
              fontSize: '20px',
              fontWeight: '900',
              color: 'var(--war-yellow)',
            }}>
              {profile?.rank || 'E'}
            </div>
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '11px',
              color: 'var(--si-muted)',
              textTransform: 'uppercase',
            }}>
              Rank
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{
        display: 'flex',
        borderBottom: '1px solid var(--war-gray-800)',
        background: 'var(--war-gray-900)',
      }}>
        {(['missions', 'earnings', 'replay'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              flex: 1,
              padding: '16px',
              background: 'transparent',
              border: 'none',
              borderBottom: `2px solid ${activeTab === tab ? 'var(--war-cyan)' : 'transparent'}`,
              color: activeTab === tab ? 'var(--war-cyan)' : 'var(--si-muted)',
              fontFamily: 'var(--font-mono)',
              fontSize: '12px',
              fontWeight: '700',
              textTransform: 'uppercase',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            {tab === 'missions' && '📋 Missions'}
            {tab === 'earnings' && '💰 Earnings'}
            {tab === 'replay' && '🎥 Replay'}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px',
      }}>
        {activeTab === 'missions' && (
          <div>
            {missions.length === 0 ? (
              <div style={{
                padding: '40px',
                textAlign: 'center',
                color: 'var(--si-muted)',
                fontFamily: 'var(--font-mono)',
                fontSize: '14px',
              }}>
                No mission history yet
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {missions.map((mission) => (
                  <div
                    key={mission.id}
                    style={{
                      padding: '16px',
                      background: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid var(--war-gray-700)',
                      borderRadius: '12px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      transition: 'all 0.2s ease',
                      cursor: 'pointer',
                    }}
                    onClick={() => {
                      if (mission.trace_id) {
                        navigate(`/replay/${mission.trace_id}`);
                      }
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = 'rgba(139, 92, 246, 0.1)';
                      e.currentTarget.style.borderColor = 'var(--war-purple)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                      e.currentTarget.style.borderColor = 'var(--war-gray-700)';
                    }}
                  >
                    <div>
                      <div style={{
                        fontFamily: 'var(--font-display)',
                        fontSize: '16px',
                        fontWeight: '800',
                        marginBottom: '4px',
                      }}>
                        {mission.location}
                      </div>
                      <div style={{
                        fontFamily: 'var(--font-mono)',
                        fontSize: '11px',
                        color: 'var(--si-muted)',
                      }}>
                        {formatDate(mission.completed_at)}
                      </div>
                    </div>
                    <div style={{
                      fontFamily: 'var(--font-numbers)',
                      fontSize: '18px',
                      fontWeight: '900',
                      color: 'var(--war-green)',
                    }}>
                      +{mission.reward} TND
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'earnings' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{
              padding: '20px',
              background: 'rgba(0, 245, 255, 0.1)',
              border: '1px solid var(--war-cyan)',
              borderRadius: '12px',
            }}>
              <div style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '12px',
                color: 'var(--si-muted)',
                marginBottom: '8px',
                textTransform: 'uppercase',
              }}>
                Total Earnings
              </div>
              <div style={{
                fontFamily: 'var(--font-numbers)',
                fontSize: '36px',
                fontWeight: '900',
                color: 'var(--war-green)',
              }}>
                {formatCurrency(earnings.total)}
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {[
                { label: 'Today', value: earnings.today, color: 'var(--war-green)' },
                { label: 'This Week', value: earnings.week, color: 'var(--war-cyan)' },
                { label: 'Pending', value: earnings.pending, color: 'var(--war-yellow)' },
              ].map((item) => (
                <div
                  key={item.label}
                  style={{
                    padding: '16px',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid var(--war-gray-700)',
                    borderRadius: '12px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <div style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '14px',
                    fontWeight: '700',
                    color: 'white',
                  }}>
                    {item.label}
                  </div>
                  <div style={{
                    fontFamily: 'var(--font-numbers)',
                    fontSize: '20px',
                    fontWeight: '900',
                    color: item.color,
                  }}>
                    {formatCurrency(item.value)}
                  </div>
                </div>
              ))}
            </div>

            <div style={{ marginTop: '24px' }}>
              <PulseButton
                onClick={() => window.open('https://t.me/salesinject_bot', '_blank')}
                variant="secondary"
                size="medium"
              >
                💳 Withdraw Funds
              </PulseButton>
            </div>
          </div>
        )}

        {activeTab === 'replay' && (
          <div>
            {missions.length === 0 ? (
              <div style={{
                padding: '40px',
                textAlign: 'center',
                color: 'var(--si-muted)',
                fontFamily: 'var(--font-mono)',
                fontSize: '14px',
              }}>
                No missions to replay yet
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {missions.map((mission) => (
                  <div
                    key={mission.id}
                    style={{
                      padding: '16px',
                      background: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid var(--war-gray-700)',
                      borderRadius: '12px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <div>
                      <div style={{
                        fontFamily: 'var(--font-display)',
                        fontSize: '16px',
                        fontWeight: '800',
                        marginBottom: '4px',
                      }}>
                        {mission.location}
                      </div>
                      <div style={{
                        fontFamily: 'var(--font-mono)',
                        fontSize: '11px',
                        color: 'var(--si-muted)',
                      }}>
                        {formatDate(mission.completed_at)}
                      </div>
                    </div>
                    <button
                      onClick={() => {
                        if (mission.trace_id) {
                          navigate(`/replay/${mission.trace_id}`);
                        }
                      }}
                      style={{
                        padding: '8px 16px',
                        background: 'var(--gradient-cyber)',
                        border: 'none',
                        borderRadius: '8px',
                        color: 'white',
                        fontFamily: 'var(--font-mono)',
                        fontSize: '12px',
                        fontWeight: '700',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                      }}
                    >
                      <span>▶</span>
                      <span>Replay</span>
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Bottom navigation hint */}
      <div style={{
        padding: '12px 24px',
        borderTop: '1px solid var(--war-gray-700)',
        textAlign: 'center',
        fontFamily: 'var(--font-mono)',
        fontSize: '11px',
        color: 'var(--si-muted)',
      }}>
        Swipe between tabs • Tap mission to view details
      </div>
    </div>
  );
}