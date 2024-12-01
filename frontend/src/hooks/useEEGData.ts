import { useState, useEffect } from 'react';
import { EEGData } from '../types/eeg';

interface UseEEGDataOptions {
  maxHistoryLength?: number;
  historyDuration?: number; // in seconds
}

export const useEEGData = (
  currentData: EEGData | null,
  options: UseEEGDataOptions = {}
) => {
  const {
    maxHistoryLength = 500,
    historyDuration = 30
  } = options;

  const [historicalData, setHistoricalData] = useState<EEGData[]>([]);
  const [metrics, setMetrics] = useState({
    averageAttention: 0,
    averageEngagement: 0,
    dominantBandPower: '',
  });

  useEffect(() => {
    if (currentData) {
      // Update historical data
      setHistoricalData(prev => {
        const now = Date.now() / 1000;
        const filtered = prev.filter(d => 
          now - d.timestamp < historyDuration
        );
        return [...filtered, currentData].slice(-maxHistoryLength);
      });

      // Update metrics
      if (historicalData.length > 0) {
        const avgAttention = historicalData.reduce(
          (sum, d) => sum + d.attention_metrics.attention_score, 0
        ) / historicalData.length;

        const avgEngagement = historicalData.reduce(
          (sum, d) => sum + d.attention_metrics.engagement_index, 0
        ) / historicalData.length;

        // Find dominant band power
        const bandPowers = currentData.band_powers;
        const dominantBand = Object.entries(bandPowers).reduce(
          (max, [band, power]) => power > max.power ? { band, power } : max,
          { band: '', power: -Infinity }
        ).band;

        setMetrics({
          averageAttention: avgAttention,
          averageEngagement: avgEngagement,
          dominantBandPower: dominantBand
        });
      }
    }
  }, [currentData, historyDuration, maxHistoryLength]);

  return {
    historicalData,
    metrics,
    currentData
  };
};