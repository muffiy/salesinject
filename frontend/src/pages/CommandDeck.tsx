import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PulseButton, CostMeter, UncertaintyBar, ActionStreakCounter } from '../components';
import { launchMission, getMissionTypes, getAgentMarket, getPredictedOutcome, getActiveMissions } from '../services/osApi';
import type { MissionLaunchRequest } from '../services/osApi';

/**
 * CommandDeck – The ONLY action surface (replaces MissionControl + partial Tasks)
 * Purpose: Launch missions, select agent, see predicted outcome, and start the dopamine loop.
 */
export function CommandDeck() {
  const navigate = useNavigate();

  // State for mission configuration
  const [selectedMissionType, setSelectedMissionType] = useState<string>('scout');
  const [selectedAgent, setSelectedAgent] = useState<string>('auto');
  const [budget, setBudget] = useState<number>(0.5);
  const [isLaunching, setIsLaunching] = useState(false);

  // Data from API
  const [missionTypes, setMissionTypes] = useState<Array<{ id: string; name: string; description: string }>>([]);
  const [agents, setAgents] = useState<Array<{ name: string; success_rate: number; speed: number; stake: number; score: number }>>([]);
  const [recentMissions, setRecentMissions] = useState<any[]>([]);
  const [prediction, setPrediction] = useState<{ win_probability: number; expected_cost: number; estimated_rank_change: number } | null>(null);

  // Load initial data
  useEffect(() => {
    loadInitialData();
  }, []);

  // Update prediction when configuration changes
  useEffect(() => {
    updatePrediction();
  }, [selectedMissionType, selectedAgent, budget]);

  const loadInitialData = async () => {
    try {
      const [types, market, missions] = await Promise.all([
        getMissionTypes(),
        getAgentMarket(),
        getActiveMissions(),
      ]);

      setMissionTypes(types);
      setAgents(market);
      // Filter to only recent completed missions
      setRecentMissions(missions.slice(0, 3));
    } catch (error) {
      console.error('Failed to load initial data:', error);
    }
  };

  const updatePrediction = async () => {
    try {
      const prediction = await getPredictedOutcome(
        selectedMissionType,
        selectedAgent === 'auto' ? undefined : selectedAgent
      );
      setPrediction(prediction);
    } catch (error) {
      console.error('Failed to get prediction:', error);
    }
  };

  const handleLaunchMission = async () => {
    setIsLaunching(true);
    try {
      const payload = {
        budget,
        // Add more mission-specific payload here
      };

      const response = await launchMission(
        selectedMissionType as MissionLaunchRequest['mission_type'],
        payload,
        selectedAgent === 'auto' ? undefined : selectedAgent
      );

      // Redirect to WarRoom with trace_id
      navigate(`/warroom?trace_id=${response.trace_id}`);
    } catch (error) {
      console.error('Failed to launch mission:', error);
      alert('Failed to launch mission. Please try again.');
    } finally {
      setIsLaunching(false);
    }
  };

  // Mock streak data - would come from user profile
  const streakCount = 5;
  const maxStreak = 12;

  return (
    <div style={{
      padding: '32px 24px',
      background: 'var(--war-black)',
      color: 'white',
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      gap: '32px',
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '16px',
      }}>
        <div>
          <h1 style={{
            fontFamily: 'var(--font-display)',
            fontSize: '48px',
            fontWeight: '900',
            color: 'var(--war-cyan)',
            marginBottom: '8px',
            textTransform: 'uppercase',
          }}>
            COMMAND DECK
          </h1>
          <p style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '14px',
            color: 'var(--si-muted)',
          }}>
            Launch missions, select your agent, predict outcomes.
          </p>
        </div>

        <ActionStreakCounter
          streakCount={streakCount}
          maxStreak={maxStreak}
          size="medium"
        />
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '32px',
      }}>
        {/* Left column: Mission configuration */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '24px',
        }}>
          {/* Mission type selector */}
          <div className="card-glass" style={{ padding: '24px' }}>
            <h2 style={{
              fontFamily: 'var(--font-display)',
              fontSize: '20px',
              fontWeight: '800',
              color: 'var(--war-cyan)',
              marginBottom: '20px',
              textTransform: 'uppercase',
            }}>
              MISSION TYPE
            </h2>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gap: '12px',
            }}>
              {missionTypes.map((type) => (
                <button
                  key={type.id}
                  onClick={() => setSelectedMissionType(type.id)}
                  style={{
                    padding: '16px 12px',
                    background: selectedMissionType === type.id
                      ? 'var(--gradient-cyber)'
                      : 'rgba(255, 255, 255, 0.05)',
                    border: `2px solid ${selectedMissionType === type.id ? 'var(--war-purple)' : 'var(--war-gray-700)'}`,
                    borderRadius: '12px',
                    color: 'white',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '12px',
                    fontWeight: '700',
                    textTransform: 'uppercase',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '8px',
                  }}
                >
                  <span style={{ fontSize: '24px' }}>
                    {type.id === 'scout' ? '🔍' :
                     type.id === 'ammo_generation' ? '⚔️' : '🎯'}
                  </span>
                  <span>{type.name}</span>
                </button>
              ))}
            </div>

            <div style={{
              marginTop: '16px',
              padding: '12px',
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid var(--war-gray-700)',
              borderRadius: '8px',
              fontFamily: 'var(--font-body)',
              fontSize: '13px',
              color: 'var(--si-muted)',
            }}>
              {missionTypes.find(t => t.id === selectedMissionType)?.description}
            </div>
          </div>

          {/* Agent selector */}
          <div className="card-glass" style={{ padding: '24px' }}>
            <h2 style={{
              fontFamily: 'var(--font-display)',
              fontSize: '20px',
              fontWeight: '800',
              color: 'var(--war-cyan)',
              marginBottom: '20px',
              textTransform: 'uppercase',
            }}>
              AGENT SELECTION
            </h2>

            <div style={{ marginBottom: '16px' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                marginBottom: '12px',
              }}>
                <input
                  type="radio"
                  id="auto-agent"
                  checked={selectedAgent === 'auto'}
                  onChange={() => setSelectedAgent('auto')}
                />
                <label htmlFor="auto-agent" style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '14px',
                  fontWeight: '700',
                  color: 'white',
                }}>
                  AUTO MODE (Selects best agent for mission)
                </label>
              </div>

              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
              }}>
                <input
                  type="radio"
                  id="manual-agent"
                  checked={selectedAgent !== 'auto'}
                  onChange={() => setSelectedAgent(agents[0]?.name || '')}
                />
                <label htmlFor="manual-agent" style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '14px',
                  fontWeight: '700',
                  color: 'white',
                }}>
                  MANUAL SELECTION
                </label>
              </div>
            </div>

            {selectedAgent !== 'auto' && (
              <select
                value={selectedAgent}
                onChange={(e) => setSelectedAgent(e.target.value)}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  background: 'rgba(0, 0, 0, 0.5)',
                  border: '2px solid var(--war-cyan)',
                  borderRadius: '8px',
                  color: 'white',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '14px',
                  marginTop: '12px',
                }}
              >
                {agents.map((agent) => (
                  <option key={agent.name} value={agent.name}>
                    {agent.name} (Score: {agent.score.toFixed(1)}, Success: {(agent.success_rate * 100).toFixed(0)}%)
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Budget slider */}
          <div className="card-glass" style={{ padding: '24px' }}>
            <h2 style={{
              fontFamily: 'var(--font-display)',
              fontSize: '20px',
              fontWeight: '800',
              color: 'var(--war-cyan)',
              marginBottom: '20px',
              textTransform: 'uppercase',
            }}>
              BUDGET ALLOCATION
            </h2>

            <div style={{ marginBottom: '20px' }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: '8px',
              }}>
                <span style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '12px',
                  color: 'var(--si-muted)',
                }}>
                  Budget: ${budget.toFixed(2)}
                </span>
                <span style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '12px',
                  color: 'var(--si-muted)',
                }}>
                  Range: $0.01 – $1.00
                </span>
              </div>

              <input
                type="range"
                min="0.01"
                max="1.00"
                step="0.01"
                value={budget}
                onChange={(e) => setBudget(parseFloat(e.target.value))}
                style={{
                  width: '100%',
                  height: '8px',
                  background: 'var(--gradient-cyber)',
                  borderRadius: '4px',
                  appearance: 'none',
                  outline: 'none',
                }}
              />

              <CostMeter
                cost={budget}
                maxCost={1.0}
                size="medium"
                warningThreshold={70}
                criticalThreshold={90}
              />
            </div>

            <div style={{
              padding: '12px',
              background: 'rgba(0, 245, 255, 0.05)',
              border: '1px solid var(--war-cyan)',
              borderRadius: '8px',
              fontFamily: 'var(--font-mono)',
              fontSize: '12px',
              color: 'var(--war-cyan)',
            }}>
              Higher budgets increase mission success probability but consume more resources.
            </div>
          </div>

          {/* Launch button */}
          <PulseButton
            onClick={handleLaunchMission}
            disabled={isLaunching}
            pulse={!isLaunching}
            size="large"
            variant="primary"
          >
            {isLaunching ? 'LAUNCHING...' : 'START OPERATION'}
          </PulseButton>
        </div>

        {/* Right column: Prediction and recent missions */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '24px',
        }}>
          {/* Prediction card */}
          <div className="card-glass" style={{ padding: '24px' }}>
            <h2 style={{
              fontFamily: 'var(--font-display)',
              fontSize: '20px',
              fontWeight: '800',
              color: 'var(--war-cyan)',
              marginBottom: '20px',
              textTransform: 'uppercase',
            }}>
              PREDICTED OUTCOME
            </h2>

            {prediction ? (
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '20px',
              }}>
                <div>
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '8px',
                  }}>
                    <span style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '13px',
                      color: 'var(--si-muted)',
                    }}>
                      Win Probability
                    </span>
                    <span style={{
                      fontFamily: 'var(--font-numbers)',
                      fontSize: '20px',
                      fontWeight: '900',
                      color: prediction.win_probability > 0.7 ? 'var(--war-green)' :
                             prediction.win_probability > 0.4 ? 'var(--war-yellow)' : 'var(--war-red)',
                    }}>
                      {(prediction.win_probability * 100).toFixed(1)}%
                    </span>
                  </div>
                  <UncertaintyBar
                    probability={prediction.win_probability}
                    height={20}
                    showLabel={false}
                  />
                </div>

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '16px',
                }}>
                  <div style={{
                    padding: '16px',
                    background: 'rgba(0, 0, 0, 0.3)',
                    border: '1px solid var(--war-gray-700)',
                    borderRadius: '12px',
                  }}>
                    <div style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '11px',
                      color: 'var(--si-muted)',
                      marginBottom: '4px',
                    }}>
                      Expected Cost
                    </div>
                    <div style={{
                      fontFamily: 'var(--font-numbers)',
                      fontSize: '24px',
                      fontWeight: '900',
                      color: 'var(--war-cyan)',
                    }}>
                      ${prediction.expected_cost.toFixed(2)}
                    </div>
                  </div>

                  <div style={{
                    padding: '16px',
                    background: 'rgba(0, 0, 0, 0.3)',
                    border: '1px solid var(--war-gray-700)',
                    borderRadius: '12px',
                  }}>
                    <div style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '11px',
                      color: 'var(--si-muted)',
                      marginBottom: '4px',
                    }}>
                      Rank Change
                    </div>
                    <div style={{
                      fontFamily: 'var(--font-numbers)',
                      fontSize: '24px',
                      fontWeight: '900',
                      color: prediction.estimated_rank_change > 0 ? 'var(--war-green)' : 'var(--war-red)',
                    }}>
                      {prediction.estimated_rank_change > 0 ? '+' : ''}{prediction.estimated_rank_change}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div style={{
                padding: '40px',
                textAlign: 'center',
                color: 'var(--si-muted)',
                fontFamily: 'var(--font-mono)',
                fontSize: '14px',
              }}>
                Loading prediction...
              </div>
            )}
          </div>

          {/* Recent missions preview */}
          <div className="card-glass" style={{ padding: '24px' }}>
            <h2 style={{
              fontFamily: 'var(--font-display)',
              fontSize: '20px',
              fontWeight: '800',
              color: 'var(--war-cyan)',
              marginBottom: '20px',
              textTransform: 'uppercase',
            }}>
              RECENT MISSIONS
            </h2>

            {recentMissions.length > 0 ? (
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
              }}>
                {recentMissions.map((mission, index) => (
                  <div
                    key={mission.trace_id || index}
                    style={{
                      padding: '12px 16px',
                      background: 'rgba(0, 0, 0, 0.3)',
                      border: '1px solid var(--war-gray-700)',
                      borderRadius: '8px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      transition: 'all 0.2s ease',
                      cursor: 'pointer',
                    }}
                    onClick={() => navigate(`/replay/${mission.trace_id}`)}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = 'rgba(139, 92, 246, 0.1)';
                      e.currentTarget.style.borderColor = 'var(--war-purple)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'rgba(0, 0, 0, 0.3)';
                      e.currentTarget.style.borderColor = 'var(--war-gray-700)';
                    }}
                  >
                    <div>
                      <div style={{
                        fontFamily: 'var(--font-mono)',
                        fontSize: '12px',
                        fontWeight: '700',
                        color: 'white',
                        textTransform: 'uppercase',
                      }}>
                        {mission.mission_type || 'Unknown'}
                      </div>
                      <div style={{
                        fontFamily: 'var(--font-mono)',
                        fontSize: '10px',
                        color: 'var(--si-muted)',
                      }}>
                        {new Date(mission.started_at || Date.now()).toLocaleDateString()}
                      </div>
                    </div>

                    <div style={{
                      padding: '4px 8px',
                      background: mission.status === 'completed' ? 'var(--war-green)20' :
                                 mission.status === 'failed' ? 'var(--war-red)20' : 'var(--war-yellow)20',
                      border: `1px solid ${mission.status === 'completed' ? 'var(--war-green)' :
                               mission.status === 'failed' ? 'var(--war-red)' : 'var(--war-yellow)'}`,
                      borderRadius: '4px',
                      fontFamily: 'var(--font-mono)',
                      fontSize: '10px',
                      fontWeight: '700',
                      color: mission.status === 'completed' ? 'var(--war-green)' :
                             mission.status === 'failed' ? 'var(--war-red)' : 'var(--war-yellow)',
                    }}>
                      {mission.status?.toUpperCase() || 'UNKNOWN'}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{
                padding: '20px',
                textAlign: 'center',
                color: 'var(--si-muted)',
                fontFamily: 'var(--font-mono)',
                fontSize: '13px',
              }}>
                No recent missions. Launch your first operation!
              </div>
            )}

            <button
              onClick={() => navigate('/intel')}
              style={{
                width: '100%',
                marginTop: '16px',
                padding: '12px',
                background: 'transparent',
                border: '1px solid var(--war-gray-700)',
                color: 'var(--si-muted)',
                fontFamily: 'var(--font-mono)',
                fontSize: '12px',
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
              VIEW ALL MISSIONS →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}