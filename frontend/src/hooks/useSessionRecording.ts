import { useState, useCallback } from 'react';
import { saveSession, loadSession } from '../utils/session-storage';
import { SessionInfo } from '../types/monitoring';

export function useSessionRecording() {
  const [isRecording, setIsRecording] = useState(false);
  const [sessionData, setSessionData] = useState<EEGData[]>([]);
  const [currentSession, setCurrentSession] = useState<SessionInfo | null>(null);

  const startRecording = useCallback(() => {
    setIsRecording(true);
    setSessionData([]);
    setCurrentSession({
      id: Date.now().toString(),
      startTime: Date.now(),
      duration: 0,
      samplesCollected: 0,
      averageAttention: 0,
      signalQuality: 1
    });
  }, []);

  const stopRecording = useCallback(async () => {
    if (!currentSession) return;

    setIsRecording(false);
    try {
      await saveSession({
        ...currentSession,
        data: sessionData,
        endTime: Date.now()
      });
    } catch (error) {
      console.error('Error saving session:', error);
    }
  }, [currentSession, sessionData]);

  const addDataPoint = useCallback((data: EEGData) => {
    if (!isRecording) return;

    setSessionData(prev => [...prev, data]);
    setCurrentSession(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        duration: (Date.now() - prev.startTime) / 1000,
        samplesCollected: sessionData.length + 1,
        averageAttention: calculateAverageAttention([...sessionData, data])
      };
    });
  }, [isRecording, sessionData]);

  return {
    isRecording,
    sessionData,
    currentSession,
    startRecording,
    stopRecording,
    addDataPoint
  };
}