import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PulseButton } from '../components';
import { getNearbyOffers, claimOffer } from '../services/osApi';

/**
 * MissionFeed - Home screen showing only the closest active offer
 * Wireframe: Show only the closest active offer as a full-screen card.
 * Below it, two locked teasers.
 */
export default function MissionFeed() {
  const navigate = useNavigate();
  const [closestOffer, setClosestOffer] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isClaiming, setIsClaiming] = useState(false);
  const [userLocation, setUserLocation] = useState<{ lat: number; lon: number } | null>(null);

  // Get user location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            lat: position.coords.latitude,
            lon: position.coords.longitude,
          });
        },
        () => {
          // Fallback to default location (Tunis)
          setUserLocation({ lat: 36.8065, lon: 10.1815 });
        },
        { timeout: 5000 }
      );
    } else {
      // Fallback to default location
      setUserLocation({ lat: 36.8065, lon: 10.1815 });
    }
  }, []);

  // Load offers when location is available
  useEffect(() => {
    if (userLocation) {
      loadOffers();
    }
  }, [userLocation]);

  const loadOffers = async () => {
    setIsLoading(true);
    try {
      const offers = await getNearbyOffers(userLocation!.lat, userLocation!.lon);
      if (offers.length > 0) {
        setClosestOffer(offers[0]);
      }
    } catch (error) {
      console.error('Failed to load offers:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClaim = async () => {
    if (!closestOffer) return;

    setIsClaiming(true);
    try {
      const response = await claimOffer(closestOffer.id);
      navigate(`/mission/${closestOffer.id}`);
    } catch (error) {
      console.error('Failed to claim offer:', error);
      alert('Failed to claim offer. Please try again.');
    } finally {
      setIsClaiming(false);
    }
  };

  // Format expiry time
  const formatExpiry = (expiry: string) => {
    const expiryDate = new Date(expiry);
    const now = new Date();
    const diffMs = expiryDate.getTime() - now.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

    if (diffHours > 0) {
      return `Expires in ${diffHours}h ${diffMinutes}m`;
    } else {
      return `Expires in ${diffMinutes}m`;
    }
  };

  if (isLoading) {
    return (
      <div style={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--war-black)',
        color: 'white',
        padding: '24px',
      }}>
        <div style={{ fontSize: '32px', marginBottom: '16px' }}>📍</div>
        <div style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '14px',
          color: 'var(--war-cyan)',
        }}>
          Finding nearby missions...
        </div>
      </div>
    );
  }

  if (!closestOffer) {
    return (
      <div style={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--war-black)',
        color: 'white',
        padding: '24px',
        textAlign: 'center',
      }}>
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>🎯</div>
        <h2 style={{
          fontFamily: 'var(--font-display)',
          fontSize: '24px',
          fontWeight: '800',
          marginBottom: '12px',
        }}>
          No Missions Available
        </h2>
        <p style={{
          fontFamily: 'var(--font-body)',
          fontSize: '14px',
          color: 'var(--si-muted)',
          marginBottom: '32px',
        }}>
          Check back later for new missions in your area.
        </p>
        <button
          onClick={loadOffers}
          style={{
            padding: '12px 24px',
            background: 'var(--gradient-cyber)',
            border: 'none',
            borderRadius: '12px',
            color: 'white',
            fontFamily: 'var(--font-display)',
            fontSize: '14px',
            fontWeight: '800',
            cursor: 'pointer',
          }}
        >
          REFRESH
        </button>
      </div>
    );
  }

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      padding: '24px',
      background: 'var(--war-black)',
      color: 'white',
    }}>
      {/* Header */}
      <div>
        <div style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '14px',
          color: 'var(--war-cyan)',
          marginBottom: '8px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}>
          ⚡ ACTIVE MISSION
        </div>

        <h1 style={{
          fontFamily: 'var(--font-display)',
          fontSize: '48px',
          fontWeight: '900',
          marginBottom: '16px',
          lineHeight: 1.1,
        }}>
          {closestOffer.location}
        </h1>

        {/* Reward */}
        <div style={{
          fontFamily: 'var(--font-numbers)',
          fontSize: '32px',
          color: 'var(--war-green)',
          marginBottom: '8px',
        }}>
          +{closestOffer.reward} TND
        </div>

        {/* Details */}
        <div style={{
          fontFamily: 'var(--font-body)',
          fontSize: '16px',
          color: 'var(--si-muted)',
          marginBottom: '8px',
        }}>
          {closestOffer.distance.toFixed(1)} km away · {formatExpiry(closestOffer.expiry)}
        </div>

        {/* High demand badge */}
        {closestOffer.highDemand && (
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '6px 12px',
            background: 'var(--war-red)20',
            border: '1px solid var(--war-red)',
            borderRadius: '999px',
            fontFamily: 'var(--font-mono)',
            fontSize: '12px',
            fontWeight: '700',
            color: 'var(--war-red)',
            marginTop: '8px',
            animation: 'pulse 2s ease-in-out infinite',
          }}>
            <span>🔥</span>
            <span>HIGH DEMAND ({closestOffer.claimCount} users)</span>
          </div>
        )}
      </div>

      {/* Locked teasers and claim button */}
      <div style={{ position: 'relative' }}>
        {/* Locked teasers */}
        <div style={{
          position: 'absolute',
          bottom: '100%',
          left: 0,
          right: 0,
          marginBottom: '24px',
          padding: '16px',
          background: 'rgba(0, 0, 0, 0.7)',
          backdropFilter: 'blur(10px)',
          borderRadius: '12px',
          border: '1px solid var(--war-gray-700)',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
          opacity: 0.8,
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontFamily: 'var(--font-mono)',
            fontSize: '13px',
            color: 'var(--si-muted)',
          }}>
            <span>🔒</span>
            <span>2 MORE NEARBY MISSIONS (Unlock after first action)</span>
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontFamily: 'var(--font-mono)',
            fontSize: '13px',
            color: 'var(--si-muted)',
          }}>
            <span>🔒</span>
            <span>HOT DROP – reward increasing...</span>
          </div>
        </div>

        {/* Claim button */}
        <PulseButton
          onClick={handleClaim}
          disabled={isClaiming}
          pulse={!isClaiming}
          size="large"
          variant="primary"
        >
          {isClaiming ? 'CLAIMING...' : '⚡ CLAIM & START'}
        </PulseButton>
      </div>

      <style>
        {`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
          }
        `}
      </style>
    </div>
  );
}