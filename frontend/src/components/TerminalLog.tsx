import React, { useState, useEffect, useRef } from 'react';

interface TerminalLogProps {
  /** Log entries to display */
  logs: Array<{
    id: string;
    timestamp: string;
    message: string;
    type: 'info' | 'success' | 'warning' | 'error' | 'system';
  }>;
  /** Maximum number of visible logs */
  maxLogs?: number;
  /** Whether to auto-scroll to bottom */
  autoScroll?: boolean;
  /** Whether to show timestamps */
  showTimestamps?: boolean;
  /** Custom CSS class */
  className?: string;
}

/**
 * Terminal-style log display
 * Used in WarRoom to stream mission events
 */
export function TerminalLog({
  logs,
  maxLogs = 50,
  autoScroll = true,
  showTimestamps = true,
  className,
}: TerminalLogProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [filter, setFilter] = useState<string>('all');

  // Filter logs based on type
  const filteredLogs = logs.filter(log =>
    filter === 'all' || log.type === filter
  ).slice(-maxLogs);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [filteredLogs, autoScroll]);

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'success': return 'var(--war-green)';
      case 'warning': return 'var(--war-yellow)';
      case 'error': return 'var(--war-red)';
      case 'system': return 'var(--war-cyan)';
      default: return 'var(--si-text)';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'success': return '✅';
      case 'warning': return '⚠️';
      case 'error': return '❌';
      case 'system': return '⚡';
      default: return 'ℹ️';
    }
  };

  return (
    <div
      className={className}
      style={{
        background: 'rgba(10, 10, 10, 0.95)',
        border: '3px solid var(--war-gray-700)',
        borderRadius: '12px',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
      }}
    >
      {/* Header with filter controls */}
      <div style={{
        padding: '12px 16px',
        background: 'var(--war-gray-900)',
        borderBottom: '1px solid var(--war-gray-700)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <div style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '14px',
          fontWeight: '700',
          color: 'var(--war-cyan)',
          textTransform: 'uppercase',
        }}>
          MISSION TERMINAL
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          {['all', 'info', 'success', 'warning', 'error', 'system'].map((type) => (
            <button
              key={type}
              onClick={() => setFilter(type)}
              style={{
                padding: '4px 8px',
                background: filter === type ? getTypeColor(type) : 'transparent',
                border: `1px solid ${getTypeColor(type)}`,
                borderRadius: '4px',
                fontFamily: 'var(--font-mono)',
                fontSize: '10px',
                fontWeight: '700',
                color: filter === type ? 'black' : getTypeColor(type),
                cursor: 'pointer',
                textTransform: 'uppercase',
                transition: 'all 0.2s ease',
              }}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Log container */}
      <div
        ref={containerRef}
        style={{
          flex: 1,
          padding: '16px',
          overflowY: 'auto',
          fontFamily: 'var(--font-mono)',
          fontSize: '12px',
          lineHeight: '1.5',
          background: 'rgba(0, 0, 0, 0.3)',
        }}
      >
        {filteredLogs.length === 0 ? (
          <div style={{
            padding: '40px',
            textAlign: 'center',
            color: 'var(--si-muted)',
            fontFamily: 'var(--font-mono)',
            fontSize: '13px',
          }}>
            No logs to display
          </div>
        ) : (
          filteredLogs.map((log) => (
            <div
              key={log.id}
              style={{
                marginBottom: '8px',
                padding: '8px 12px',
                background: 'rgba(0, 0, 0, 0.5)',
                borderLeft: `3px solid ${getTypeColor(log.type)}`,
                borderRadius: '4px',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px',
              }}
            >
              {/* Timestamp */}
              {showTimestamps && (
                <div style={{
                  minWidth: '70px',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '10px',
                  color: 'var(--si-muted)',
                  marginTop: '1px',
                }}>
                  {log.timestamp}
                </div>
              )}

              {/* Icon */}
              <div style={{
                fontSize: '12px',
                marginTop: '1px',
              }}>
                {getTypeIcon(log.type)}
              </div>

              {/* Message */}
              <div style={{
                flex: 1,
                color: getTypeColor(log.type),
                wordBreak: 'break-word',
              }}>
                {log.message}
              </div>
            </div>
          ))
        )}

        {/* Scan line effect */}
        <div style={{
          position: 'sticky',
          bottom: 0,
          left: 0,
          right: 0,
          height: '2px',
          background: 'linear-gradient(90deg, transparent, var(--war-cyan), transparent)',
          animation: 'terminal-scan 3s linear infinite',
          opacity: 0.3,
          marginTop: '8px',
        }} />
      </div>

      {/* Footer with stats */}
      <div style={{
        padding: '8px 16px',
        background: 'var(--war-gray-900)',
        borderTop: '1px solid var(--war-gray-700)',
        display: 'flex',
        justifyContent: 'space-between',
        fontFamily: 'var(--font-mono)',
        fontSize: '11px',
        color: 'var(--si-muted)',
      }}>
        <div>
          Logs: {filteredLogs.length}/{logs.length}
        </div>
        <div>
          Filter: {filter.toUpperCase()}
        </div>
        <div>
          Auto-scroll: {autoScroll ? 'ON' : 'OFF'}
        </div>
      </div>

      <style>
        {`
          @keyframes terminal-scan {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
          }

          /* Custom scrollbar */
          ::-webkit-scrollbar {
            width: 8px;
          }
          ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.05);
          }
          ::-webkit-scrollbar-thumb {
            background: var(--war-cyan);
            border-radius: 4px;
          }
          ::-webkit-scrollbar-thumb:hover {
            background: var(--war-purple);
          }
        `}
      </style>
    </div>
  );
}