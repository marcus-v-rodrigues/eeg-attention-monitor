import { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from './useWebSocket';
import { useEEGData } from './useEEGData';
import { SessionState } from '../types/monitoring';

export const useAttentionMonitor = (wsUrl: string) => {
  const [isRecording, setIsRecording] = useState(false);
  const [sessionState, setSessionState] = useState<SessionState>('idle');
  const { data, isConnected, error } = useWebSocket(wsUrl);
  const { historicalData, metrics, currentData } = useEEGData(data);

  const startRecording = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/session/start', {
        method: 'POST'
      });
      if (response.ok) {
        setIsRecording(true);
        setSessionState('recording');
      }
    } catch (err) {
      console.error('Failed to start recording:', err);
    }
  }, []);

  const stopRecording = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/session/stop', {
        method: 'POST'
      });
      if (response.ok) {
        setIsRecording(false);
        setSessionState('idle');
      }
    } catch (err) {
      console.error('Failed to stop recording:', err);
    }
  }, []);

  return {
    isConnected,
    isRecording,
    sessionState,
    currentData,
    historicalData,
    metrics,
    error,
    actions: {
      startRecording,
      stopRecording
    }
  };
};