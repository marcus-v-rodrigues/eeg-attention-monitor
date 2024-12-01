"use client";

import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { useWebSocketContext } from './WebSocketContext';
import { EEGData } from '../types/eeg';
import { MONITORING_CONFIG } from '../config/monitoring';

interface MonitoringState {
  currentData: EEGData | null;
  historicalData: EEGData[];
  isRecording: boolean;
  sessionDuration: number;
  signalQuality: number;
  attentionMetrics: {
    average: number;
    trend: 'increasing' | 'stable' | 'decreasing';
  };
  config: {
    channels: string[];
    sampleRate: number;
    bufferSize: number;
    bandRanges: {
      [key: string]: [number, number];
    };
  };
}

type MonitoringAction =
  | { type: 'SET_CURRENT_DATA'; payload: EEGData }
  | { type: 'START_RECORDING' }
  | { type: 'STOP_RECORDING' }
  | { type: 'UPDATE_QUALITY'; payload: number }
  | { type: 'CLEAR_DATA' };

const initialState: MonitoringState = {
  currentData: null,
  historicalData: [],
  isRecording: false,
  sessionDuration: 0,
  signalQuality: 1,
  attentionMetrics: {
    average: 0,
    trend: 'stable'
  },
  config: {
    channels: MONITORING_CONFIG.channels,
    sampleRate: MONITORING_CONFIG.refreshRate,
    bufferSize: MONITORING_CONFIG.bufferSize,
    bandRanges: MONITORING_CONFIG.bandRanges
  }
};

function reducer(state: MonitoringState, action: MonitoringAction): MonitoringState {
  switch (action.type) {
    case 'SET_CURRENT_DATA':
      const newHistoricalData = [...state.historicalData, action.payload].slice(-500);
      const average = calculateAverageAttention(newHistoricalData);
      const trend = calculateAttentionTrend(newHistoricalData);
      
      return {
        ...state,
        currentData: action.payload,
        historicalData: newHistoricalData,
        attentionMetrics: { average, trend }
      };
    
    case 'START_RECORDING':
      return {
        ...state,
        isRecording: true,
        sessionDuration: 0
      };
    
    case 'STOP_RECORDING':
      return {
        ...state,
        isRecording: false
      };
    
    case 'UPDATE_QUALITY':
      return {
        ...state,
        signalQuality: action.payload
      };
    
    case 'CLEAR_DATA':
      return {
        ...initialState,
        config: state.config
      };
    
    default:
      return state;
  }
}

// Utility functions
function calculateAverageAttention(data: EEGData[]): number {
  if (data.length === 0) return 0;
  return data.reduce((sum, d) => sum + d.attention_metrics.attention_score, 0) / data.length;
}

function calculateAttentionTrend(data: EEGData[]): 'increasing' | 'stable' | 'decreasing' {
  if (data.length < 10) return 'stable';
  
  const recent = data.slice(-10);
  const firstHalf = recent.slice(0, 5);
  const secondHalf = recent.slice(-5);
  
  const firstAvg = calculateAverageAttention(firstHalf);
  const secondAvg = calculateAverageAttention(secondHalf);
  
  const difference = secondAvg - firstAvg;
  
  if (difference > 0.05) return 'increasing';
  if (difference < -0.05) return 'decreasing';
  return 'stable';
}

const MonitoringContext = createContext<{
  state: MonitoringState;
  dispatch: React.Dispatch<MonitoringAction>;
} | null>(null);

export const MonitoringProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState);
  const { lastMessage } = useWebSocketContext();

  useEffect(() => {
    if (lastMessage) {
      dispatch({ 
        type: 'SET_CURRENT_DATA', 
        payload: lastMessage 
      });
    }
  }, [lastMessage]);

  return (
    <MonitoringContext.Provider value={{ state, dispatch }}>
      {children}
    </MonitoringContext.Provider>
  );
};

export const useMonitoringContext = () => {
  const context = useContext(MonitoringContext);
  if (!context) {
    throw new Error('useMonitoringContext must be used within a MonitoringProvider');
  }
  return context;
};