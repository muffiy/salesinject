import { useState } from 'react';
import { PulseButton } from './PulseButton';

interface PermissionGateProps {
  onGrant: () => void;
}

/**
 * Request location, camera, and notifications permissions
 */
export default function PermissionGate({ onGrant }: PermissionGateProps) {
  const [isRequesting, setIsRequesting] = useState(false);

  const requestAll = async () => {
    setIsRequesting(true);

    try {
      // Request location permission
      if (navigator.geolocation) {
        await new Promise((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(
            () => resolve(true),
            () => resolve(false), // Continue even if location is denied
            { timeout: 5000 }
          );
        });
      }

      // Request camera permission
      if (navigator.mediaDevices?.getUserMedia) {
        try {
          await navigator.mediaDevices.getUserMedia({ video: true });
        } catch {
          // Continue even if camera is denied
          console.log('Camera permission denied or not available');
        }
      }

      // Request notifications permission
      if ('Notification' in window && Notification.permission === 'default') {
        await Notification.requestPermission();
      }

      // All permissions requested (even if some were denied)
      onGrant();
    } catch (error) {
      console.error('Permission request error:', error);
      // Still continue to app even if permission requests fail
      onGrant();
    } finally {
      setIsRequesting(false);
    }
  };

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
      transition: 'var(--transition-medium)'
    }}>
      <h2 style={{
        fontSize: '28px',
        fontWeight: '800',
        marginBottom: '32px',
        fontFamily: 'var(--font-display)',
        textAlign: 'center',
        transition: 'var(--transition-medium)'
      }}>
        We need access to:
      </h2>

      <ul style={{
        listStyle: 'none',
        padding: 0,
        margin: 0,
        width: '100%',
        maxWidth: '400px',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
        transition: 'var(--transition-medium)'
      }}>
        <li style={{
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          padding: '16px',
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '12px',
          border: '1px solid var(--war-gray-700)',
          transition: 'var(--transition-medium)'
        }}>
          <div style={{
            fontSize: '24px',
            width: '40px',
            height: '40px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'var(--war-cyan)20',
            borderRadius: '8px',
            transition: 'var(--transition-medium)'
          }}>
            📍
          </div>
          <div>
            <div style={{
              fontFamily: 'var(--font-display)',
              fontSize: '16px',
              fontWeight: '700',
              marginBottom: '4px',
              transition: 'var(--transition-medium)'
            }}>
              Location
            </div>
            <div style={{
              fontFamily: 'var(--font-body)',
              fontSize: '14px',
              color: 'var(--si-muted)',
              transition: 'var(--transition-medium)'
            }}>
              Find nearby missions
            </div>
          </div>
        </li>

        <li style={{
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          padding: '16px',
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '12px',
          border: '1px solid var(--war-gray-700)',
          transition: 'var(--transition-medium)'
        }}>
          <div style={{
            fontSize: '24px',
            width: '40px',
            height: '40px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'var(--war-purple)20',
            borderRadius: '8px',
            transition: 'var(--transition-medium)'
          }}>
            📷
          </div>
          <div>
            <div style={{
              fontFamily: 'var(--font-display)',
              fontSize: '16px',
              fontWeight: '700',
              marginBottom: '4px',
              transition: 'var(--transition-medium)'
            }}>
              Camera
            </div>
            <div style={{
              fontFamily: 'var(--font-body)',
              fontSize: '14px',
              color: 'var(--si-muted)',
              transition: 'var(--transition-medium)'
            }}>
              Capture content
            </div>
          </div>
        </li>

        <li style={{
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          padding: '16px',
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '12px',
          border: '1px solid var(--war-gray-700)',
          transition: 'var(--transition-medium)'
        }}>
          <div style={{
            fontSize: '24px',
            width: '40px',
            height: '40px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'var(--war-green)20',
            borderRadius: '8px',
            transition: 'var(--transition-medium)'
          }}>
            🔔
          </div>
          <div>
            <div style={{
              fontFamily: 'var(--font-display)',
              fontSize: '16px',
              fontWeight: '700',
              marginBottom: '4px',
              transition: 'var(--transition-medium)'
            }}>
              Notifications
            </div>
            <div style={{
              fontFamily: 'var(--font-body)',
              fontSize: '14px',
              color: 'var(--si-muted)',
              transition: 'var(--transition-medium)'
            }}>
              Mission alerts
            </div>
          </div>
        </li>
      </ul>

      <div style={{ marginTop: '48px', width: '100%', maxWidth: '400px' }}>
        <PulseButton
          onClick={requestAll}
          disabled={isRequesting}
          size="large"
          variant="primary"
          style={{
            transition: 'var(--transition-medium)',
            position: 'relative',
            overflow: 'hidden'
          }}
        >
          {isRequesting ? 'REQUESTING...' : 'ALLOW ALL'}
        </PulseButton>
      </div>

      <p style={{
        marginTop: '24px',
        fontFamily: 'var(--font-mono)',
        fontSize: '12px',
        color: 'var(--si-muted)',
        textAlign: 'center',
        maxWidth: '400px',
        transition: 'var(--transition-medium)'
      }}>
        Permissions are required for the full experience. You can modify them later in your device settings.
      </p>
    </div>
  );
}