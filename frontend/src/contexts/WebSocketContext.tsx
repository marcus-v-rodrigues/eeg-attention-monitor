"use client";

import React, { createContext, useContext, useEffect, useState } from 'react';
import { EEGData } from '../types/eeg';

interface WebSocketContextType {
  isConnected: boolean;
  lastMessage: EEGData | null;
  sendMessage: (data: any) => void;
}

const WebSocketContext = createContext<WebSocketContextType | null>(null);

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<EEGData | null>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    const connectWebSocket = () => {
      const socket = new WebSocket('ws://localhost:8000/api/v1/ws/stream');

      socket.onopen = () => {
        console.log('WebSocket conectado');
        setIsConnected(true);
      };

      socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          setLastMessage(message);
        } catch (error) {
          console.error('Erro ao processar mensagem:', error);
        }
      };

      socket.onclose = () => {
        console.log('WebSocket desconectado');
        setIsConnected(false);
        setTimeout(connectWebSocket, 3000);
      };

      socket.onerror = (error) => {
        console.error('Erro no WebSocket:', error);
      };

      setWs(socket);
    };

    connectWebSocket();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const sendMessage = (data: any) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data));
    }
  };

  return (
    <WebSocketContext.Provider value={{ isConnected, lastMessage, sendMessage }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocketContext = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocketContext must be used within a WebSocketProvider');
  }
  return context;
};