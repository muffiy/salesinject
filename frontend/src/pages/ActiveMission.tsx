import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PulseButton, TerminalLog } from '../components';
import { getOfferDetails, uploadVideo } from '../services/osApi';
import { connectMissionStream } from '../services/osApi';

/**
 * ActiveMission - Mission execution screen
 * Wireframe: Show status ladder, geofence indicator, video upload
 */
export default function ActiveMission() {
  const { offerId } = useParams<{ offerId: string }>();
  const navigate = useNavigate();
  const [offer, setOffer] = useState<any>(null);
  const [status, setStatus] = useState<string>('accepted');
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoPreview, setVideoPreview] = useState<string | null>(null);
  const [isGeofenced, setIsGeofenced] = useState<boolean>(false);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [logs, setLogs] = useState<any[]>([]);

  const statusSteps = [
    { key: 'accepted', label: 'Accepted', description: 'Mission claimed' },
    { key: 'traveling', label: 'Traveling', description: 'Heading to location' },
    { key: 'arrived', label: 'Arrived', description: 'At destination' },
    { key: 'creating', label: 'Creating', description: 'Recording content' },
    { key: 'submitted', label: 'Submitted', description: 'Content uploaded' },
    { key: 'processing', label: 'Processing', description: 'Reward verification' },
  ];

  const currentStepIndex = statusSteps.findIndex(step => step.key === status);

  // Load offer details
  useEffect(() => {
    if (offerId) {
      loadOfferDetails();
    }
  }, [offerId]);

  // Simulate WebSocket connection for mission updates
  useEffect(() => {
    if (!offerId) return;

    // In real app, use: connectMissionStream(offerId, handleMissionEvent)
    const simulateMissionProgress = () => {
      const steps = ['accepted', 'traveling', 'arrived', 'creating', 'submitted', 'processing'];
      let currentStep = 0;

      const interval = setInterval(() => {
        if (currentStep < steps.length - 1) {
          currentStep++;
          setStatus(steps[currentStep]);
          addLog(`Status updated: ${steps[currentStep]}`, 'system');
        } else {
          clearInterval(interval);
          // Auto-navigate after completion
          setTimeout(() => {
            navigate('/');
          }, 3000);
        }
      }, 3000); // Change status every 3 seconds for demo

      return () => clearInterval(interval);
    };

    const timer = setTimeout(simulateMissionProgress, 1000);
    return () => clearTimeout(timer);
  }, [offerId, navigate]);

  const loadOfferDetails = async () => {
    try {
      const offerData = await getOfferDetails(offerId!);
      setOffer(offerData);
      addLog(`Loaded mission: ${offerData.location}`, 'info');
    } catch (error) {
      console.error('Failed to load offer details:', error);
      addLog('Failed to load mission details', 'error');
    }
  };

  const addLog = (message: string, type: 'info' | 'success' | 'warning' | 'error' | 'system') => {
    const newLog = {
      id: Date.now().toString(),
      timestamp: new Date().toLocaleTimeString(),
      message,
      type,
    };
    setLogs(prev => [...prev, newLog].slice(-20)); // Keep last 20 logs
  };

  const handleVideoSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setVideoFile(file);
      addLog(`Video selected: ${file.name}`, 'info');

      // Create preview URL
      const previewUrl = URL.createObjectURL(file);
      setVideoPreview(previewUrl);
    }
  };

  const handleUpload = async () => {
    if (!videoFile || !offerId) return;

    setIsUploading(true);
    addLog('Uploading video...', 'info');

    try {
      await uploadVideo(offerId, videoFile);
      addLog('Video uploaded successfully!', 'success');
      setStatus('submitted');
    } catch (error) {
      console.error('Upload failed:', error);
      addLog('Upload failed. Please try again.', 'error');
    } finally {
      setIsUploading(false);
    }
  };

  const handleNavigate = () => {
    if (offer?.lat && offer?.lon) {
      window.open(`https://maps.google.com/?q=${offer.lat},${offer.lon}`, '_blank');
      addLog('Opened navigation to destination', 'info');
    }
  };

  const simulateArrival = () => {
    setIsGeofenced(true);
    addLog('Arrived at destination', 'success');
    if (status === 'traveling') {
      setStatus('arrived');
    }
  };

  if (!offer) {
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
          Loading mission...
        </div>
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
      overflow: 'hidden',
    }}>
      {/* Header */}
      <div>
        <h2 style={{
          fontFamily: 'var(--font-display)',
          fontSize: '32px',
          fontWeight: '800',
          marginBottom: '8px',
        }}>
          {offer.location}
        </h2>
        <div style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '14px',
          color: 'var(--si-muted)',
        }}>
          {offer.address || 'No address provided'}
        </div>
      </div>

      {/* Status progress */}
      <div style={{ marginTop: '24px' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          fontFamily: 'var(--font-mono)',
          fontSize: '12px',
          color: 'var(--si-muted)',
          marginBottom: '8px',
        }}>
          <span>STATUS</span>
          <span style={{
            textTransform: 'uppercase',
            color: 'var(--war-cyan)',
            fontWeight: '700',
          }}>
            {statusSteps.find(s => s.key === status)?.label}
          </span>
        </div>

        {/* Progress bar */}
        <div style={{
          height: '6px',
          background: 'var(--war-gray-800)',
          borderRadius: '999px',
          overflow: 'hidden',
          marginBottom: '16px',
        }}>
          <div style={{
            height: '100%',
            background: 'var(--war-cyan)',
            borderRadius: '999px',
            width: `${((currentStepIndex + 1) / statusSteps.length) * 100}%`,
            transition: 'width 0.5s ease',
          }} />
        </div>

        {/* Status steps */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: `repeat(${statusSteps.length}, 1fr)`,
          gap: '8px',
          marginBottom: '24px',
        }}>
          {statusSteps.map((step, index) => (
            <div
              key={step.key}
              style={{
                textAlign: 'center',
                padding: '8px 4px',
              }}
            >
              <div style={{
                width: '24px',
                height: '24px',
                margin: '0 auto 4px',
                borderRadius: '50%',
                background: index <= currentStepIndex ? 'var(--war-cyan)' : 'var(--war-gray-700)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '12px',
                fontWeight: '700',
                color: index <= currentStepIndex ? 'black' : 'var(--si-muted)',
              }}>
                {index + 1}
              </div>
              <div style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '10px',
                color: index <= currentStepIndex ? 'var(--war-cyan)' : 'var(--si-muted)',
                fontWeight: index <= currentStepIndex ? '700' : '500',
              }}>
                {step.label}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action buttons */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '24px' }}>
        <PulseButton
          onClick={handleNavigate}
          variant="secondary"
          size="medium"
        >
          🧭 Navigate to Location
        </PulseButton>

        {!isGeofenced && (
          <button
            onClick={simulateArrival}
            style={{
              padding: '12px',
              background: 'transparent',
              border: '1px solid var(--war-yellow)',
              borderRadius: '12px',
              color: 'var(--war-yellow)',
              fontFamily: 'var(--font-mono)',
              fontSize: '13px',
              fontWeight: '700',
              cursor: 'pointer',
              textAlign: 'center',
            }}
          >
            Simulate Arrival (Dev)
          </button>
        )}
      </div>

      {/* Geofence status */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        padding: '12px',
        background: isGeofenced ? 'var(--war-green)20' : 'var(--war-red)20',
        border: `1px solid ${isGeofenced ? 'var(--war-green)' : 'var(--war-red)'}`,
        borderRadius: '12px',
        marginBottom: '24px',
      }}>
        <div style={{
          width: '16px',
          height: '16px',
          borderRadius: '50%',
          background: isGeofenced ? 'var(--war-green)' : 'var(--war-red)',
          animation: isGeofenced ? 'pulse 2s infinite' : 'none',
        }} />
        <div style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '13px',
          fontWeight: '700',
          color: isGeofenced ? 'var(--war-green)' : 'var(--war-red)',
        }}>
          {isGeofenced ? '✓ You are at the location' : '✗ Not yet arrived at location'}
        </div>
      </div>

      {/* Video upload section (only when arrived) */}
      {isGeofenced && status === 'arrived' && (
        <div style={{ marginBottom: '24px' }}>
          <div style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '14px',
            fontWeight: '700',
            color: 'var(--war-cyan)',
            marginBottom: '12px',
          }}>
            📹 UPLOAD VIDEO
          </div>

          {videoPreview ? (
            <div style={{ marginBottom: '12px' }}>
              <video
                src={videoPreview}
                controls
                style={{
                  width: '100%',
                  maxHeight: '200px',
                  borderRadius: '12px',
                  background: 'black',
                }}
              />
            </div>
          ) : (
            <div style={{
              padding: '32px',
              background: 'rgba(0, 0, 0, 0.3)',
              border: '2px dashed var(--war-gray-700)',
              borderRadius: '12px',
              textAlign: 'center',
              marginBottom: '12px',
            }}>
              <div style={{ fontSize: '32px', marginBottom: '12px' }}>📁</div>
              <div style={{
                fontFamily: 'var(--font-body)',
                fontSize: '14px',
                color: 'var(--si-muted)',
                marginBottom: '16px',
              }}>
                Select a video file to upload
              </div>
            </div>
          )}

          <div style={{ display: 'flex', gap: '12px' }}>
            <label style={{
              flex: 1,
              padding: '12px',
              background: 'var(--war-gray-800)',
              border: '1px solid var(--war-gray-700)',
              borderRadius: '12px',
              color: 'white',
              fontFamily: 'var(--font-mono)',
              fontSize: '13px',
              textAlign: 'center',
              cursor: 'pointer',
            }}>
              <input
                type="file"
                accept="video/*"
                onChange={handleVideoSelect}
                style={{ display: 'none' }}
              />
              {videoFile ? 'CHANGE VIDEO' : 'SELECT VIDEO'}
            </label>

            <PulseButton
              onClick={handleUpload}
              disabled={!videoFile || isUploading}
              variant="primary"
              size="medium"
              style={{ flex: 1 }}
            >
              {isUploading ? 'UPLOADING...' : '📤 UPLOAD & EARN'}
            </PulseButton>
          </div>
        </div>
      )}

      {/* Terminal log */}
      <div style={{ flex: 1, minHeight: '200px', marginBottom: '24px' }}>
        <TerminalLog
          logs={logs}
          maxLogs={10}
          autoScroll={true}
          showTimestamps={true}
        />
      </div>

      {/* Reward preview */}
      <div style={{
        padding: '16px',
        background: 'var(--war-green)10',
        border: '1px solid var(--war-green)',
        borderRadius: '12px',
        textAlign: 'center',
      }}>
        <div style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '12px',
          color: 'var(--si-muted)',
          marginBottom: '4px',
        }}>
          REWARD LOCKED
        </div>
        <div style={{
          fontFamily: 'var(--font-numbers)',
          fontSize: '32px',
          fontWeight: '900',
          color: 'var(--war-green)',
        }}>
          +{offer.reward} TND
        </div>
      </div>

      <style>
        {`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
        `}
      </style>
    </div>
  );
}