import { useState, useEffect, useCallback } from 'react';
import { EEGData } from '../types/eeg';

interface WebSocketMessage {
  type: string;
  data: EEGData;
  timestamp: number;
}

export const useWebSocket = (url: string) => {
  const [data, setData] = useState<EEGData | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const connect = useCallback(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        if (message.type === 'processed_data') {
          setData(message.data);
        }
      } catch (err) {
        setError('Error processing message');
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      // Attempt to reconnect after 3 seconds
      setTimeout(connect, 3000);
    };

    ws.onerror = (err) => {
      setError('WebSocket error');
      console.error('WebSocket error:', err);
    };

    return ws;
  }, [url]);

  useEffect(() => {
    const ws = connect();
    return () => {
      ws.close();
    };
  }, [connect]);

  return { data, isConnected, error };
};