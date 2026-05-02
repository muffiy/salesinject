import React, { useState, useEffect, useRef } from 'react';

interface HighlightStep {
  id: string;
  title: string;
  description: string;
  timestamp: string;
  impact: 'high' | 'medium' | 'low';
  rankChange?: number;
}

interface ReplayHighlightReelProps {
  /** Mission trace ID */
  traceId: string;
  /** Highlight steps (auto-generated if not provided) */
  highlights?: HighlightStep[];
  /** Auto-play the reel */
  autoPlay?: boolean;
  /** Loop the reel */
  loop?: boolean;
  /** Callback when a step is clicked */
  onStepClick?: (step: HighlightStep) => void;
  /** Callback when reel ends */
  onEnd?: () => void;
}

/**
 * Auto‑loop of best moment from a mission
 * Used in LoopEngine
 */
export function ReplayHighlightReel({
  traceId,
  highlights,
  autoPlay = true,
  loop = false,
  onStepClick,
  onEnd,
}: ReplayHighlightReelProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(autoPlay);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Use provided highlights or generate mock data
  const reelHighlights = highlights || generateMockHighlights(traceId);

  // Auto-play logic
  useEffect(() => {
    if (isPlaying && reelHighlights.length > 0) {
      if (intervalRef.current) clearInterval(intervalRef.current);

      intervalRef.current = setInterval(() => {
        setCurrentStep((prev) => {
          const next = prev + 1;
          if (next >= reelHighlights.length) {
            if (loop) {
              return 0;
            } else {
              setIsPlaying(false);
              onEnd?.();
              return prev;
            }
          }
          return next;
        });
      }, 3000); // 3 seconds per step

      return () => {
        if (intervalRef.current) clearInterval(intervalRef.current);
      };
    }
  }, [isPlaying, reelHighlights.length, loop, onEnd]);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleStepSelect = (index: number) => {
    setCurrentStep(index);
    if (onStepClick && reelHighlights[index]) {
      onStepClick(reelHighlights[index]);
    }
  };

  if (reelHighlights.length === 0) {
    return (
      <div style={{
        padding: '32px',
        background: 'var(--war-gray-900)',
        border: '2px dashed var(--war-gray-700)',
        borderRadius: '16px',
        textAlign: 'center',
        color: 'var(--si-muted)',
        fontFamily: 'var(--font-mono)',
        fontSize: '14px',
      }}>
        No highlights found for this mission.
      </div>
    );
  }

  const currentHighlight = reelHighlights[currentStep];
  const impactColor = {
    high: 'var(--war-red)',
    medium: 'var(--war-yellow)',
    low: 'var(--war-cyan)',
  }[currentHighlight.impact];

  return (
    <div style={{
      position: 'relative',
      background: 'rgba(26, 26, 26, 0.8)',
      backdropFilter: 'blur(20px)',
      border: '3px solid var(--war-purple)',
      borderRadius: '20px',
      overflow: 'hidden',
      padding: '24px',
    }}>
      {/* Header with controls */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px',
      }}>
        <div style={{
          fontFamily: 'var(--font-display)',
          fontSize: '20px',
          fontWeight: '900',
          color: 'white',
          textTransform: 'uppercase',
        }}>
          HIGHLIGHT REEL
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '12px',
            color: 'var(--si-muted)',
          }}>
            {currentStep + 1} / {reelHighlights.length}
          </div>

          <button
            onClick={handlePlayPause}
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              background: 'var(--gradient-rage)',
              border: 'none',
              color: 'white',
              fontSize: '18px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {isPlaying ? '⏸️' : '▶️'}
          </button>
        </div>
      </div>

      {/* Current highlight display */}
      <div style={{
        position: 'relative',
        height: '200px',
        background: 'rgba(0, 0, 0, 0.5)',
        borderRadius: '12px',
        overflow: 'hidden',
        marginBottom: '24px',
        border: `2px solid ${impactColor}`,
      }}>
        {/* Simulated mission visualization */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `linear-gradient(135deg, ${impactColor}20, transparent)`,
        }} />

        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center',
          padding: '20px',
        }}>
          <div style={{
            fontFamily: 'var(--font-display)',
            fontSize: '32px',
            fontWeight: '900',
            color: impactColor,
            marginBottom: '12px',
            textShadow: `0 0 20px ${impactColor}`,
          }}>
            {currentHighlight.title}
          </div>
          <div style={{
            fontFamily: 'var(--font-body)',
            fontSize: '16px',
            color: 'white',
            marginBottom: '16px',
            maxWidth: '600px',
          }}>
            {currentHighlight.description}
          </div>
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '16px',
          }}>
            <div style={{
              padding: '8px 16px',
              background: 'rgba(0, 0, 0, 0.5)',
              border: `1px solid ${impactColor}`,
              borderRadius: '8px',
              fontFamily: 'var(--font-mono)',
              fontSize: '12px',
              color: 'white',
            }}>
              {currentHighlight.timestamp}
            </div>
            {currentHighlight.rankChange !== undefined && (
              <div style={{
                padding: '8px 16px',
                background: 'rgba(0, 0, 0, 0.5)',
                border: '1px solid var(--war-green)',
                borderRadius: '8px',
                fontFamily: 'var(--font-numbers)',
                fontSize: '12px',
                fontWeight: '900',
                color: 'var(--war-green)',
              }}>
                RANK {currentHighlight.rankChange > 0 ? '+' : ''}{currentHighlight.rankChange}
              </div>
            )}
          </div>
        </div>

        {/* Scan line effect */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '2px',
          background: `linear-gradient(90deg, transparent, ${impactColor}, transparent)`,
          animation: 'highlight-scan 3s linear infinite',
          opacity: 0.6,
        }} />
      </div>

      {/* Step indicators */}
      <div style={{
        display: 'flex',
        gap: '8px',
        justifyContent: 'center',
      }}>
        {reelHighlights.map((step, index) => {
          const isActive = index === currentStep;
          const stepImpactColor = {
            high: 'var(--war-red)',
            medium: 'var(--war-yellow)',
            low: 'var(--war-cyan)',
          }[step.impact];

          return (
            <button
              key={step.id}
              onClick={() => handleStepSelect(index)}
              style={{
                flex: 1,
                height: '6px',
                background: isActive ? stepImpactColor : 'var(--war-gray-700)',
                border: 'none',
                borderRadius: '999px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                ...(isActive && {
                  boxShadow: `0 0 10px ${stepImpactColor}`,
                }),
              }}
              title={step.title}
            />
          );
        })}
      </div>

      <style>
        {`
          @keyframes highlight-scan {
            0% { transform: translateY(-100%); }
            100% { transform: translateY(400%); }
          }
        `}
      </style>
    </div>
  );
}

// Helper to generate mock highlights for demonstration
function generateMockHighlights(traceId: string): HighlightStep[] {
  return [
    {
      id: '1',
      title: 'TARGET ACQUIRED',
      description: 'Scout agent identified high-value influencer in target niche.',
      timestamp: '00:02:15',
      impact: 'high',
      rankChange: 2,
    },
    {
      id: '2',
      title: 'ENGAGEMENT SPIKE',
      description: 'Generated content achieved 240% above average engagement rate.',
      timestamp: '00:05:42',
      impact: 'medium',
      rankChange: 1,
    },
    {
      id: '3',
      title: 'COMPETITION OUTMANEUVERED',
      description: 'Successfully countered rival agent with superior positioning.',
      timestamp: '00:08:30',
      impact: 'high',
      rankChange: 3,
    },
    {
      id: '4',
      title: 'MISSION COMPLETE',
      description: 'All objectives achieved. New rank position secured.',
      timestamp: '00:12:10',
      impact: 'low',
      rankChange: 0,
    },
  ];
}