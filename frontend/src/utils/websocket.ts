import { EEGData } from '../types/eeg';

export type WebSocketMessage = {
  type: 'initial_state' | 'processed_data' | 'error' | 'quality_update' | 'session_state';
  data?: EEGData;
  error?: string;
  timestamp: number;
  quality?: {
    signalQuality: number;
    artifacts: boolean;
    connectivity: boolean;
  };
  sessionState?: {
    isRecording: boolean;
    duration: number;
    samplesCollected: number;
  };
};

export interface WebSocketOptions {
  reconnectAttempts?: number;
  reconnectDelay?: number;
  heartbeatInterval?: number;
  onReconnecting?: (attempt: number) => void;
  onMaxAttemptsReached?: () => void;
}

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private readonly maxReconnectAttempts: number;
  private readonly reconnectDelay: number;
  private readonly heartbeatInterval: number;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private isConnecting = false;

  constructor(
    private readonly url: string,
    private readonly onMessage: (data: WebSocketMessage) => void,
    private readonly onConnectionChange: (connected: boolean) => void,
    private readonly options: WebSocketOptions = {}
  ) {
    this.maxReconnectAttempts = options.reconnectAttempts || 5;
    this.reconnectDelay = options.reconnectDelay || 1000;
    this.heartbeatInterval = options.heartbeatInterval || 30000;
  }

  public async connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      return;
    }

    this.isConnecting = true;

    try {
      this.ws = new WebSocket(this.url);
      
      this.ws.onopen = () => {
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.onConnectionChange(true);
        this.startHeartbeat();
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.onMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        this.isConnecting = false;
        this.stopHeartbeat();
        this.onConnectionChange(false);
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnecting = false;
        if (this.ws?.readyState === WebSocket.OPEN) {
          this.ws.close();
        }
      };

    } catch (error) {
      this.isConnecting = false;
      console.error('Error creating WebSocket connection:', error);
      this.attemptReconnect();
    }
  }

  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      this.sendHeartbeat();
    }, this.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private sendHeartbeat(): void {
    this.send({ type: 'heartbeat', timestamp: Date.now() });
  }

  private async attemptReconnect(): Promise<void> {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }

    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      
      if (this.options.onReconnecting) {
        this.options.onReconnecting(this.reconnectAttempts);
      }

      const delay = this.reconnectDelay * Math.min(this.reconnectAttempts, 5);
      
      this.reconnectTimer = setTimeout(() => {
        this.connect();
      }, delay);
    } else {
      if (this.options.onMaxAttemptsReached) {
        this.options.onMaxAttemptsReached();
      }
      console.error('Max reconnection attempts reached');
    }
  }

  public send(data: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(data));
      } catch (error) {
        console.error('Error sending WebSocket message:', error);
      }
    } else {
      console.error('WebSocket is not connected');
    }
  }

  public disconnect(): void {
    this.stopHeartbeat();
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  public get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// Função fábrica para criar cliente WebSocket
export function createWebSocketClient(
  url: string,
  onMessage: (data: WebSocketMessage) => void,
  onConnectionChange: (connected: boolean) => void,
  options?: WebSocketOptions
): WebSocketClient {
  return new WebSocketClient(url, onMessage, onConnectionChange, options);
}

// Hook personalizado para usar WebSocket
import { useState, useEffect, useCallback } from 'react';

export function useWebSocket(url: string, options?: WebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [client, setClient] = useState<WebSocketClient | null>(null);

  useEffect(() => {
    const wsClient = createWebSocketClient(
      url,
      (message) => setLastMessage(message),
      (connected) => setIsConnected(connected),
      options
    );

    setClient(wsClient);
    wsClient.connect();

    return () => {
      wsClient.disconnect();
    };
  }, [url, options]);

  const sendMessage = useCallback((data: any) => {
    client?.send(data);
  }, [client]);

  return {
    isConnected,
    lastMessage,
    sendMessage
  };
}