import { useState, useCallback, useEffect } from 'react';
import { EEGData, ProcessedData } from '../types/eeg';
import { MONITORING_CONFIG } from '../config/monitoring';

export function useEEGProcessing() {
  const [buffer, setBuffer] = useState<EEGData[]>([]);
  const [processedData, setProcessedData] = useState<ProcessedData | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const processData = useCallback((data: EEGData) => {
    setBuffer(prev => [...prev.slice(-MONITORING_CONFIG.bufferSize), data]);
    
    // Processa dados em tempo real
    setProcessedData({
      data,
      status: 'success'
    });
  }, []);

  useEffect(() => {
    return () => {
      setBuffer([]);
      setProcessedData(null);
    };
  }, []);

  return {
    buffer,
    processedData,
    isProcessing,
    processData
  };
}