import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PulseButton, ShareButton } from '../components';
import { getReplay } from '../services/osApi';

/**
 * LoopEngine - Mission replay with timeline, highlight reel, share button
 * Wireframe: Step-by-step timeline, highlight reel, share, re-run
 */
export default function LoopEngine() {
  const { traceId } = useParams<{ traceId: string }>();
  const navigate = useNavigate();
  const [mission, setMission] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSharing, setIsSharing] = useState(false);
  const [activeStep, setActiveStep] = useState<number>(0);

  useEffect(() => {
    if (traceId) {
      loadMissionReplay();
    }
  }, [traceId]);

  const loadMissionReplay = async () => {
    setIsLoading(true);
    try {
      const missionData = await getReplay(traceId!);
      setMission(missionData);
    } catch (error) {
      console.error('Failed to load mission replay:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleShare = (url: string) => {
    console.log('Shared URL:', url);
    setIsSharing(true);
    setTimeout(() => setIsSharing(false), 2000);
  };

  const handleReRun = () => {
    // In real app, this would relaunch a similar mission
    alert('Mission re-run feature coming soon!');
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
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
          Loading replay...
        </div>
      </div>
    );
  }

  if (!mission) {
    return (
      <div style={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
        background: 'var(--war-black)',
        color: 'white',
        textAlign: 'center',
      }}>
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>📺</div>
        <h2 style={{
          fontFamily: 'var(--font-display)',
          fontSize: '24px',
          fontWeight: '800',
          marginBottom: '12px',
        }}>
          Replay Not Found
        </h2>
        <p style={{
          fontFamily: 'var(--font-body)',
          fontSize: '14px',
          color: 'var(--si-muted)',
          marginBottom: '32px',
        }}>
          This mission replay is no longer available.
        </p>
        <PulseButton
          onClick={() => navigate('/')}
          variant="primary"
          size="medium"
        >
          ← Back to Missions
        </PulseButton>
      </div>
    );
  }

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      padding: '24px',
      background: 'var(--war-black)',
      color: 'white',
      overflowY: 'auto',
    }}>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <button
          onClick={() => navigate(-1)}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--war-cyan)',
            fontFamily: 'var(--font-mono)',
            fontSize: '14px',
            fontWeight: '700',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '16px',
          }}
        >
          ← Back
        </button>

        <h2 style={{
          fontFamily: 'var(--font-display)',
          fontSize: '32px',
          fontWeight: '800',
          marginBottom: '8px',
        }}>
          {mission.mission_type || 'Mission'} Replay
        </h2>

        <div style={{
          fontFamily: 'var(--font-numbers)',
          fontSize: '24px',
          fontWeight: '900',
          color: 'var(--war-green)',
        }}>
          +{mission.total_cost || mission.reward || 0} TND
        </div>
      </div>

      {/* Timeline */}
      <div style={{ marginBottom: '32px' }}>
        <h3 style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '14px',
          color: 'var(--si-muted)',
          marginBottom: '16px',
          textTransform: 'uppercase',
        }}>
          MISSION TIMELINE
        </h3>

        {mission.steps && mission.steps.length > 0 ? (
          <div style={{ position: 'relative', paddingLeft: '24px' }}>
            {/* Vertical line */}
            <div style={{
              position: 'absolute',
              left: '10px',
              top: '0',
              bottom: '0',
              width: '2px',
              background: 'var(--war-gray-700)',
            }} />

            {mission.steps.map((step: any, index: number) => (
              <div
                key={step.node_id || index}
                style={{
                  position: 'relative',
                  marginBottom: '24px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  opacity: activeStep >= index ? 1 : 0.6,
                }}
                onClick={() => setActiveStep(index)}
                onMouseEnter={(e) => {
                  e.currentTarget.style.opacity = '1';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.opacity = activeStep >= index ? 1 : 0.6;
                }}
              >
                {/* Step indicator */}
                <div style={{
                  position: 'absolute',
                  left: '-24px',
                  top: '0',
                  width: '20px',
                  height: '20px',
                  borderRadius: '50%',
                  background: step.success === false
                    ? 'var(--war-red)'
                    : activeStep >= index
                    ? 'var(--war-cyan)'
                    : 'var(--war-gray-700)',
                  border: '2px solid var(--war-black)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '10px',
                  fontWeight: '900',
                  color: 'white',
                  zIndex: 1,
                }}>
                  {step.success === false ? '✗' : '✓'}
                </div>

                {/* Step content */}
                <div style={{
                  padding: '16px',
                  background: activeStep === index
                    ? 'rgba(0, 245, 255, 0.1)'
                    : 'rgba(255, 255, 255, 0.05)',
                  border: `1px solid ${activeStep === index ? 'var(--war-cyan)' : 'var(--war-gray-700)'}`,
                  borderRadius: '12px',
                }}>
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    marginBottom: '8px',
                  }}>
                    <div style={{
                      fontFamily: 'var(--font-display)',
                      fontSize: '16px',
                      fontWeight: '800',
                      color: step.success === false ? 'var(--war-red)' : 'white',
                    }}>
                      {step.node_type || `Step ${index + 1}`}
                    </div>
                    <div style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '11px',
                      color: 'var(--si-muted)',
                    }}>
                      {formatTime(step.timestamp)}
                    </div>
                  </div>

                  <div style={{
                    fontFamily: 'var(--font-body)',
                    fontSize: '14px',
                    color: 'var(--si-muted)',
                    marginBottom: '8px',
                  }}>
                    {step.result?.message || step.result || 'Step completed'}
                  </div>

                  {step.cost && (
                    <div style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                      padding: '4px 8px',
                      background: 'rgba(0, 0, 0, 0.3)',
                      borderRadius: '4px',
                      fontFamily: 'var(--font-mono)',
                      fontSize: '11px',
                      color: 'var(--war-yellow)',
                    }}>
                      <span>⚡</span>
                      <span>Cost: {step.cost} TND</span>
                    </div>
                  )}

                  {step.rank_impact && step.rank_impact !== 0 && (
                    <div style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                      padding: '4px 8px',
                      marginLeft: '8px',
                      background: 'rgba(0, 0, 0, 0.3)',
                      borderRadius: '4px',
                      fontFamily: 'var(--font-mono)',
                      fontSize: '11px',
                      color: step.rank_impact > 0 ? 'var(--war-green)' : 'var(--war-red)',
                    }}>
                      <span>{step.rank_impact > 0 ? '↑' : '↓'}</span>
                      <span>Rank: {step.rank_impact > 0 ? '+' : ''}{step.rank_impact}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{
            padding: '24px',
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid var(--war-gray-700)',
            borderRadius: '12px',
            textAlign: 'center',
          }}>
            <div style={{ fontSize: '32px', marginBottom: '12px' }}>📊</div>
            <div style={{
              fontFamily: 'var(--font-body)',
              fontSize: '14px',
              color: 'var(--si-muted)',
            }}>
              No detailed timeline available for this mission
            </div>
          </div>
        )}
      </div>

      {/* Highlight reel */}
      {mission.steps && mission.steps.some((s: any) => s.success) && (
        <div style={{ marginBottom: '32px' }}>
          <h3 style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '14px',
            color: 'var(--si-muted)',
            marginBottom: '16px',
            textTransform: 'uppercase',
          }}>
            HIGHLIGHT REEL
          </h3>

          <div style={{
            padding: '20px',
            background: 'var(--gradient-cyber)20',
            border: '1px solid var(--war-purple)',
            borderRadius: '12px',
            textAlign: 'center',
          }}>
            <div style={{ fontSize: '48px', marginBottom: '12px' }}>🎬</div>
            <div style={{
              fontFamily: 'var(--font-display)',
              fontSize: '18px',
              fontWeight: '800',
              marginBottom: '8px',
            }}>
              Best Moment
            </div>
            <div style={{
              fontFamily: 'var(--font-body)',
              fontSize: '14px',
              color: 'var(--si-muted)',
              marginBottom: '16px',
            }}>
              Mission completed successfully with rank increase!
            </div>
            <button
              onClick={() => {
                const bestStep = mission.steps.find((s: any) => s.success);
                if (bestStep) {
                  setActiveStep(mission.steps.indexOf(bestStep));
                }
              }}
              style={{
                padding: '8px 16px',
                background: 'var(--gradient-rage)',
                border: 'none',
                borderRadius: '8px',
                color: 'white',
                fontFamily: 'var(--font-mono)',
                fontSize: '12px',
                fontWeight: '700',
                cursor: 'pointer',
              }}
            >
              WATCH HIGHLIGHT
            </button>
          </div>
        </div>
      )}

      {/* Actions */}
      <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', gap: '12px' }}>
          <div style={{ flex: 1 }}>
            <ShareButton
              traceId={traceId!}
              variant="primary"
              size="medium"
              message={`Check out my mission replay! ${window.location.href}`}
              onShare={handleShare}
            />
          </div>
          <div style={{ flex: 1 }}>
            <PulseButton
              onClick={handleReRun}
              variant="secondary"
              size="medium"
            >
              🔄 Re-run Mission
            </PulseButton>
          </div>
        </div>

        <button
          onClick={() => navigate('/intel')}
          style={{
            width: '100%',
            padding: '12px',
            background: 'transparent',
            border: '1px solid var(--war-gray-700)',
            borderRadius: '12px',
            color: 'var(--si-muted)',
            fontFamily: 'var(--font-mono)',
            fontSize: '13px',
            fontWeight: '700',
            cursor: 'pointer',
            textTransform: 'uppercase',
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(139, 92, 246, 0.1)';
            e.currentTarget.style.color = 'white';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'transparent';
            e.currentTarget.style.color = 'var(--si-muted)';
          }}
        >
          View All Missions
        </button>
      </div>

      {/* Summary */}
      <div style={{
        marginTop: '24px',
        padding: '16px',
        background: 'rgba(0, 0, 0, 0.3)',
        border: '1px solid var(--war-gray-700)',
        borderRadius: '12px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <div>
          <div style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '11px',
            color: 'var(--si-muted)',
            marginBottom: '4px',
            textTransform: 'uppercase',
          }}>
            Total Impact
          </div>
          <div style={{
            fontFamily: 'var(--font-numbers)',
            fontSize: '20px',
            fontWeight: '900',
            color: mission.final_rank_change > 0 ? 'var(--war-green)' : 'var(--war-red)',
          }}>
            Rank {mission.final_rank_change > 0 ? '+' : ''}{mission.final_rank_change || 0}
          </div>
        </div>
        <div>
          <div style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '11px',
            color: 'var(--si-muted)',
            marginBottom: '4px',
            textTransform: 'uppercase',
          }}>
            Mission Date
          </div>
          <div style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '14px',
            fontWeight: '700',
            color: 'white',
          }}>
            {new Date(mission.created_at).toLocaleDateString()}
          </div>
        </div>
      </div>
    </div>
  );
}