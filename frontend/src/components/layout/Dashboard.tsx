import React, { useState } from 'react';
import { useMonitoringContext } from '../../contexts/MonitoringContext';
import { useWebSocketContext } from '../../contexts/WebSocketContext';
import { Button } from '@/components/ui/button';
import { Brain, Menu, X } from 'lucide-react';

interface DashboardProps {
  children: React.ReactNode;
}

export const Dashboard: React.FC<DashboardProps> = ({ children }) => {
  const { isConnected } = useWebSocketContext();
  const { state } = useMonitoringContext();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white border-b">
        <div className="flex h-16 items-center px-4 md:px-6">
        
          {/* Logo */}
          <div className="flex items-center gap-2 pr-6 h-16 border-b">
            <Brain className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-xl font-bold">EEG Monitor</h1>
              <p className="text-xs text-gray-500">Real-time Analysis</p>
            </div>
          </div>

          <div className="flex items-center gap-2 ml-4">
            {/* Indicador de Status */}
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-green-500' : 'bg-red-500'
              }`} />
              <span className="text-sm text-gray-500">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>

            {/* Status da Sessão */}
            {state.isRecording && (
              <div className="flex items-center gap-2 ml-4">
                <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                <span className="text-sm text-gray-500">Recording</span>
              </div>
            )}
          </div>

          {/* Qualidade do Sinal */}
          <div className="ml-auto flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">Signal Quality:</span>
              <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-green-500 transition-all duration-500"
                  style={{ width: `${state.signalQuality * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className={`flex-1 transition-all duration-300`}>
        <div className="container mx-auto px-4 py-6">
          {children}
        </div>
      </main>
    </div>
  );
};